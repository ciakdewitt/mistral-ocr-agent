"""
RAG system tool for the LangGraph agent.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# This is a basic RAG implementation for demonstration
# In a production system, you would use a more robust vector store and embedding model

logger = logging.getLogger(__name__)

class RAGTool:
    """
    Tool for retrieving information using RAG (Retrieval Augmented Generation).
    """
    
    def __init__(self, vector_store_path: Optional[str] = None):
        """
        Initialize the RAG tool.
        
        Args:
            vector_store_path: Path to the vector store. If None, will use environment variable.
        """
        self.vector_store_path = vector_store_path or os.environ.get("VECTOR_DB_PATH", "./data/vector_store")
        self.chunk_size = int(os.environ.get("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", "200"))
        
        # Initialize Chroma client
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.vector_store_path)
            logger.info(f"Initialized ChromaDB client at {self.vector_store_path}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
    
    def ingest_document(self, document_text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Ingest a document into the RAG system.
        
        Args:
            document_text: Text content of the document
            document_id: Unique ID for the document
            metadata: Optional metadata about the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
            )
            
            documents = text_splitter.create_documents([document_text], [metadata or {}])
            
            # Prepare ChromaDB collection
            collection_name = "ocr_documents"
            try:
                collection = self.chroma_client.get_or_create_collection(collection_name)
            except Exception as e:
                logger.error(f"Error getting or creating collection: {str(e)}")
                return False
            
            # Add documents to the collection
            chunk_ids = []
            chunk_texts = []
            chunk_metadatas = []
            
            for i, doc in enumerate(documents):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                chunk_texts.append(doc.page_content)
                
                # Prepare metadata
                doc_metadata = doc.metadata.copy()
                doc_metadata["document_id"] = document_id
                doc_metadata["chunk_id"] = i
                chunk_metadatas.append(doc_metadata)
            
            # Add to collection
            collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                metadatas=chunk_metadatas
            )
            
            logger.info(f"Successfully ingested document {document_id} with {len(documents)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            return False
    
    def query(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query_text: Query text
            top_k: Number of top results to return
            
        Returns:
            Dictionary with results and sources
        """
        try:
            collection_name = "ocr_documents"
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except Exception as e:
                logger.error(f"Error getting collection: {str(e)}")
                return {
                    "query": query_text,
                    "results": [],
                    "sources": [],
                    "error": f"No documents found in collection: {str(e)}"
                }
            
            # Query the collection
            result = collection.query(
                query_texts=[query_text],
                n_results=top_k
            )
            
            # Format results
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            
            results = []
            sources = []
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                # Add result
                results.append({
                    "content": doc,
                    "relevance": 1.0 - min(distance, 1.0)  # Convert distance to relevance score
                })
                
                # Add source
                source = {
                    "document_id": metadata.get("document_id", "unknown"),
                    "chunk_id": metadata.get("chunk_id", i),
                    "relevance": 1.0 - min(distance, 1.0)
                }
                sources.append(source)
            
            return {
                "query": query_text,
                "results": results,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return {
                "query": query_text,
                "results": [],
                "sources": [],
                "error": str(e)
            }
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks from the RAG system.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection_name = "ocr_documents"
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except Exception:
                return False
            
            # Query to find all chunks of this document
            result = collection.get(
                where={"document_id": document_id}
            )
            
            if result and "ids" in result and result["ids"]:
                # Delete the chunks
                collection.delete(
                    ids=result["ids"]
                )
                logger.info(f"Deleted document {document_id} with {len(result['ids'])} chunks")
                return True
            else:
                logger.warning(f"No chunks found for document {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False