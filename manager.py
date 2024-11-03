# memory/manager.py
from typing import List, Dict, Any, Optional
import sqlite3
from datetime import datetime
import json
from rich.console import Console

console = Console()

class EnhancedMemoryManager:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    type TEXT,
                    timestamp DATETIME,
                    context TEXT
                )
            """)
    
    def add_memory(self, content: str, memory_type: str, context: Dict[str, Any] = None) -> Optional[str]:
        try:
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO memories (id, content, type, timestamp, context) VALUES (?, ?, ?, ?, ?)",
                    (memory_id, content, memory_type, datetime.now(), json.dumps(context))
                )
            
            return memory_id
        except Exception as e:
            console.print(f"[red]Error adding memory:[/red] {str(e)}")
            return None
    
    def retrieve_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT id, content, type, timestamp, context
                    FROM memories
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", limit)
                )
                
                memories = []
                for row in cursor.fetchall():
                    memories.append({
                        'id': row[0],
                        'content': row[1],
                        'type': row[2],
                        'timestamp': row[3],
                        'context': json.loads(row[4]) if row[4] else None
                    })
                
                return memories
        except Exception as e:
            console.print(f"[red]Error retrieving memories:[/red] {str(e)}")
            return []