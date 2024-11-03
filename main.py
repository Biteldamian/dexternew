# main.py
import os
import argparse
from rich.console import Console
from rich.panel import Panel
import ollama
import asyncio
from pathlib import Path

from agents.base import Task
from agents.dexter_agent import DexterAgent
from agents.orchestrator import DexterOrchestrator
from memory.manager import EnhancedMemoryManager
from database.operator import KnowledgeBase
from toolbox.tools import ToolKit
from utils.analysis import view_interaction_history
from utils.analysis import view_task_results

console = Console()

async def main():
    parser = argparse.ArgumentParser(description='DexterGPT CLI')
    parser.add_argument('-o', '--objective', type=str, help='Task objective')
    parser.add_argument('-f', '--file', type=str, help='Path to input file')
    args = parser.parse_args()

    try:
        # Initialize components
        memory_manager = EnhancedMemoryManager()
        knowledge_base = KnowledgeBase()
        toolkit = ToolKit()
        
        # Initialize agent with correct parameters
        dexter_agent = DexterAgent(
            name="DexterGPT",
            model_name="llama3.2",
            memory_manager=memory_manager,
            knowledge_base=knowledge_base,
            toolkit=toolkit
        )
        
        # Get objective
        objective = args.objective or input("Please enter your objective: ")
        
        # Create task
        task = Task(
            id="task_1",
            content=objective,
            type="analysis",
            priority=1,
            context={}
        )
        
        # Process task
        result = await dexter_agent.process_task(task)
        
        # Display result
        if result.status == "completed":
            console.print("[green]Task completed successfully[/green]")
            console.print(Panel(str(result.result)))
        else:
            console.print(f"[red]Task failed:[/red] {result.result}")
        
        return result
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(main())