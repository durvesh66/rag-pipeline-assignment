# RAG Pipeline - Document Question Answering System

A production-ready Retrieval-Augmented Generation (RAG) pipeline that allows users to upload documents and ask questions based on their content.

## 🚀 Features

- 📁 **Document Upload**: Support for PDF, DOCX, and TXT files (up to 20 documents, 1000 pages each)
- 🔍 **Intelligent Search**: Vector-based document retrieval using FAISS
- 🤖 **Question Answering**: Context-aware responses using document content
- 🚀 **REST API**: FastAPI-based API with comprehensive endpoints
- 🐳 **Containerized**: Docker and Docker Compose for easy deployment
- 📊 **Metadata Management**: SQLite database for document tracking
- 🧪 **Tested**: Comprehensive test suite included

## 🏗️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Database**: SQLite with aiosqlite
- **Document Processing**: PyPDF2, python-docx
- **Containerization**: Docker, Docker Compose

## 📋 System Requirements

- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 2GB free space
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+

## ⚡ Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### Installation

1. **Clone the repository**
