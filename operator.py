# database/operator.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from utils.logger import logger
from rich.console import Console

console = Console()

class KnowledgeBase:
    def __init__(self, db_path: str = "knowledge/dexter.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize database with tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        content TEXT,
                        doc_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_entries (
                        id INTEGER PRIMARY KEY,
                        topic TEXT,
                        content TEXT,
                        source TEXT,
                        relevance REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS document_tags (
                        document_id INTEGER,
                        tag_id INTEGER,
                        FOREIGN KEY(document_id) REFERENCES documents(id),
                        FOREIGN KEY(tag_id) REFERENCES tags(id),
                        PRIMARY KEY(document_id, tag_id)
                    )
                """)
        except Exception as e:
            console.print(f"[red]Error setting up database:[/red] {str(e)}")
    
    async def get_relevant_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge based on query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # First try to find exact matches
                cursor = conn.execute("""
                    SELECT id, content, doc_type, created_at
                    FROM documents
                    WHERE content LIKE ?
                    UNION
                    SELECT id, content, 'knowledge' as doc_type, created_at
                    FROM knowledge_entries
                    WHERE content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (f"%{query}%", f"%{query}%", limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'timestamp': row[3]
                    })
                
                return results
                
        except Exception as e:
            console.print(f"[red]Error retrieving knowledge:[/red] {str(e)}")
            return []
    
    def add_document(self, name: str, content: str, doc_type: str, 
                    tags: List[str] = None) -> Optional[int]:
        """Add a document to the knowledge base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO documents (name, content, doc_type)
                    VALUES (?, ?, ?)
                    """,
                    (name, content, doc_type)
                )
                doc_id = cursor.lastrowid
                
                # Add tags if provided
                if tags:
                    for tag in tags:
                        # Insert tag if it doesn't exist
                        conn.execute(
                            "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                            (tag,)
                        )
                        
                        # Get tag id
                        cursor = conn.execute(
                            "SELECT id FROM tags WHERE name = ?",
                            (tag,)
                        )
                        tag_id = cursor.fetchone()[0]
                        
                        # Link document to tag
                        conn.execute(
                            """
                            INSERT INTO document_tags (document_id, tag_id)
                            VALUES (?, ?)
                            """,
                            (doc_id, tag_id)
                        )
                
                return doc_id
                
        except Exception as e:
            console.print(f"[red]Error adding document:[/red] {str(e)}")
            return None
    
    def add_knowledge(self, topic: str, content: str, 
                     source: str = None, relevance: float = 1.0) -> Optional[int]:
        """Add a knowledge entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO knowledge_entries 
                    (topic, content, source, relevance)
                    VALUES (?, ?, ?, ?)
                    """,
                    (topic, content, source, relevance)
                )
                return cursor.lastrowid
                
        except Exception as e:
            console.print(f"[red]Error adding knowledge entry:[/red] {str(e)}")
            return None