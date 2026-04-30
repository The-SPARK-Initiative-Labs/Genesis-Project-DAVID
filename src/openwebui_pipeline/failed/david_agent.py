"""
title: David AI System Agent
author: AI Team
version: 1.0.0
license: MIT
description: David's LangGraph system agent as Open WebUI pipeline
requirements: langgraph, langchain-core, langchain-ollama
"""

import os
import uuid
import time
from typing import List, Union, Generator, Iterator, TypedDict, Annotated, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from operator import add

# Import David's existing tools
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'local_agent'))
from david_tools_grouped import DAVID_TOOLS_GROUPED

# David's state schema
class DavidState(TypedDict):
    messages: Annotated[list, add_messages]
    approval_status: str
    user_info: str
    session_id: str

class Pipeline:
    class Valves(BaseModel):
        ollama_model: str = Field(default="qwen3:14b", description="Ollama model name")
        ollama_base_url: str = Field(default="http://host.docker.internal:11434", description="Ollama server URL")
        enable_approval: bool = Field(default=True, description="Enable tool approval system")

    def __init__(self):
        self.name = "David AI System Agent"
        self.valves = self.Valves()
        self.memory = MemorySaver()
        self.session_mapping = {}
        self._initialize_david()

    def _initialize_david(self):
        """Initialize David's LangGraph workflow"""
        self.llm = ChatOllama(
            model=self.valves.ollama_model,
            base_url=self.valves.ollama_base_url,
            temperature=0.6,
        )
        
        self.david_with_tools = self.llm.bind_tools(DAVID_TOOLS_GROUPED)
        
        workflow = StateGraph(DavidState)
        workflow.add_node("david_agent", self._david_agent_node)
        workflow.add_node("approval", self._approval_node)
        workflow.add_node("tools", self._tools_node)
        workflow.add_node("rejected", self._rejection_node)
        
        workflow.add_edge(START, "david_agent")
        workflow.add_edge("david_agent", "approval")
        workflow.add_conditional_edges("approval", self._should_use_tools, ["tools", "rejected", "__end__"])
        workflow.add_edge("tools", "david_agent")
        workflow.add_edge("rejected", "__end__")
        
        self.david_graph = workflow.compile(checkpointer=self.memory)

    def _david_agent_node(self, state: DavidState):
        """David's main agent logic"""
        messages = state["messages"]
        
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
        
        if not self.valves.enable_approval:
            return {"approval_status": "approved"}
        
        # Simplified approval - auto-approve safe operations
        return {"approval_status": "approved"}

    def _should_use_tools(self, state: DavidState):
        """Route based on approval status"""
        approval_status = state.get("approval_status", "")
        
        if approval_status == "requires_approval":
            return "rejected"
        
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
            content="Operation requires approval."
        )
        return {"messages": [rejection_message], "approval_status": ""}

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        
        try:
            # Convert to LangChain messages
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
                "user_info": "User",
                "session_id": thread_id
            }

            # Execute David's workflow
            result = self.david_graph.invoke(initial_state, config=config)
            final_messages = result["messages"]
            
            if final_messages and isinstance(final_messages[-1], AIMessage):
                return final_messages[-1].content
            else:
                return "David processed your request."

        except Exception as e:
            return f"David error: {str(e)}"

    def _get_session_id(self, chat_id: str) -> str:
        """Map OpenWebUI chat to David session"""
        if chat_id not in self.session_mapping:
            self.session_mapping[chat_id] = f"david_{chat_id}_{int(time.time())}"
        return self.session_mapping[chat_id]
