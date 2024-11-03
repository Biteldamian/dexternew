# utils/analysis.py
from rich.table import Table
from rich.console import Console
import sqlite3

console = Console()

def view_interaction_history(db_path: str = "knowledge/dexter.db"):
    """View interaction history from database"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, type, status, content, error
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            
            table = Table(title="Recent Interactions")
            table.add_column("Timestamp")
            table.add_column("Type")
            table.add_column("Status")
            table.add_column("Content")
            table.add_column("Error")
            
            for row in cursor.fetchall():
                table.add_row(*[str(cell) for cell in row])
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error viewing interaction history:[/red] {str(e)}")

def view_task_results(db_path: str = "knowledge/dexter.db"):
    """View task results from database"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT created_at, task_id, agent_name, status, content, error
                FROM task_results
                ORDER BY created_at DESC
                LIMIT 50
            """)
            
            table = Table(title="Recent Task Results")
            table.add_column("Timestamp")
            table.add_column("Task ID")
            table.add_column("Agent")
            table.add_column("Status")
            table.add_column("Content")
            table.add_column("Error")
            
            for row in cursor.fetchall():
                table.add_row(*[str(cell) for cell in row])
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error viewing task results:[/red] {str(e)}")