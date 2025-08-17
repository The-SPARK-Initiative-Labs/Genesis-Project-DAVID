# MCP Tool Bridge - Convert existing MCP tools to LangChain tools
from langchain_core.tools import tool
from typing import Dict, Any
import asyncio

class MCPToolBridge:
    """Bridge between existing MCP tools and LangChain framework"""
    
    def __init__(self, mcp_client, guardian):
        self.mcp_client = mcp_client
        self.guardian = guardian

# LangChain tool wrappers for existing MCP functionality
@tool
async def read_file(path: str) -> str:
    """Read contents of a file"""
    import app
    guardian = app.guardian
    mcp_client = app.mcp_client
    
    # Use existing permission check - UNCHANGED
    if not await guardian.check_permission("read_file", {"path": path}):
        return "Permission denied - awaiting approval"
    
    try:
        # Use existing MCP call logic - UNCHANGED
        result = await mcp_client.call_tool("read_file", {"path": path})
        if "error" in result:
            return f"Error reading file: {result['error']}"
        return result.get("result", {}).get("content", "")
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def write_file(path: str, content: str) -> str:
    """Write content to a file (requires permission)"""
    from __main__ import guardian, mcp_client
    
    # Use existing permission check - UNCHANGED
    if not await guardian.check_permission("write_file", {"path": path, "content": content}):
        return "Permission denied - awaiting approval"
    
    try:
        result = await mcp_client.call_tool("write_file", {"path": path, "content": content})
        if "error" in result:
            return f"Error writing file: {result['error']}"
        return "File written successfully"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def list_directory(path: str) -> str:
    """List contents of a directory"""
    from __main__ import guardian, mcp_client
    
    # Use existing permission check - UNCHANGED
    if not await guardian.check_permission("list_directory", {"path": path}):
        return "Permission denied - awaiting approval"
    
    try:
        result = await mcp_client.call_tool("list_directory", {"path": path})
        if "error" in result:
            return f"Error listing directory: {result['error']}"
        
        # Use existing parsing logic - UNCHANGED
        if "result" in result:
            content = result["result"]
            
            if isinstance(content, dict) and "content" in content:
                if isinstance(content["content"], list) and len(content["content"]) > 0:
                    text_content = content["content"][0].get("text", "")
                    return text_content
                else:
                    return str(content["content"])
            elif "files" in content:
                files = content["files"]
                return "\n".join(files) if isinstance(files, list) else str(files)
            else:
                return str(content)
        
        return "No result returned"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def execute_command(command: str, working_directory: str = ".", timeout: int = 30) -> str:
    """Execute a system command (requires permission)"""
    from __main__ import guardian, mcp_client
    
    # Use existing permission check - UNCHANGED
    if not await guardian.check_permission("execute_command", {"command": command, "working_directory": working_directory, "timeout": timeout}):
        return "Permission denied - awaiting approval"
    
    try:
        result = await mcp_client.call_tool("execute_command", {
            "command": command,
            "working_directory": working_directory,
            "timeout": timeout
        })
        if "error" in result:
            return f"Error executing command: {result['error']}"
        return result.get("result", {}).get("output", "")
    except Exception as e:
        return f"Error: {str(e)}"

@tool
async def system_info(info_type: str = "all") -> str:
    """Get system information"""
    from __main__ import guardian, mcp_client
    
    # Use existing permission check - UNCHANGED
    if not await guardian.check_permission("system_info", {"info_type": info_type}):
        return "Permission denied - awaiting approval"
    
    try:
        result = await mcp_client.call_tool("system_info", {"type": info_type})
        if "error" in result:
            return f"Error getting system info: {result['error']}"
        
        # Use existing parsing logic - UNCHANGED
        if "result" in result:
            content = result["result"]
            
            if isinstance(content, dict) and "content" in content:
                if isinstance(content["content"], list) and len(content["content"]) > 0:
                    return content["content"][0].get("text", "")
                else:
                    return str(content["content"])
            elif isinstance(content, dict) and "info" in content:
                return content["info"]
            else:
                return str(content)
        
        return "No system info returned"
    except Exception as e:
        return f"Error: {str(e)}"

# All tools for LangGraph agent
ALL_LANGCHAIN_TOOLS = [read_file, write_file, list_directory, execute_command, system_info]
