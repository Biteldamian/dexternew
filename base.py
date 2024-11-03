# agents/base.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from rich.console import Console
from memory.manager import EnhancedMemoryManager

console = Console()

@dataclass
class Task:
    id: str
    content: str
    type: str
    priority: int
    context: Dict[str, Any]
    status: str = "pending"
    result: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    memory_references: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    error_message: Optional[str] = None
    
    def mark_completed(self, result: Any):
        """Mark task as completed with result"""
        self.status = "completed"
        self.result = result
    
    def mark_failed(self, error: str):
        """Mark task as failed with error message"""
        self.status = "failed"
        self.error_message = error
    
    def add_subtask(self, subtask: 'Task'):
        """Add a subtask to this task"""
        subtask.parent_task_id = self.id
        self.subtasks.append(subtask)
    
    def add_memory_reference(self, memory_id: str):
        """Add a memory reference to this task"""
        if memory_id not in self.memory_references:
            self.memory_references.append(memory_id)


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, 
                 name: str,
                 capabilities: List[str],
                 **kwargs):  # Add **kwargs to accept additional arguments
        self.name = name
        self.capabilities = capabilities
        self.task_history = []
        # Store any additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    
    @abstractmethod
    async def process_task(self, task: Task) -> Task:
        """Process a task and return the result"""
        pass
    
    def can_handle_task(self, task: Task) -> bool:
        """Check if agent can handle the given task type"""
        return task.type in self.capabilities
    
    def _format_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Format prompt for the task"""
        return f"""
Task ID: {task.id}
Type: {task.type}
Priority: {task.priority}
Content: {task.content}

Context:
{json.dumps(context, indent=2)}

Previous Task History:
{self._format_task_history()}

Please process this task according to its type and requirements.
"""
    
    def _format_task_history(self) -> str:
        """Format recent task history"""
        recent_tasks = self.task_history[-5:] if self.task_history else []
        return "\n".join([
            f"Task {task.id}: {task.type} - {task.status}"
            for task in recent_tasks
        ])
    
    def _log_task(self, task: Task):
        """Log task to history"""
        self.task_history.append(task)
        console.print(f"[blue]{self.name}:[/blue] Processing task {task.id}")
    
    def _handle_error(self, task: Task, error: Exception) -> Task:
        """Handle task processing error"""
        error_message = f"Error processing task: {str(error)}"
        console.print(f"[red]{self.name} Error:[/red] {error_message}")
        task.mark_failed(error_message)
        return task
    
    async def _preprocess_task(self, task: Task) -> Dict[str, Any]:
        """Preprocess task and gather context"""
        context = task.context.copy()
        
        # Add task history context
        context["recent_tasks"] = [
            {"id": t.id, "type": t.type, "status": t.status}
            for t in self.task_history[-3:]
        ]
        
        # Add memory references if available
        if hasattr(self, 'memory_manager') and self.memory_manager:
            relevant_memories = await self.memory_manager.retrieve_memories(
                query=task.content,
                limit=5
            )
            context["relevant_memories"] = relevant_memories
        
        return context
    
    async def _postprocess_task(self, task: Task):
        """Postprocess completed task"""
        # Store task in memory if available
        if hasattr(self, 'memory_manager') and self.memory_manager:
            memory_id = await self.memory_manager.add_memory(
                content=str(task.result),
                memory_type=f"task_result_{task.type}",
                context={"task_id": task.id}
            )
            task.add_memory_reference(memory_id)
        
        # Log completion
        console.print(f"[green]{self.name}:[/green] Completed task {task.id}")
        
        # Add to history
        self._log_task(task)