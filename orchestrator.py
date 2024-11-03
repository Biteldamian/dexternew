# agents/orchestrator.py
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import json
import ollama
from rich.console import Console
from utils.logger import logger

from agents.base import Task, BaseAgent
from memory.manager import EnhancedMemoryManager
from database.operator import KnowledgeBase
from toolbox.tools import ToolKit

console = Console()

class DexterOrchestrator:
    def __init__(self, 
                 memory_manager: EnhancedMemoryManager,
                 knowledge_base: KnowledgeBase,
                 toolkit: ToolKit):
        self.memory_manager = memory_manager
        self.knowledge_base = knowledge_base
        self.toolkit = toolkit
        self.agents = {}
        self.task_history = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
    
    async def process_objective(self, objective: str, agent: Optional[BaseAgent] = None) -> Dict[str, Any]:
        try:
            logger.info(f"Processing objective: {objective}")
            
            task = Task(
                id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=objective,
                type=self._determine_task_type(objective),
                priority=1,
                context={}
            )
            
            # Log start of processing
            self.knowledge_base.log_interaction(
                interaction_type="objective_start",
                content=objective
            )
            
            # Process task
            if agent:
                result = await self._process_with_agent(task, agent)
            else:
                result = await self._route_and_process_task(task)
            
            # Log completion
            self.knowledge_base.log_interaction(
                interaction_type="objective_complete",
                content=str(result.result),
                status=result.status
            )
            
            return {
                "status": "success",
                "result": result.result,
                "task_id": result.id,
                "task": result
            }
            
        except Exception as e:
            error_msg = f"Error processing objective: {str(e)}"
            logger.error(error_msg)
            
            # Log error
            self.knowledge_base.log_interaction(
                interaction_type="objective_error",
                content=objective,
                status="error",
                error=str(e)
            )
            
            return {
                "status": "error",
                "error": str(e),
                "task_id": task.id if 'task' in locals() else None
            }
    
    async def _process_with_agent(self, task: Task, agent: BaseAgent) -> Task:
        """Process task with specific agent"""
        try:
            return await agent.process_task(task)
        except Exception as e:
            console.print(f"[red]Error in agent processing:[/red] {str(e)}")
            task.status = "failed"
            task.result = f"Error: {str(e)}"
            return task
    
    async def _route_and_process_task(self, task: Task) -> Task:
        """Route task to appropriate agent"""
        try:
            # Get appropriate agent
            agent_name = self._select_agent(task)
            agent = self.agents.get(agent_name)
            
            if not agent:
                raise ValueError(f"Agent {agent_name} not found")
            
            # Process with selected agent
            result = await self._process_with_agent(task, agent)
            
            # Store in task history
            self.task_history.append({
                "task_id": task.id,
                "agent": agent_name,
                "status": result.status,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            console.print(f"[red]Error in task routing:[/red] {str(e)}")
            task.status = "failed"
            task.result = f"Error: {str(e)}"
            return task
    
    def _determine_task_type(self, objective: str) -> str:
        """Determine task type from objective"""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["create", "code", "program", "develop", "game"]):
            return "code_generation"
        elif any(word in objective_lower for word in ["research", "find", "search", "analyze"]):
            return "research"
        else:
            return "analysis"
    
    def _select_agent(self, task: Task) -> str:
        """Select appropriate agent based on task type"""
        if task.type == "code_generation":
            return "CodeAgent"
        elif task.type == "research":
            return "ResearchAgent"
        else:
            return "DexterGPT"
    
    def _extract_project_info(self, task: Task) -> Dict[str, Any]:
        """Extract project information from completed task"""
        if task.type != "code_generation" or not task.result:
            return {}
        
        try:
            result_str = str(task.result)
            
            # Extract project name
            project_name = "project"  # Default name
            if "Project Name:" in result_str:
                project_name = result_str.split("Project Name:")[1].split("\n")[0].strip()
            
            # Extract code blocks
            code_blocks = []
            if "```" in result_str:
                import re
                code_blocks = re.findall(r'Filename: (\S+)\s*```[\w]*\n(.*?)\n```', result_str, re.DOTALL)
            
            return {
                "project_name": project_name,
                "code_blocks": code_blocks
            }
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not extract project info:[/yellow] {str(e)}")
            return {}