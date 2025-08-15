import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from pathlib import Path

from models import QueryRequest, QueryResponse, UploadResponse, MetadataResponse
from database import DocumentStore
from utils import DocumentProcessor, VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Pipeline API",
    description="Document upload and query system using RAG",
    version="1.0.0"
)
from fastapi.responses import RedirectResponse

@app.get("/")
async def read_root():
    """Redirect root to API documentation"""
    return RedirectResponse(url='/docs')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_processor = DocumentProcessor()
vector_store = VectorStore()
document_store = DocumentStore()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    Path("data").mkdir(exist_ok=True)
    await document_store.initialize()
    logger.info("Application started successfully")

@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        if len(files) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 documents allowed")
        
        processed_docs = []
        total_chunks = 0
        
        for file in files:
            content = await file.read()
            if len(content) > 10_000_000:  # 10MB limit
                raise HTTPException(status_code=400, detail=f"File {file.filename} too large")
            
            chunks = await doc_processor.process_document(content, file.filename)
            
            if len(chunks) > 1000:
                raise HTTPException(status_code=400, detail=f"Document {file.filename} exceeds 1000 page limit")
            
            total_chunks += len(chunks)
            doc_id = await vector_store.add_document(chunks, file.filename)
            await document_store.store_document_metadata(doc_id, file.filename, len(chunks))
            
            processed_docs.append({
                "filename": file.filename,
                "chunks": len(chunks),
                "doc_id": doc_id
            })
        
        return UploadResponse(
            message=f"Successfully processed {len(files)} documents",
            documents=processed_docs,
            total_chunks=total_chunks
        )
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG pipeline"""
    try:
        relevant_chunks = await vector_store.search(request.query, top_k=request.top_k)
        
        if not relevant_chunks:
            return QueryResponse(
                query=request.query,
                answer="No relevant documents found.",
                sources=[],
                chunks_used=0
            )
        
        answer = await doc_processor.generate_response(request.query, relevant_chunks)
        sources = list(set([chunk['filename'] for chunk in relevant_chunks]))
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            chunks_used=len(relevant_chunks)
        )
    
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get system metadata"""
    try:
        metadata = await document_store.get_metadata()
        return MetadataResponse(**metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RAG Pipeline"}

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT variable
    uvicorn.run(app, host="0.0.0.0", port=port)
