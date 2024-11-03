# agents/dexter_agent.py
from typing import Dict, Any
import ollama
import json
from rich.console import Console
from .base import BaseAgent, Task

console = Console()

class DexterAgent(BaseAgent):
    def __init__(self, 
                 name: str = "DexterGPT",
                 model_name: str = "llama3.2",
                 memory_manager = None,
                 knowledge_base = None,
                 toolkit = None):
        # Pass all arguments to parent class using kwargs
        super().__init__(
            name=name,
            capabilities=[
                "task_analysis",
                "resource_management",
                "tool_coordination"
            ],
            model_name=model_name,
            memory_manager=memory_manager,
            knowledge_base=knowledge_base,
            toolkit=toolkit
        )
    
    async def process_task(self, task: Task) -> Task:
        try:
            # Get context
            context = await self._get_context(task)
            
            # Process with Ollama
            response = ollama.generate(
                model=self.model_name,  # Use model_name instead of model
                prompt=self._format_prompt(task, context)
            )
            
            # Update task
            task.result = response['response']
            task.status = "completed"
            
            # Store in memory if available
            if self.memory_manager:
                memory_id = self.memory_manager.add_memory(
                    content=str(task.result),
                    memory_type="result",
                    context={"task_id": task.id}
                )
                if memory_id:
                    task.memory_references.append(memory_id)
            
            return task
            
        except Exception as e:
            console.print(f"[red]Error in DexterAgent:[/red] {str(e)}")
            task.status = "failed"
            task.result = f"Error: {str(e)}"
            return task
    
    async def _get_context(self, task: Task) -> Dict[str, Any]:
        context = {}
        
        if self.memory_manager:
            memories = self.memory_manager.retrieve_memories(task.content)
            if memories:
                context["memories"] = memories
        
        if self.knowledge_base:
            try:
                knowledge = await self.knowledge_base.get_relevant_knowledge(task.content)
                if knowledge:
                    context["knowledge"] = knowledge
            except Exception as e:
                console.print(f"[yellow]Warning: Could not retrieve knowledge: {str(e)}[/yellow]")
        
        return context
    
    def _format_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        prompt = f"""
Task Type: {task.type}
Task Content: {task.content}

Context:
{json.dumps(context, indent=2)}

Instructions:
For analysis tasks, provide comprehensive information and insights.
For code tasks, include working code with explanations.
For research tasks, provide detailed findings and sources.

Response:
"""
        return prompt