import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_upload_single_document():
    """Test uploading a single document"""
    test_content = "This is a test document with some content for testing the RAG pipeline. It contains multiple sentences to test chunking."
    test_file = ("test.txt", io.BytesIO(test_content.encode()), "text/plain")
    
    response = client.post("/upload", files={"files": test_file})
    assert response.status_code == 200
    data = response.json()
    assert "Successfully processed" in data["message"]
    assert data["total_chunks"] > 0

def test_upload_multiple_documents():
    """Test uploading multiple documents"""
    files = [
        ("test1.txt", io.BytesIO(b"First test document content with substantial text for chunking"), "text/plain"),
        ("test2.txt", io.BytesIO(b"Second test document content with different information"), "text/plain")
    ]
    
    response = client.post("/upload", files=[("files", f) for f in files])
    assert response.status_code == 200
    data = response.json()
    assert len(data["documents"]) == 2

def test_upload_too_many_documents():
    """Test uploading more than 20 documents"""
    files = [("files", (f"test{i}.txt", io.BytesIO(b"test content"), "text/plain")) 
             for i in range(21)]
    
    response = client.post("/upload", files=files)
    assert response.status_code == 400
    assert "Maximum 20 documents allowed" in response.json()["detail"]

def test_metadata_endpoint():
    """Test metadata endpoint"""
    response = client.get("/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "documents" in data
