import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_query_with_documents():
    """Test querying after uploading documents"""
    # First upload a document
    test_content = "The capital of France is Paris. It is a beautiful city with many attractions. The Eiffel Tower is located in Paris."
    test_file = ("test.txt", io.BytesIO(test_content.encode()), "text/plain")
    
    upload_response = client.post("/upload", files={"files": test_file})
    assert upload_response.status_code == 200
    
    # Then query
    query_data = {"query": "What is the capital of France?", "top_k": 3}
    response = client.post("/query", json=query_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is the capital of France?"
    assert len(data["sources"]) > 0
    assert data["chunks_used"] > 0

def test_query_no_relevant_documents():
    """Test querying with irrelevant content"""
    query_data = {"query": "What is quantum physics?", "top_k": 3}
    response = client.post("/query", json=query_data)
    
    assert response.status_code == 200
    data = response.json()
    # Should still return a response, even if not highly relevant

def test_query_empty_system():
    """Test querying when no documents are in a fresh system"""
    # This test assumes a fresh instance or cleared data
    query_data = {"query": "Any question", "top_k": 5}
    response = client.post("/query", json=query_data)
    
    assert response.status_code == 200
    data = response.json()
    # System should handle empty case gracefully

def test_query_with_different_top_k():
    """Test query with different top_k values"""
    # Upload test document first
    test_content = "Machine learning is a subset of artificial intelligence. It involves algorithms that learn from data."
    test_file = ("ml.txt", io.BytesIO(test_content.encode()), "text/plain")
    
    upload_response = client.post("/upload", files={"files": test_file})
    assert upload_response.status_code == 200
    
    # Test with different top_k values
    for k in [1, 3, 5, 10]:
        query_data = {"query": "What is machine learning?", "top_k": k}
        response = client.post("/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert data["chunks_used"] <= k  # Should not exceed requested top_k
