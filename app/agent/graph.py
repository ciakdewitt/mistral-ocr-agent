"""
Main LangGraph definition for the OCR agent.
"""
import os
from typing import Annotated, TypedDict, Dict, List, Any, Optional, Tuple
import logging

from langgraph.graph import StateGraph, MessagesState
from langgraph.graph.message import AnyMessage
from langgraph.prebuilt import ToolMessage, AssistantMessage, UserMessage
from anthropic import Anthropic

from app.agent.state import AgentState, UserQuery, DocumentInfo, OCRResult, ToolCall
from app.ocr.processor import OCRProcessor
from app.utils.helpers import determine_document_type, extract_file_metadata

logger = logging.getLogger(__name__)

# Initialize clients
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
ocr_processor = OCRProcessor()

def parse_user_input(state: AgentState) -> AgentState:
    """
    Parse user input to determine intent and document info.
    """
    user_input = state.user_input.strip()
    logger.info(f"Parsing user input: {user_input[:100]}...")
    
    # Create a new state to avoid modifying the input state
    new_state = AgentState(**state.dict())
    
    # Detect if there's a document path or URL in the input
    document_path = None
    document_url = None
    
    # Simple detection of file paths and URLs (in a real app, this would be more robust)
    for word in user_input.split():
        if word.startswith(("http://", "https://")):
            document_url = word
            break
        elif (
            "/" in word or "\\" in word or  # Unix/Windows path separator
            (word.endswith((".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff")))
        ):
            document_path = word
            break
    
    # Create document info if we found a path or URL
    if document_path or document_url:
        doc_info = DocumentInfo(
            file_path=document_path,
            url=document_url,
            document_type=determine_document_type(document_path or document_url or "")
        )
        
        # If it's a file path, get additional metadata
        if document_path:
            try:
                metadata = extract_file_metadata(document_path)
                doc_info.content_type = metadata.get("content_type")
                doc_info.size_bytes = metadata.get("size_bytes")
            except Exception as e:
                logger.warning(f"Error extracting file metadata: {str(e)}")
        
        new_state.document_info = doc_info
    
    # Create user query
    query = user_input
    # If we found a document, remove its reference from the query for clarity
    if document_path:
        query = query.replace(document_path, "").strip()
    if document_url:
        query = query.replace(document_url, "").strip()
    
    # Determine if OCR/RAG is needed based on simple heuristics
    # In a real app, you'd use a more sophisticated approach, possibly with LLM
    requires_ocr = (
        "ocr" in query.lower() or 
        "scan" in query.lower() or
        "extract" in query.lower() or
        "read" in query.lower() or
        (new_state.document_info is not None)
    )
    
    requires_rag = (
        "search" in query.lower() or
        "find" in query.lower() or
        "similar" in query.lower() or
        "related" in query.lower() or
        "question" in query.lower() or
        "?" in query
    )
    
    new_state.user_query = UserQuery(
        query_text=query,
        requires_ocr=requires_ocr,
        requires_rag=requires_rag
    )
    
    new_state.current_step = "determine_next_step"
    new_state.add_thought("Parsed user input and identified document information and query intent.")
    
    return new_state

def determine_next_step(state: AgentState) -> str:
    """
    Determine the next step based on the current state.
    """
    logger.info("Determining next step...")
    
    if state.error:
        return "handle_error"
    
    if not state.user_query:
        return "handle_error"
    
    # If OCR is required and we have document info
    if state.user_query.requires_ocr and state.document_info and state.document_info.is_valid():
        return "process_document_ocr"
    
    # If we need to process a document but don't have enough info
    if state.user_query.requires_ocr and (not state.document_info or not state.document_info.is_valid()):
        return "request_document_info"
    
    # If RAG is required after OCR
    if state.ocr_results and state.ocr_results.success and state.user_query.requires_rag:
        return "perform_rag_query"
    
    # If we have OCR results, generate response
    if state.ocr_results and state.ocr_results.success:
        return "generate_response"
    
    # If no special processing needed, just generate a response
    return "generate_response"

