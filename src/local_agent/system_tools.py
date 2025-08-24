# C:\David\src\local_agent\system_tools.py
# Phase 3A: Core System Tools with Safety Wrappers

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

# Base workspace directory for file operations
WORKSPACE_DIR = Path("C:/David/workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)

def validate_path(path: str, create_dirs: bool = False) -> Path:
    """
    Validate and resolve file paths to prevent traversal attacks.
    
    Args:
        path: The file path to validate
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Path: Validated Path object within workspace
        
    Raises:
        PermissionError: If path escapes workspace directory
    """
    try:
        # Convert to Path object and resolve
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = WORKSPACE_DIR / path_obj
        
        resolved_path = path_obj.resolve()
        
        # Ensure path is within workspace
        if not str(resolved_path).startswith(str(WORKSPACE_DIR.resolve())):
            raise PermissionError(f"Path access denied: {path} (outside workspace)")
        
        # Create parent directories if requested
        if create_dirs:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
        return resolved_path
    except Exception as e:
        raise PermissionError(f"Invalid path: {path} - {str(e)}")

def create_backup(file_path: Path) -> Optional[str]:
    """Create backup of existing file before modification."""
    if file_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup_{timestamp}")
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
    return None

# FILE OPERATIONS
@tool
def read_file(path: str) -> str:
    """
    Read content from any file in the workspace.
    
    Args:
        path: Relative or absolute path to file
        
    Returns:
        str: File content
    """
    try:
        file_path = validate_path(path)
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"File content ({len(content)} characters):\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool  
def write_file(path: str, content: str) -> str:
    """
    Write content to file with automatic backup of existing files.
    
    Args:
        path: Relative or absolute path to file
        content: Content to write
        
    Returns:
        str: Success message with backup info
    """
    try:
        file_path = validate_path(path, create_dirs=True)
        
        # Create backup if file exists
        backup_info = ""
        if file_path.exists():
            backup_path = create_backup(file_path)
            backup_info = f" (backup: {backup_path})"
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {path}{backup_info}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def append_file(path: str, content: str) -> str:
    """
    Append content to existing file or create new file.
    
    Args:
        path: Relative or absolute path to file  
        content: Content to append
        
    Returns:
        str: Success message
    """
    try:
        file_path = validate_path(path, create_dirs=True)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully appended {len(content)} characters to {path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"

@tool
def list_directory(path: str = ".") -> str:
    """
    List contents of directory.
    
    Args:
        path: Directory path (default: current workspace)
        
    Returns:
        str: Directory listing
    """
    try:
        dir_path = validate_path(path)
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"
        
        if not dir_path.is_dir():
            return f"Error: Path is not a directory: {path}"
        
        items = []
        for item in sorted(dir_path.iterdir()):
            size = ""
            if item.is_file():
                size = f" ({item.stat().st_size} bytes)"
            items.append(f"{'📁' if item.is_dir() else '📄'} {item.name}{size}")
        
        if not items:
            return f"Directory {path} is empty"
        
        return f"Contents of {path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool
def create_directory(path: str) -> str:
    """
    Create new directory.
    
    Args:
        path: Directory path to create
        
    Returns:
        str: Success message
    """
    try:
        dir_path = validate_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@tool
def delete_file(path: str) -> str:
    """
    Delete file with automatic backup.
    
    Args:
        path: File path to delete
        
    Returns:
        str: Success message with backup info
    """
    try:
        file_path = validate_path(path)
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        # Create backup before deletion
        backup_path = create_backup(file_path)
        file_path.unlink()
        
        return f"File deleted: {path} (backup: {backup_path})"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

# SYSTEM OPERATIONS
@tool
def execute_command(command: str, working_dir: str = ".", timeout: int = 30) -> str:
    """
    Execute system command with safety checks and automatic blocking of destructive commands.
    
    Args:
        command: Command to execute
        working_dir: Working directory (default: current workspace)
        timeout: Timeout in seconds
        
    Returns:  
        str: Command output and execution details
    """
    try:
        # Block obviously destructive commands
        dangerous = [
            'rm -rf', 'del /s', 'del /q', 'rmdir /s', 'format', 'shutdown', 'reboot',
            'taskkill /f', 'net stop', 'sc delete', 'reg delete', 'attrib +h +s',
            'cipher /w:', 'sdelete', 'wipe', 'diskpart', 'fdisk'
        ]
        
        command_lower = command.lower()
        for danger in dangerous:
            if danger in command_lower:
                return f"⚠️ BLOCKED: Potentially destructive command '{danger}' detected.\nCommand: {command}\n\nUse execute_command_confirmed() if this is intentional."
        
        # Validate working directory
        work_path = validate_path(working_dir)
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(work_path),
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output_parts = [f"Command: {command}"]
        output_parts.append(f"Exit code: {result.returncode}")
        
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        
        return "\n".join(output_parts)
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool
def execute_command_confirmed(command: str, working_dir: str = ".", timeout: int = 30) -> str:
    """
    Execute system command WITHOUT safety blocks - use only when destructive commands are intentional.
    
    Args:
        command: Command to execute (no safety blocks)
        working_dir: Working directory 
        timeout: Timeout in seconds
        
    Returns:
        str: Command output and execution details
    """
    try:
        work_path = validate_path(working_dir)
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(work_path),
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output_parts = [f"⚠️ CONFIRMED Command: {command}"]
        output_parts.append(f"Exit code: {result.returncode}")
        
        if result.stdout:
            output_parts.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"STDERR:\n{result.stderr}")
        
        return "\n".join(output_parts)
        
    except subprocess.TimeoutExpired:
        return f"Error: Confirmed command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing confirmed command: {str(e)}"

@tool
def file_info(path: str) -> str:
    """
    Get detailed information about a file or directory.
    
    Args:
        path: Path to examine
        
    Returns:
        str: File metadata and properties
    """
    try:
        file_path = validate_path(path)
        if not file_path.exists():
            return f"Error: Path not found: {path}"
        
        stat = file_path.stat()
        info_parts = [f"Path: {path}"]
        info_parts.append(f"Type: {'Directory' if file_path.is_dir() else 'File'}")
        info_parts.append(f"Size: {stat.st_size} bytes")
        info_parts.append(f"Modified: {datetime.fromtimestamp(stat.st_mtime)}")
        info_parts.append(f"Created: {datetime.fromtimestamp(stat.st_ctime)}")
        info_parts.append(f"Permissions: {oct(stat.st_mode)[-3:]}")
        
        if file_path.is_file():
            info_parts.append(f"Extension: {file_path.suffix}")
        
        return "\n".join(info_parts)
    except Exception as e:
        return f"Error getting file info: {str(e)}"

# Export all system tools
SYSTEM_TOOLS = [
    read_file,
    write_file, 
    append_file,
    list_directory,
    create_directory,
    delete_file,
    execute_command,
    execute_command_confirmed,
    file_info
]
