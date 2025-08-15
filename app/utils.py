import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
import re
from typing import List, Dict, Any
import logging
import io
import PyPDF2
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunk_size = 500
        self.chunk_overlap = 50

    async def process_document(self, content: bytes, filename: str) -> List[Dict[str, Any]]:
        try:
            text = await self._extract_text(content, filename)
            chunks = self._chunk_text(text)

            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    "text": chunk,
                    "chunk_id": i,
                    "filename": filename,
                    "timestamp": datetime.now().isoformat(),
                })

            return processed_chunks
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise

    async def _extract_text(self, content: bytes, filename: str) -> str:
        try:
            file_ext = filename.lower().split(".")[-1]

            if file_ext == "pdf":
                return await self._extract_pdf_text(content)
            elif file_ext in ["docx", "doc"]:
                return await self._extract_docx_text(content)
            else:
                return content.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.warning(f"Error extracting text from {filename}: {str(e)}")
            return content.decode("utf-8", errors="ignore")

    async def _extract_pdf_text(self, content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except:
            return content.decode("utf-8", errors="ignore")

    async def _extract_docx_text(self, content: bytes) -> str:
        try:
            doc_file = io.BytesIO(content)
            doc = DocxDocument(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except:
            return content.decode("utf-8", errors="ignore")

    def _chunk_text(self, text: str) -> List[str]:
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return []

        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i : i + self.chunk_size]
            chunk = " ".join(chunk_words)
            chunks.append(chunk)

            if i + self.chunk_size >= len(words):
                break

        return chunks

    async def generate_response(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate response using retrieved chunks with proper string handling"""
        if not chunks:
            return "No relevant information found in the documents."

        context = "\n\n".join(
            chunk["text"] if isinstance(chunk["text"], str) else str(chunk["text"])
            for chunk in chunks[:3]
        )
        sentences = context.split(".")
        
        # CRITICAL FIX: Force string conversion to prevent numpy array hashing errors
        query_words = set(str(word) for word in query.lower().split())

        relevant_sentences = []
        for sentence in sentences:
            if sentence.strip():
                # CRITICAL FIX: Force string conversion here too
                sentence_words = set(str(word) for word in sentence.lower().split())
                overlap = len(query_words.intersection(sentence_words))
                if overlap > 0:
                    relevant_sentences.append((sentence.strip(), overlap))

        if not relevant_sentences:
            return f"Based on the documents: {context[:200]}..."

        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # CRITICAL FIX: Extract only the sentence strings from tuples
        response = ". ".join(str(s[0]) for s in relevant_sentences[:2])
        
        return response + "." if response else "No specific answer found."


class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.doc_mapping: Dict[int, Dict[str, Any]] = {}

    async def add_document(self, chunks: List[Dict[str, Any]], filename: str) -> str:
        doc_id = str(uuid.uuid4())
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts).astype("float32")

        start_idx = self.index.ntotal
        self.index.add(np.array(embeddings))

        for i, chunk in enumerate(chunks):
            self.doc_mapping[start_idx + i] = {
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk["text"],
                "chunk_id": chunk["chunk_id"],
            }

        return doc_id

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedding_model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        results = []
        for i, idx in enumerate(indices[0]):
            if idx in self.doc_mapping:
                result = self.doc_mapping[idx].copy()
                result["score"] = float(distances[0][i])
                results.append(result)

        return results

    async def delete_document(self, doc_id: str):
        indices_to_remove = []
        for idx, doc_info in self.doc_mapping.items():
            if doc_info["doc_id"] == doc_id:
                indices_to_remove.append(idx)

        for idx in indices_to_remove:
            del self.doc_mapping[idx]