def process_document_ocr(state: AgentState) -> AgentState:
    """
    Process document with OCR.
    """
    logger.info("Processing document with OCR...")
    
    new_state = AgentState(**state.dict())
    new_state.current_step = "process_document_ocr"
    new_state.status = "processing"
    
    if not new_state.document_info or not new_state.document_info.is_valid():
        new_state.error = "No valid document information provided"
        new_state.status = "error"
        return new_state
    
    try:
        # Create tool call record
        tool_call = ToolCall(
            tool_name="ocr_processor",
            tool_input={
                "file_path": new_state.document_info.file_path,
                "url": new_state.document_info.url
            }
        )
        new_state.add_tool_call(tool_call)
        
        # Process document with OCR
        if new_state.document_info.file_path:
            ocr_result = ocr_processor.process_file(new_state.document_info.file_path)
        elif new_state.document_info.url:
            ocr_result = ocr_processor.process_url(new_state.document_info.url)
        else:
            raise ValueError("No file path or URL provided")
        
        # Update state with OCR results
        new_state.ocr_results = OCRResult(
            raw_text=ocr_result.text,
            markdown=ocr_result.markdown,
            document_id=ocr_result.id,
            success=True,
            pages_processed=len(ocr_result.pages) if hasattr(ocr_result, 'pages') else 1,
            has_images=hasattr(ocr_result, 'images') and bool(ocr_result.images),
            image_count=len(ocr_result.images) if hasattr(ocr_result, 'images') else 0
        )
        
        # Update tool call record
        tool_call.success = True
        tool_call.tool_output = {
            "success": True,
            "pages_processed": new_state.ocr_results.pages_processed,
            "has_images": new_state.ocr_results.has_images,
            "image_count": new_state.ocr_results.image_count
        }
        
        new_state.add_thought("Successfully processed document with OCR")
        
    except Exception as e:
        logger.error(f"Error processing document with OCR: {str(e)}")
        new_state.error = f"Error processing document with OCR: {str(e)}"
        new_state.status = "error"
        
        # Update tool call record
        if new_state.get_last_tool_call():
            tool_call = new_state.get_last_tool_call()
            tool_call.success = False
            tool_call.error_message = str(e)
        
        new_state.add_thought(f"Failed to process document with OCR: {str(e)}")
    
    return new_state

def perform_rag_query(state: AgentState) -> AgentState:
    """
    Perform a RAG query on the document content.
    """
    logger.info("Performing RAG query...")
    
    # This is a placeholder for the actual RAG implementation
    # In a real application, you would implement this with a vector database and embeddings
    
    new_state = AgentState(**state.dict())
    new_state.current_step = "perform_rag_query"
    
    # For now, just simulate a RAG response using document understanding from Mistral
    if new_state.ocr_results and new_state.ocr_results.success and new_state.user_query:
        try:
            # Use document understanding capabilities for answering questions about the document
            # This is a temporary solution until we implement full RAG
            document_source = new_state.document_info.file_path or new_state.document_info.url
            
            if document_source:
                answer = ocr_processor.document_understanding(
                    document_source=document_source,
                    query=new_state.user_query.query_text
                )
                
                new_state.rag_results = {
                    "query": new_state.user_query.query_text,
                    "answer": answer,
                    "results": [],
                    "sources": []
                }
                
                new_state.add_thought("Used document understanding to answer query about the document")
            else:
                new_state.error = "No document source available for RAG query"
        except Exception as e:
            logger.error(f"Error performing RAG query: {str(e)}")
            new_state.error = f"Error performing RAG query: {str(e)}"
    else:
        new_state.error = "No OCR results available for RAG query"
    
    return new_state

