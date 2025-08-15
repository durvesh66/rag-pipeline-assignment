from pydantic import BaseModel, Field
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="The question to ask")
    top_k: int = Field(default=5, description="Number of relevant chunks to retrieve")
    
class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    chunks_used: int

class UploadResponse(BaseModel):
    message: str
    documents: List[Dict[str, Any]]
    total_chunks: int

class MetadataResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents: List[Dict[str, Any]]
