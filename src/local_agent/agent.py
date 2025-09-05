# C:\David\src\local_agent\agent.py
# Simple David with approval system - no consciousness complexity

import os
from typing import Annotated, Literal, Dict, List, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from .david_tools import DAVID_TOOLS

# Global checkpointer for memory persistence
checkpointer = MemorySaver()

# Simple system prompt
SIMPLE_PROMPT = """You are David, an AI assistant that helps Ben with coding and system tasks. 

You have tools available for file operations, system commands, code execution, and more.
Be helpful, direct, and use tools when needed to accomplish tasks."""

# Simple state - just messages and approval status
class DavidState(TypedDict):
    messages: Annotated[list, add_messages]
    approval_status: str

# Tool Definitions
@tool
def get_status() -> dict:
    """Return David's current configuration and status."""
    model = os.getenv("OLLAMA_MODEL", "qwen3:14b")
    return {
        "model_name": model,
        "temperature": 0.6,
        "context_window": 8192,
        "status": "operational"
    }

@tool  
def david_memory_check(query: str = "") -> str:
    """Check David's memory or conversation context."""
    return f"Memory system operational. Context query: {query if query else 'general status'}"

# Available tools for David  
david_tools = [get_status, david_memory_check] + DAVID_TOOLS
tool_node = ToolNode(david_tools)