def generate_response(state: AgentState) -> AgentState:
    """
    Generate a response using Anthropic API.
    """
    logger.info("Generating response...")
    
    new_state = AgentState(**state.dict())
    new_state.current_step = "generate_response"
    new_state.status = "processing"
    
    system_prompt = """
    You are an AI assistant that helps users analyze documents using OCR. 
    You can extract text from documents, answer questions about their content, and provide insights.
    
    If you have processed a document with OCR, summarize what you found and provide relevant information.
    If you have answered a specific question about a document, provide the answer clearly.
    Be helpful, concise, and accurate in your responses.
    """
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": state.user_input
        }
    ]
    
    # Add context from OCR results if available
    if state.ocr_results and state.ocr_results.success:
        context = f"""
        I have processed your document with OCR. Here is what I found:
        
        Document type: {state.document_info.document_type if state.document_info else 'Unknown'}
        Pages processed: {state.ocr_results.pages_processed}
        
        Here's a summary of the content:
        {state.ocr_results.raw_text[:500]}...
        """
        
        messages.append({
            "role": "assistant",
            "content": context
        })
    
    # Add RAG results if available
    if state.rag_results and hasattr(state.rag_results, 'answer') and state.rag_results.answer:
        rag_response = f"""
        Based on your question about the document, I found this answer:
        
        {state.rag_results.answer}
        """
        
        messages.append({
            "role": "assistant",
            "content": rag_response
        })
    
    try:
        # Generate response using Anthropic
        response = anthropic_client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-20250219"),
            messages=messages,
            max_tokens=1000
        )
        
        new_state.response = response.content[0].text
        new_state.status = "completed"
        new_state.add_thought("Generated response using Anthropic API")
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        new_state.error = f"Error generating response: {str(e)}"
        new_state.status = "error"
        new_state.add_thought(f"Failed to generate response: {str(e)}")
    
    return new_state

def request_document_info(state: AgentState) -> AgentState:
    """
    Generate a response requesting document information.
    """
    logger.info("Requesting document information...")
    
    new_state = AgentState(**state.dict())
    new_state.current_step = "request_document_info"
    
    new_state.response = """
    I need more information about the document you want me to process.
    
    Please provide either:
    - A file path to a local document (PDF or image)
    - A URL to a document online
    
    For example: "Extract text from /path/to/document.pdf" or "Analyze this document: https://example.com/document.pdf"
    """
    
    new_state.status = "completed"
    new_state.add_thought("Requested additional document information from user")
    
    return new_state

def handle_error(state: AgentState) -> AgentState:
    """
    Handle errors and generate appropriate responses.
    """
    logger.info("Handling error...")
    
    new_state = AgentState(**state.dict())
    new_state.current_step = "handle_error"
    
    if not new_state.error:
        new_state.error = "An unknown error occurred"
    
    new_state.response = f"""
    I encountered an error while processing your request:
    
    {new_state.error}
    
    Please try again with more information or a different approach.
    """
    
    new_state.status = "error"
    new_state.add_thought(f"Handled error: {new_state.error}")
    
    return new_state

def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph for the OCR agent.
    """
    # Create a new graph
    graph = StateGraph(AgentState)
    
    # Add nodes to the graph
    graph.add_node("parse_user_input", parse_user_input)
    graph.add_node("process_document_ocr", process_document_ocr)
    graph.add_node("perform_rag_query", perform_rag_query)
    graph.add_node("generate_response", generate_response)
    graph.add_node("request_document_info", request_document_info)
    graph.add_node("handle_error", handle_error)
    
    # Connect the nodes
    # Start with parsing user input
    graph.set_entry_point("parse_user_input")
    
    # From parse_user_input, determine next step
    graph.add_conditional_edges(
        "parse_user_input",
        determine_next_step,
        {
            "process_document_ocr": "process_document_ocr",
            "request_document_info": "request_document_info",
            "perform_rag_query": "perform_rag_query",
            "generate_response": "generate_response",
            "handle_error": "handle_error"
        }
    )
    
    # From process_document_ocr, determine next step
    graph.add_conditional_edges(
        "process_document_ocr",
        determine_next_step,
        {
            "perform_rag_query": "perform_rag_query",
            "generate_response": "generate_response",
            "handle_error": "handle_error"
        }
    )
    
    # From perform_rag_query, go to generate_response or handle_error
    graph.add_conditional_edges(
        "perform_rag_query",
        determine_next_step,
        {
            "generate_response": "generate_response",
            "handle_error": "handle_error"
        }
    )
    
    # End nodes
    graph.add_edge("generate_response", "END")
    graph.add_edge("request_document_info", "END")
    graph.add_edge("handle_error", "END")
    
    return graph

# Create the agent graph
agent_graph = create_agent_graph()