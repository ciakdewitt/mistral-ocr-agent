"""
State management for the LangGraph agent.
"""
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Literal, Union
from typing_extensions import NotRequired
from pydantic import BaseModel, Field

class DocumentInfo(BaseModel):
    """Information about a document being processed."""
    file_path: Optional[str] = None
    url: Optional[str] = None
    document_type: Literal["pdf", "image", "text", "unknown"] = "unknown"
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    num_pages: Optional[int] = None
    
    def is_valid(self) -> bool:
        """Check if document info is valid."""
        return (self.file_path is not None or self.url is not None)

class OCRResult(BaseModel):
    """Results from OCR processing."""
    raw_text: str = Field(default="")
    markdown: str = Field(default="")
    document_id: Optional[str] = None
    success: bool = Field(default=False)
    error_message: Optional[str] = None
    pages_processed: int = Field(default=0)
    processing_time_ms: Optional[int] = None
    has_images: bool = Field(default=False)
    image_count: int = Field(default=0)

class RAGQueryResult(BaseModel):
    """Results from a RAG query."""
    query: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    answer: Optional[str] = None

class ToolCall(BaseModel):
    """A tool call made by the agent."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Dict[str, Any]] = None
    success: bool = False
    error_message: Optional[str] = None

class UserQuery(BaseModel):
    """User query information."""
    query_text: str
    query_type: str = "general"
    document_context: Optional[str] = None
    requires_ocr: bool = False
    requires_rag: bool = False

class AgentState(BaseModel):
    """State of the LangGraph agent."""
    # Input state
    user_input: str = Field(default="")
    user_query: Optional[UserQuery] = None
    
    # Document state
    document_info: Optional[DocumentInfo] = None
    document_content: Optional[str] = None
    
    # Processing state
    ocr_results: Optional[OCRResult] = None
    rag_results: Optional[RAGQueryResult] = None
    
    # Agent execution state
    current_step: str = Field(default="start")
    tool_calls: List[ToolCall] = Field(default_factory=list)
    thoughts: List[str] = Field(default_factory=list)
    
    # Output state
    response: str = Field(default="")
    error: Optional[str] = None
    status: str = Field(default="idle")  # idle, processing, completed, error
    
    def add_thought(self, thought: str) -> None:
        """Add an agent thought to the state."""
        self.thoughts.append(thought)
    
    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Add a tool call to the state."""
        self.tool_calls.append(tool_call)
    
    def get_last_tool_call(self) -> Optional[ToolCall]:
        """Get the last tool call."""
        if not self.tool_calls:
            return None
        return self.tool_calls[-1]
    
    def reset_processing_state(self) -> None:
        """Reset the processing state."""
        self.current_step = "start"
        self.tool_calls = []
        self.thoughts = []
        self.response = ""
        self.error = None
        self.status = "idle"