def create_agent_executor():
    """Create simple David with approval system."""
    
    # Initialize LLM
    model_name = os.getenv("OLLAMA_MODEL", "qwen3:14b")
    llm = ChatOllama(
        model=model_name,
        temperature=0.6,
        top_p=0.95,
        top_k=20,
        num_ctx=8192,
    )
    
    # Bind tools to LLM
    david_with_tools = llm.bind_tools(david_tools)
    
    def david_agent(state: DavidState):
        """Simple David agent with tools."""
        messages = state["messages"]
        
        # Add system prompt if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SIMPLE_PROMPT)] + messages
        
        response = david_with_tools.invoke(messages)
        return {"messages": [response]}

    async def approval_node(state: DavidState):
        """Check if operations need approval and get human consent for dangerous operations"""
        print("🔍 APPROVAL NODE CALLED - CHECKING TOOLS")  # DEBUG
        last_message = state["messages"][-1]
        
        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            return {"approval_status": "approved"}  # No tools to approve
        
        def resolve_path(path: str) -> str:
            """Resolve relative paths to C:\David default"""
            import os
            if not os.path.isabs(path):
                return os.path.join("C:\\David", path)
            return path
        
        def is_outside_david_dir(path: str) -> bool:
            """Check if resolved path is outside C:\David"""
            resolved = resolve_path(path)
            return not resolved.startswith("C:\\David")
        
        # Check each tool call for danger level and location
        dangerous_operations = []
        medium_risk_operations = []
        outside_david_operations = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get('name', '')
            
            # Check if operation involves paths outside C:\David
            if 'args' in tool_call:
                for key, value in tool_call['args'].items():
                    if key in ['path', 'source', 'destination', 'working_dir'] and isinstance(value, str):
                        if is_outside_david_dir(value):
                            outside_david_operations.append((tool_call, key, value))
            
            # High risk operations
            if tool_name in ['delete_file', 'execute_command', 'execute_command_confirmed', 
                           'kill_process', 'start_process', 'execute_powershell', 'execute_batch',
                           'delete_directory', 'registry_write', 'start_service', 'stop_service',
                           'restart_service', 'set_environment_variable', 'click_coordinates',
                           'type_text', 'key_combination', 'create_scheduled_task', 
                           'delete_scheduled_task']:
                dangerous_operations.append(tool_call)
            # Medium risk operations 
            elif tool_name in ['write_file', 'append_file', 'edit_line', 'find_replace',
                             'file_permissions', 'copy_file', 'move_file', 'copy_directory',
                             'move_directory', 'screenshot', 'sqlite_query', 'sqlite_create_table',
                             'create_zip', 'extract_zip']:
                medium_risk_operations.append(tool_call)
        
        # Auto-approve safe operations within C:\David
        if not dangerous_operations and not medium_risk_operations and not outside_david_operations:
            return {"approval_status": "approved"}
        
        # Print details and request approval
        print("\n" + "="*50)
        print("🚨 APPROVAL REQUIRED 🚨")
        print("="*50)
        
        if outside_david_operations:
            print("OPERATIONS OUTSIDE C:\\DAVID:")
            for tool_call, key, value in outside_david_operations:
                resolved = resolve_path(value)
                print(f"  • {tool_call.get('name', 'unknown')}")
                print(f"    {key}: {value} → {resolved}")
            print()
        
        if dangerous_operations:
            print("HIGH RISK OPERATIONS:")
            for tool_call in dangerous_operations:
                print(f"  • {tool_call.get('name', 'unknown')}")
                if 'args' in tool_call:
                    for key, value in tool_call['args'].items():
                        if isinstance(value, str) and key in ['path', 'source', 'destination']:
                            resolved = resolve_path(value)
                            print(f"    {key}: {value} → {resolved}")
                        else:
                            print(f"    {key}: {value}")
                print()
        
        if medium_risk_operations:
            print("MEDIUM RISK OPERATIONS:")
            for tool_call in medium_risk_operations:
                print(f"  • {tool_call.get('name', 'unknown')}")
                if 'args' in tool_call:
                    for key, value in tool_call['args'].items():
                        if isinstance(value, str) and key in ['path', 'source', 'destination']:
                            resolved = resolve_path(value)
                            print(f"    {key}: {value} → {resolved}")
                        else:
                            print(f"    {key}: {value}")
                print()
        
        print("="*50)
        
        # Use Chainlit for UI approval
        import chainlit as cl
        
        try:
            # Build approval message
            approval_details = []
            if outside_david_operations:
                approval_details.append("**OPERATIONS OUTSIDE C:\\DAVID:**")
                for tool_call, key, value in outside_david_operations:
                    resolved = resolve_path(value)
                    approval_details.append(f"• {tool_call.get('name', 'unknown')}: {key} = {value} → {resolved}")
            
            if dangerous_operations:
                approval_details.append("**HIGH RISK OPERATIONS:**")
                for tool_call in dangerous_operations:
                    tool_name = tool_call.get('name', 'unknown')
                    if 'args' in tool_call:
                        args_text = []
                        for key, value in tool_call['args'].items():
                            if isinstance(value, str) and key in ['path', 'source', 'destination', 'command']:
                                resolved = resolve_path(value) if key != 'command' else value
                                args_text.append(f"{key}: {resolved}")
                            else:
                                args_text.append(f"{key}: {value}")
                        approval_details.append(f"• **{tool_name}** - {', '.join(args_text)}")
                    else:
                        approval_details.append(f"• **{tool_name}**")
            
            if medium_risk_operations:
                approval_details.append("**MEDIUM RISK OPERATIONS:**")
                for tool_call in medium_risk_operations:
                    tool_name = tool_call.get('name', 'unknown')
                    if 'args' in tool_call:
                        args_text = []
                        for key, value in tool_call['args'].items():
                            if isinstance(value, str) and key in ['path', 'source', 'destination']:
                                resolved = resolve_path(value)
                                args_text.append(f"{key}: {resolved}")
                            else:
                                args_text.append(f"{key}: {value}")
                        approval_details.append(f"• **{tool_name}** - {', '.join(args_text)}")
                    else:
                        approval_details.append(f"• **{tool_name}**")
            
            approval_message = "⚠️ **APPROVAL REQUIRED** ⚠️\n\n" + "\n".join(approval_details) + "\n\n**Approve these operations?**"
            
            # Get approval via UI
            response = await cl.AskUserMessage(
                content=approval_message,
                timeout=60
            ).send()
            
            if response and response.get('output'):
                user_input = response['output'].strip().lower()
                if user_input in ['y', 'yes']:
                    print("✅ Operations APPROVED")
                    return {"approval_status": "approved"}
                else:
                    print("❌ Operations REJECTED")
                    return {"approval_status": "rejected"}
            else:
                print("❌ Operations REJECTED (no response)")
                return {"approval_status": "rejected"}
                
        except Exception as e:
            print(f"❌ Operations REJECTED (error: {e})")
            return {"approval_status": "rejected"}

    def should_use_tools(state: DavidState) -> Literal["tools", "rejected", "__end__"]:
        """Route based on approval status and tool calls"""
        approval_status = state.get("approval_status", "")
        
        if approval_status == "rejected":
            return "rejected"
        
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls and approval_status == "approved":
            return "tools"
        return "__end__"
    
    def rejection_node(state: DavidState):
        """Handle rejected operations"""
        rejection_message = AIMessage(content="I understand. The requested operation has been rejected for safety reasons. Is there anything else I can help you with?")
        return {"messages": [rejection_message], "approval_status": ""}

    # Build simple workflow with approval
    workflow = StateGraph(DavidState)
    workflow.add_node("agent", david_agent)
    workflow.add_node("approval", approval_node)
    workflow.add_node("rejected", rejection_node)
    workflow.add_node("tools", tool_node)

    # Simple flow: START → agent → approval → [tools OR rejected OR end]
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", "approval")
    workflow.add_conditional_edges("approval", should_use_tools, ["tools", "rejected", "__end__"])
    workflow.add_edge("tools", "agent")
    workflow.add_edge("rejected", "__end__")

    # Compile with memory
    david_graph = workflow.compile(checkpointer=checkpointer)
    
    return david_graph, llm

# Legacy compatibility functions for conversation_logger
class LegacySessionHistory:
    """Wrapper to maintain compatibility with existing conversation logger."""
    def __init__(self, graph, session_id):
        self.graph = graph
        self.session_id = session_id
        self.messages = []
    
    def update_from_graph(self):
        """Update messages from LangGraph state."""
        try:
            config = {"configurable": {"thread_id": self.session_id}}
            # Get the current state
            state = self.graph.get_state(config)
            if state and state.values.get("messages"):
                self.messages = state.values["messages"]
        except Exception:
            # If we can't get state, keep existing messages
            pass

# Global storage for compatibility
session_histories = {}

def get_or_create_session_history(session_id: str, graph):
    """Get or create session history for compatibility."""
    if session_id not in session_histories:
        session_histories[session_id] = LegacySessionHistory(graph, session_id)
    else:
        session_histories[session_id].update_from_graph()
    return session_histories[session_id]
