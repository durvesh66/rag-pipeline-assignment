import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import aiosqlite

class DocumentStore:
    def __init__(self, db_path: str = "data/documents.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize the database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    metadata TEXT
                )
            """)
            await db.commit()
    
    async def store_document_metadata(self, doc_id: str, filename: str, chunk_count: int, metadata: Dict = None):
        """Store document metadata"""
        upload_date = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {})
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO documents 
                (doc_id, filename, upload_date, chunk_count, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, filename, upload_date, chunk_count, metadata_json))
            await db.commit()
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get system metadata"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*), SUM(chunk_count) FROM documents") as cursor:
                row = await cursor.fetchone()
                total_docs = row[0] or 0
                total_chunks = row[1] or 0
            
            documents = []
            async with db.execute("SELECT * FROM documents ORDER BY upload_date DESC") as cursor:
                async for row in cursor:
                    documents.append({
                        'doc_id': row[0],
                        'filename': row[1],
                        'upload_date': row[2],
                        'chunk_count': row[3]
                    })
            
            return {
                'total_documents': total_docs,
                'total_chunks': total_chunks,
                'documents': documents
            }
    
    async def delete_document(self, doc_id: str):
        """Delete document metadata"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            await db.commit()
