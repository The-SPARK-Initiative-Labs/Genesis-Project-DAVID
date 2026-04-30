"""
title: David AI System Agent Pipeline
author: AI Team
version: 1.0.0
license: MIT
description: David's LangGraph system agent as Open WebUI pipeline
requirements: langgraph, langchain-core, langchain-ollama, redis, asyncio
"""

import os
import uuid
import time
import asyncio
from typing import List, Union, Generator, Optional, TypedDict, Annotated, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from operator import add

# Import David's existing tools
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'local_agent'))
from david_tools_grouped import DAVID_TOOLS_GROUPED

# David's state schema
class DavidState(TypedDict):
    messages: Annotated[list, add_messages]
    approval_status: str
    user_info: str
    session_id: str

class Pipeline:
    class Valves(BaseModel):
        # Model Configuration
        ollama_model: str = Field(default="qwen3:14b", description="Ollama model name")
        ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
        temperature: float = Field(default=0.6, description="Model temperature")
        
        # David Configuration
        enable_approval_system: bool = Field(default=True, description="Enable tool approval system")
        approval_timeout: int = Field(default=60, description="Approval timeout in seconds")
        auto_approve_safe: bool = Field(default=True, description="Auto-approve safe operations")
        
        # Performance
        enable_streaming: bool = Field(default=True, description="Enable streaming responses")
        max_tool_concurrency: int = Field(default=3, description="Max concurrent tool executions")

    def __init__(self):
        self.type = "pipe"
        self.id = "david_system_agent"
        self.name = "David AI System Agent"
        self.valves = self.Valves()
        
        # Initialize components
        self.memory = MemorySaver()
        self.session_mapping = {}
        self.approval_queue = {}
        self._initialize_david()

    def _initialize_david(self):
        """Initialize David's LangGraph workflow"""
        # Initialize LLM
        self.llm = ChatOllama(
            model=self.valves.ollama_model,
            base_url=self.valves.ollama_base_url,
            temperature=self.valves.temperature,
            top_p=0.95,
            top_k=20,
            num_ctx=8192,
        )
        
        # Bind David's tools to LLM
        self.david_with_tools = self.llm.bind_tools(DAVID_TOOLS_GROUPED)
        
        # Create David's workflow
        workflow = StateGraph(DavidState)
        
        # Add nodes
        workflow.add_node("david_agent", self._david_agent_node)
        workflow.add_node("approval", self._approval_node)
        workflow.add_node("tools", self._tools_node)
        workflow.add_node("rejected", self._rejection_node)
        
        # Define flow
        workflow.add_edge(START, "david_agent")
        workflow.add_edge("david_agent", "approval")
        workflow.add_conditional_edges("approval", self._should_use_tools, ["tools", "rejected", "__end__"])
        workflow.add_edge("tools", "david_agent")
        workflow.add_edge("rejected", "__end__")
        
        # Compile with memory
        self.david_graph = workflow.compile(checkpointer=self.memory)

    def _david_agent_node(self, state: DavidState):
        """David's main agent logic"""
        messages = state["messages"]
        
        # Add system prompt if not present
        system_prompt = """You are David, an AI assistant that helps with coding and system tasks. 
        You have tools available for file operations, system commands, code execution, and more.
        Be helpful, direct, and use tools when needed to accomplish tasks."""
        
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = self.david_with_tools.invoke(messages)
        return {"messages": [response]}

    def _approval_node(self, state: DavidState):
        """Handle tool approval system"""
        last_message = state["messages"][-1]
        
        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            return {"approval_status": "approved"}
        
        if not self.valves.enable_approval_system:
            return {"approval_status": "approved"}
        
        # Check tool safety
        dangerous_operations = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get('name', '')
            action = tool_call.get('args', {}).get('action', '')
            
            # High risk operations
            if self._is_dangerous_operation(tool_name, action, tool_call.get('args', {})):
                dangerous_operations.append(tool_call)
        
        if not dangerous_operations and self.valves.auto_approve_safe:
            return {"approval_status": "approved"}
        
        # Store for approval (simplified for now)
        approval_id = f"approval_{int(time.time())}"
        self.approval_queue[approval_id] = {
            "operations": dangerous_operations,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        return {"approval_status": "requires_approval", "approval_id": approval_id}

    def _is_dangerous_operation(self, tool_name: str, action: str, args: Dict[str, Any]) -> bool:
        """Check if operation is dangerous"""
        dangerous_patterns = [
            (tool_name == 'file_operations' and action in ['delete']),
            (tool_name == 'directory_operations' and action in ['delete']),
            (tool_name == 'process_management' and action in ['kill', 'start']),
            (tool_name == 'system_commands'),
            (tool_name == 'registry_operations' and action in ['write']),
            (tool_name == 'service_management' and action in ['start', 'stop', 'restart']),
        ]
        
        # Check path outside David directory
        for key, value in args.items():
            if key in ['path', 'source', 'destination'] and isinstance(value, str):
                if not self._is_safe_path(value):
                    return True
        
        return any(dangerous_patterns)

    def _is_safe_path(self, path: str) -> bool:
        """Check if path is within David's safe directory"""
        import os
        if not os.path.isabs(path):
            resolved = os.path.join("C:\\David", path)
        else:
            resolved = path
        return resolved.startswith("C:\\David")

    def _should_use_tools(self, state: DavidState):
        """Route based on approval status"""
        approval_status = state.get("approval_status", "")
        
        if approval_status == "requires_approval":
            return "rejected"  # Simplified - in full implementation, wait for approval
        
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls and approval_status == "approved":
            return "tools"
        return "__end__"

    def _tools_node(self, state: DavidState):
        """Execute approved tools"""
        from langgraph.prebuilt import ToolNode
        tool_node = ToolNode(DAVID_TOOLS_GROUPED)
        return tool_node.invoke(state)

    def _rejection_node(self, state: DavidState):
        """Handle rejected operations"""
        rejection_message = AIMessage(
            content="Operation requires approval. In a full deployment, this would wait for administrator approval."
        )
        return {"messages": [rejection_message], "approval_status": ""}

    async def emit_status(self, __event_emitter__, message: str, done: bool = False):
        """Emit status updates to Open WebUI"""
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {
                    "status": "complete" if done else "in_progress",
                    "description": message,
                    "done": done,
                },
            })

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[callable] = None
    ) -> Union[str, Generator]:
        """Main pipeline execution"""
        
        await self.emit_status(__event_emitter__, "David is thinking...", False)
        
        try:
            # Extract and convert messages
            messages = body.get("messages", [])
            langchain_messages = []
            
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))

            # Get session ID for persistence
            chat_id = body.get("metadata", {}).get("chat_id", str(uuid.uuid4()))
            thread_id = self._get_session_id(chat_id)
            config = {"configurable": {"thread_id": thread_id}}

            # Prepare David's state
            initial_state = {
                "messages": langchain_messages,
                "approval_status": "",
                "user_info": __user__.get("name", "Unknown") if __user__ else "Unknown",
                "session_id": thread_id
            }

            await self.emit_status(__event_emitter__, "Processing with David's tools", False)

            # Execute David's workflow
            if self.valves.enable_streaming:
                response_content = ""
                async for chunk in self.david_graph.astream(initial_state, config=config):
                    if chunk and "messages" in chunk:
                        last_msg = chunk["messages"][-1]
                        if isinstance(last_msg, AIMessage):
                            content = last_msg.content
                            if content != response_content:
                                response_content = content
                                yield content
            else:
                result = self.david_graph.invoke(initial_state, config=config)
                final_messages = result["messages"]
                if final_messages and isinstance(final_messages[-1], AIMessage):
                    yield final_messages[-1].content

            await self.emit_status(__event_emitter__, "David task completed", True)

        except Exception as e:
            error_msg = f"David encountered an error: {str(e)}"
            await self.emit_status(__event_emitter__, error_msg, True)
            yield f"Error: {error_msg}"

    def _get_session_id(self, chat_id: str) -> str:
        """Map OpenWebUI chat to David session"""
        if chat_id not in self.session_mapping:
            self.session_mapping[chat_id] = f"david_{chat_id}_{int(time.time())}"
        return self.session_mapping[chat_id]
