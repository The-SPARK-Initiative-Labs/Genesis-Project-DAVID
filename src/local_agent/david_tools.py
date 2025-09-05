# C:\David\src\local_agent\david_tools.py
# David tools - handling missing dependencies gracefully

import os
import shutil
import subprocess
import hashlib
import zipfile
import sqlite3
import json
import platform
import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool

# Try importing optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# =============================================================================
# FILE OPERATIONS
# =============================================================================

def resolve_path(path: str) -> str:
    """Resolve relative paths to C:\\David default"""
    if not os.path.isabs(path):
        return os.path.join("C:\\David", path)
    return path

@tool
def read_file(path: str) -> str:
    """Read any file content."""
    try:
        resolved_path = resolve_path(path)
        with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return f"File content ({len(content)} chars):\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(path: str, content: str) -> str:
    """Write/overwrite file content."""
    try:
        resolved_path = resolve_path(path)
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {resolved_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def append_file(path: str, content: str) -> str:
    """Append to existing file."""
    try:
        resolved_path = resolve_path(path)
        with open(resolved_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully appended {len(content)} characters to {resolved_path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"

@tool
def delete_file(path: str) -> str:
    """Delete file."""
    try:
        resolved_path = resolve_path(path)
        os.remove(resolved_path)
        return f"Successfully deleted {resolved_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

@tool
def copy_file(source: str, destination: str) -> str:
    """Copy file."""
    try:
        resolved_source = resolve_path(source)
        resolved_dest = resolve_path(destination)
        os.makedirs(os.path.dirname(resolved_dest), exist_ok=True)
        shutil.copy2(resolved_source, resolved_dest)
        return f"Successfully copied {resolved_source} to {resolved_dest}"
    except Exception as e:
        return f"Error copying file: {str(e)}"

@tool
def move_file(source: str, destination: str) -> str:
    """Move/rename file."""
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(source, destination)
        return f"Successfully moved {source} to {destination}"
    except Exception as e:
        return f"Error moving file: {str(e)}"

@tool
def file_exists(path: str) -> str:
    """Check if file exists."""
    return f"File {path}: {'EXISTS' if os.path.exists(path) else 'DOES NOT EXIST'}"

@tool
def file_info(path: str) -> str:
    """Get file metadata."""
    try:
        if not os.path.exists(path):
            return f"Path {path} does not exist"
            
        stat = os.stat(path)
        info = []
        info.append(f"Path: {path}")
        info.append(f"Size: {stat.st_size} bytes")
        info.append(f"Modified: {datetime.fromtimestamp(stat.st_mtime)}")
        info.append(f"Created: {datetime.fromtimestamp(stat.st_ctime)}")
        info.append(f"Type: {'File' if os.path.isfile(path) else 'Directory'}")
        return "\n".join(info)
    except Exception as e:
        return f"Error getting file info: {str(e)}"

# =============================================================================
# DIRECTORY OPERATIONS
# =============================================================================

@tool
def list_directory(path: str = ".") -> str:
    """List directory contents."""
    try:
        resolved_path = resolve_path(path)
        if not os.path.exists(resolved_path):
            return f"Directory {resolved_path} does not exist"
            
        items = []
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                try:
                    size = os.path.getsize(item_path)
                    items.append(f"📄 {item} ({size} bytes)")
                except:
                    items.append(f"📄 {item}")
        
        if not items:
            return f"Directory {path} is empty"
        return f"Contents of {path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@tool
def create_directory(path: str) -> str:
    """Create directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@tool
def delete_directory(path: str, recursive: bool = False) -> str:
    """Delete directory."""
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        return f"Directory deleted: {path}"
    except Exception as e:
        return f"Error deleting directory: {str(e)}"

@tool
def get_current_directory() -> str:
    """Get current working directory."""
    return f"Current directory: {os.getcwd()}"

@tool
def change_directory(path: str) -> str:
    """Change working directory."""
    try:
        os.chdir(path)
        return f"Changed directory to: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

# =============================================================================
# SYSTEM COMMANDS
# =============================================================================

@tool
def execute_command(command: str, working_dir: str = ".", timeout: int = 30) -> str:
    """Execute system command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output = [f"Command: {command}", f"Exit code: {result.returncode}"]
        
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
            
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool
def python_execute(code: str, file_path: str = "", timeout: int = 30) -> str:
    """Execute Python code."""
    try:
        if file_path:
            if not os.path.exists(file_path):
                return f"Python file {file_path} does not exist"
            result = subprocess.run(
                ["python", file_path],
                timeout=timeout,
                capture_output=True,
                text=True
            )
        else:
            result = subprocess.run(
                ["python", "-c", code],
                timeout=timeout,
                capture_output=True,
                text=True
            )
        
        output = [f"Python execution completed", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        
        return "\n".join(output)
    except subprocess.TimeoutExpired:
        return f"Python execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing Python: {str(e)}"

@tool
def system_info() -> str:
    """Get system information."""
    try:
        info = []
        info.append(f"System: {platform.system()}")
        info.append(f"Release: {platform.release()}")
        info.append(f"Version: {platform.version()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Python version: {platform.python_version()}")
        
        if PSUTIL_AVAILABLE:
            info.append(f"CPU cores: {psutil.cpu_count()}")
            memory = psutil.virtual_memory()
            info.append(f"Memory: {memory.total // (1024**3)} GB total, {memory.available // (1024**3)} GB available")
        
        return "\n".join(info)
    except Exception as e:
        return f"Error getting system info: {str(e)}"

# Basic status check tool
@tool
def get_status() -> dict:
    """Get David's status."""
    model = os.getenv("OLLAMA_MODEL", "qwen3:14b")
    return {
        "model_name": model,
        "temperature": 0.6,
        "context_window": 8192,
        "status": "operational",
        "tools_available": len(DAVID_TOOLS)
    }

# =============================================================================
# ADDITIONAL FILE OPERATIONS
# =============================================================================

@tool
def edit_line(path: str, line_number: int, new_content: str) -> str:
    """Edit specific line in file."""
    try:
        resolved_path = resolve_path(path)
        with open(resolved_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if line_number < 1 or line_number > len(lines):
            return f"Error: Line {line_number} out of range (1-{len(lines)})"
        
        lines[line_number - 1] = new_content + '\n'
        
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return f"Successfully edited line {line_number} in {resolved_path}"
    except Exception as e:
        return f"Error editing line: {str(e)}"

@tool
def find_replace(path: str, find: str, replace: str, regex: bool = False) -> str:
    """Find and replace text in file."""
    try:
        resolved_path = resolve_path(path)
        with open(resolved_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if regex:
            import re
            new_content = re.sub(find, replace, content)
        else:
            new_content = content.replace(find, replace)
        
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Find/replace completed in {resolved_path}"
    except Exception as e:
        return f"Error in find/replace: {str(e)}"

@tool
def file_permissions(path: str, permissions: str) -> str:
    """Change file permissions (Windows)."""
    try:
        resolved_path = resolve_path(path)
        if platform.system() == "Windows":
            subprocess.run(['icacls', resolved_path, '/grant', f'Everyone:{permissions}'], check=True)
            return f"Permissions changed for {resolved_path}"
        else:
            os.chmod(resolved_path, int(permissions, 8))
            return f"Permissions changed for {resolved_path}"
    except Exception as e:
        return f"Error changing permissions: {str(e)}"

@tool
def file_search(directory: str, pattern: str) -> str:
    """Search for files by pattern."""
    try:
        resolved_dir = resolve_path(directory)
        import glob
        search_pattern = os.path.join(resolved_dir, pattern)
        matches = glob.glob(search_pattern, recursive=True)
        
        if not matches:
            return f"No files found matching '{pattern}' in {resolved_dir}"
        
        return f"Found {len(matches)} files:\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching files: {str(e)}"

@tool
def file_hash(path: str, algorithm: str = 'md5') -> str:
    """Generate file hash."""
    try:
        resolved_path = resolve_path(path)
        hash_obj = hashlib.new(algorithm)
        
        with open(resolved_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return f"{algorithm.upper()} hash of {resolved_path}: {hash_obj.hexdigest()}"
    except Exception as e:
        return f"Error generating hash: {str(e)}"

# =============================================================================
# ADDITIONAL DIRECTORY OPERATIONS
# =============================================================================

@tool
def copy_directory(source: str, destination: str) -> str:
    """Copy entire directory."""
    try:
        resolved_source = resolve_path(source)
        resolved_dest = resolve_path(destination)
        shutil.copytree(resolved_source, resolved_dest)
        return f"Directory copied from {resolved_source} to {resolved_dest}"
    except Exception as e:
        return f"Error copying directory: {str(e)}"

@tool
def move_directory(source: str, destination: str) -> str:
    """Move directory."""
    try:
        resolved_source = resolve_path(source)
        resolved_dest = resolve_path(destination)
        shutil.move(resolved_source, resolved_dest)
        return f"Directory moved from {resolved_source} to {resolved_dest}"
    except Exception as e:
        return f"Error moving directory: {str(e)}"

@tool
def directory_exists(path: str) -> str:
    """Check if directory exists."""
    resolved_path = resolve_path(path)
    return f"Directory {resolved_path}: {'EXISTS' if os.path.isdir(resolved_path) else 'DOES NOT EXIST'}"

@tool
def directory_size(path: str) -> str:
    """Calculate directory size."""
    try:
        resolved_path = resolve_path(path)
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(resolved_path)
            for filename in filenames
        )
        return f"Directory size of {resolved_path}: {total_size:,} bytes ({total_size / (1024**2):.2f} MB)"
    except Exception as e:
        return f"Error calculating directory size: {str(e)}"

@tool
def find_directories(root: str, pattern: str) -> str:
    """Find directories by pattern."""
    try:
        resolved_root = resolve_path(root)
        matches = []
        for dirpath, dirnames, filenames in os.walk(resolved_root):
            for dirname in dirnames:
                if pattern.lower() in dirname.lower():
                    matches.append(os.path.join(dirpath, dirname))
        
        if not matches:
            return f"No directories found matching '{pattern}' in {resolved_root}"
        
        return f"Found {len(matches)} directories:\n" + "\n".join(matches)
    except Exception as e:
        return f"Error finding directories: {str(e)}"

@tool
def directory_tree(path: str, max_depth: int = None) -> str:
    """Get directory tree structure."""
    try:
        resolved_path = resolve_path(path)
        tree_lines = []
        
        for root, dirs, files in os.walk(resolved_path):
            level = root.replace(resolved_path, '').count(os.sep)
            if max_depth and level >= max_depth:
                dirs.clear()
                continue
            
            indent = ' ' * 2 * level
            tree_lines.append(f"{indent}{os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                tree_lines.append(f"{subindent}{file}")
        
        return f"Directory tree of {resolved_path}:\n" + "\n".join(tree_lines)
    except Exception as e:
        return f"Error generating directory tree: {str(e)}"

# This will be defined at the end
DAVID_TOOLS = []

# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================

@tool
def list_processes() -> str:
    """List all running processes."""
    try:
        if PSUTIL_AVAILABLE:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(f"PID {proc.info['pid']}: {proc.info['name']} (CPU: {proc.info['cpu_percent']:.1f}%, MEM: {proc.info['memory_percent']:.1f}%)")
                except:
                    continue
            return f"Running processes ({len(processes)}):\n" + "\n".join(processes[:50])
        else:
            result = subprocess.run(['tasklist'], capture_output=True, text=True)
            return f"Process list:\n{result.stdout}"
    except Exception as e:
        return f"Error listing processes: {str(e)}"

@tool
def process_info(pid_or_name: str) -> str:
    """Get detailed process information."""
    try:
        if PSUTIL_AVAILABLE:
            if pid_or_name.isdigit():
                proc = psutil.Process(int(pid_or_name))
            else:
                procs = [p for p in psutil.process_iter() if p.name().lower() == pid_or_name.lower()]
                if not procs:
                    return f"Process '{pid_or_name}' not found"
                proc = procs[0]
            
            info = []
            info.append(f"PID: {proc.pid}")
            info.append(f"Name: {proc.name()}")
            info.append(f"CPU: {proc.cpu_percent()}%")
            info.append(f"Memory: {proc.memory_percent():.2f}%")
            info.append(f"Status: {proc.status()}")
            return "\n".join(info)
        else:
            return f"Process info for {pid_or_name} (requires psutil)"
    except Exception as e:
        return f"Error getting process info: {str(e)}"

@tool
def start_process(executable: str, args: str = None, working_dir: str = None) -> str:
    """Start new process."""
    try:
        cmd = [executable]
        if args:
            cmd.extend(args.split())
        
        working_dir = resolve_path(working_dir) if working_dir else None
        
        proc = subprocess.Popen(cmd, cwd=working_dir)
        return f"Started process: {executable} (PID: {proc.pid})"
    except Exception as e:
        return f"Error starting process: {str(e)}"

@tool
def kill_process(pid_or_name: str) -> str:
    """Terminate process."""
    try:
        if PSUTIL_AVAILABLE:
            if pid_or_name.isdigit():
                proc = psutil.Process(int(pid_or_name))
                proc.terminate()
                return f"Terminated process PID {pid_or_name}"
            else:
                killed = 0
                for proc in psutil.process_iter():
                    if proc.name().lower() == pid_or_name.lower():
                        proc.terminate()
                        killed += 1
                return f"Terminated {killed} processes named '{pid_or_name}'"
        else:
            subprocess.run(['taskkill', '/f', '/im', pid_or_name], check=True)
            return f"Terminated process: {pid_or_name}"
    except Exception as e:
        return f"Error killing process: {str(e)}"

@tool
def process_exists(name: str) -> str:
    """Check if process is running."""
    try:
        if PSUTIL_AVAILABLE:
            exists = any(p.name().lower() == name.lower() for p in psutil.process_iter())
            return f"Process '{name}': {'RUNNING' if exists else 'NOT RUNNING'}"
        else:
            result = subprocess.run(['tasklist', '/fi', f'imagename eq {name}'], capture_output=True, text=True)
            exists = name.lower() in result.stdout.lower()
            return f"Process '{name}': {'RUNNING' if exists else 'NOT RUNNING'}"
    except Exception as e:
        return f"Error checking process: {str(e)}"

# =============================================================================
# NETWORK OPERATIONS
# =============================================================================

@tool
def ping_host(target: str, count: int = 4) -> str:
    """Ping network host."""
    try:
        cmd = ['ping', '-n', str(count), target] if platform.system() == "Windows" else ['ping', '-c', str(count), target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return f"Ping results for {target}:\n{result.stdout}"
    except Exception as e:
        return f"Error pinging host: {str(e)}"

@tool
def nslookup(hostname: str) -> str:
    """DNS lookup."""
    try:
        result = subprocess.run(['nslookup', hostname], capture_output=True, text=True, timeout=10)
        return f"DNS lookup for {hostname}:\n{result.stdout}"
    except Exception as e:
        return f"Error in DNS lookup: {str(e)}"

@tool
def traceroute(target: str) -> str:
    """Trace network route."""
    try:
        cmd = ['tracert', target] if platform.system() == "Windows" else ['traceroute', target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return f"Traceroute to {target}:\n{result.stdout}"
    except Exception as e:
        return f"Error in traceroute: {str(e)}"

@tool
def netstat(options: str = '') -> str:
    """Network connection status."""
    try:
        cmd = ['netstat'] + options.split() if options else ['netstat']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return f"Network status:\n{result.stdout}"
    except Exception as e:
        return f"Error getting network status: {str(e)}"

@tool
def network_interfaces() -> str:
    """List network interfaces."""
    try:
        if PSUTIL_AVAILABLE:
            interfaces = psutil.net_if_addrs()
            info = []
            for interface, addrs in interfaces.items():
                info.append(f"Interface: {interface}")
                for addr in addrs:
                    info.append(f"  {addr.family.name}: {addr.address}")
            return "\n".join(info)
        else:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            return f"Network interfaces:\n{result.stdout}"
    except Exception as e:
        return f"Error getting network interfaces: {str(e)}"

# =============================================================================
# SYSTEM COMMANDS
# =============================================================================

@tool
def execute_powershell(script: str, working_dir: str = '.', timeout: int = 30) -> str:
    """Run PowerShell commands."""
    try:
        working_dir = resolve_path(working_dir)
        result = subprocess.run(
            ['powershell', '-Command', script],
            cwd=working_dir,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output = [f"PowerShell: {script}", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error executing PowerShell: {str(e)}"

@tool
def execute_batch(script: str, working_dir: str = '.', timeout: int = 30) -> str:
    """Run batch scripts."""
    try:
        working_dir = resolve_path(working_dir)
        result = subprocess.run(
            ['cmd', '/c', script],
            cwd=working_dir,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output = [f"Batch: {script}", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error executing batch: {str(e)}"

# =============================================================================
# HARDWARE ACCESS
# =============================================================================

@tool
def cpu_usage() -> str:
    """Get CPU usage percentage."""
    try:
        if PSUTIL_AVAILABLE:
            usage = psutil.cpu_percent(interval=1)
            return f"CPU usage: {usage}%"
        else:
            return "CPU usage info requires psutil"
    except Exception as e:
        return f"Error getting CPU usage: {str(e)}"

@tool
def memory_usage() -> str:
    """Get RAM usage information."""
    try:
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            return f"Memory: {mem.percent}% used ({mem.used // (1024**3)} GB / {mem.total // (1024**3)} GB)"
        else:
            return "Memory usage info requires psutil"
    except Exception as e:
        return f"Error getting memory usage: {str(e)}"

@tool
def disk_usage(drive: str = 'C:') -> str:
    """Get disk space information."""
    try:
        if PSUTIL_AVAILABLE:
            usage = psutil.disk_usage(drive)
            return f"Disk {drive}: {usage.percent}% used ({usage.used // (1024**3)} GB / {usage.total // (1024**3)} GB)"
        else:
            usage = shutil.disk_usage(drive)
            return f"Disk {drive}: {usage.used // (1024**3)} GB used / {usage.total // (1024**3)} GB total"
    except Exception as e:
        return f"Error getting disk usage: {str(e)}"

@tool
def disk_list() -> str:
    """List all disk drives."""
    try:
        if PSUTIL_AVAILABLE:
            partitions = psutil.disk_partitions()
            drives = []
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drives.append(f"{partition.device} ({partition.fstype}) - {usage.percent}% used")
                except:
                    drives.append(f"{partition.device} ({partition.fstype}) - unavailable")
            return "Disk drives:\n" + "\n".join(drives)
        else:
            return "Disk list requires psutil"
    except Exception as e:
        return f"Error listing disks: {str(e)}"

# =============================================================================
# REGISTRY ACCESS (Windows)
# =============================================================================

@tool
def registry_read(key_path: str, value_name: str) -> str:
    """Read registry value."""
    try:
        if not WINREG_AVAILABLE:
            return "Registry access requires Windows"
        
        key_parts = key_path.split('\\', 1)
        hive = getattr(winreg, key_parts[0])
        subkey = key_parts[1] if len(key_parts) > 1 else ""
        
        with winreg.OpenKey(hive, subkey) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return f"Registry value {key_path}\\{value_name}: {value}"
    except Exception as e:
        return f"Error reading registry: {str(e)}"

@tool
def registry_write(key_path: str, value_name: str, value: str, value_type: str) -> str:
    """Write registry value."""
    try:
        if not WINREG_AVAILABLE:
            return "Registry access requires Windows"
        
        key_parts = key_path.split('\\', 1)
        hive = getattr(winreg, key_parts[0])
        subkey = key_parts[1] if len(key_parts) > 1 else ""
        
        type_map = {
            'REG_SZ': winreg.REG_SZ,
            'REG_DWORD': winreg.REG_DWORD,
            'REG_BINARY': winreg.REG_BINARY
        }
        reg_type = type_map.get(value_type, winreg.REG_SZ)
        
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)
            return f"Registry value written: {key_path}\\{value_name}"
    except Exception as e:
        return f"Error writing registry: {str(e)}"

# =============================================================================
# USER INTERFACE AUTOMATION
# =============================================================================

@tool
def screenshot(file_path: str = None) -> str:
    """Take screenshot."""
    try:
        if not PYAUTOGUI_AVAILABLE:
            return "Screenshot requires pyautogui"
        
        if not file_path:
            file_path = f"screenshot_{int(time.time())}.png"
        
        resolved_path = resolve_path(file_path)
        screenshot = pyautogui.screenshot()
        screenshot.save(resolved_path)
        return f"Screenshot saved to {resolved_path}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

@tool
def click_coordinates(x: int, y: int) -> str:
    """Click at specific coordinates."""
    try:
        if not PYAUTOGUI_AVAILABLE:
            return "Mouse control requires pyautogui"
        
        pyautogui.click(x, y)
        return f"Clicked at coordinates ({x}, {y})"
    except Exception as e:
        return f"Error clicking: {str(e)}"

@tool
def type_text(text: str) -> str:
    """Type text at current cursor."""
    try:
        if not PYAUTOGUI_AVAILABLE:
            return "Text input requires pyautogui"
        
        pyautogui.typewrite(text)
        return f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}"
    except Exception as e:
        return f"Error typing text: {str(e)}"

@tool
def key_combination(keys: str) -> str:
    """Send key combinations (Ctrl+C, etc.)."""
    try:
        if not PYAUTOGUI_AVAILABLE:
            return "Key input requires pyautogui"
        
        key_list = [k.strip() for k in keys.split('+')]
        pyautogui.hotkey(*key_list)
        return f"Sent key combination: {keys}"
    except Exception as e:
        return f"Error sending keys: {str(e)}"

@tool
def window_list() -> str:
    """List open windows."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True)
            return f"Open windows:\n{result.stdout}"
        else:
            return "Window list requires Windows"
    except Exception as e:
        return f"Error listing windows: {str(e)}"

# =============================================================================
# SERVICE MANAGEMENT (Windows)
# =============================================================================

@tool
def list_services() -> str:
    """List Windows services."""
    try:
        result = subprocess.run(['sc', 'query'], capture_output=True, text=True)
        return f"Windows services:\n{result.stdout}"
    except Exception as e:
        return f"Error listing services: {str(e)}"

@tool
def service_status(service_name: str) -> str:
    """Get service status."""
    try:
        result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
        return f"Service {service_name} status:\n{result.stdout}"
    except Exception as e:
        return f"Error getting service status: {str(e)}"

@tool
def start_service(service_name: str) -> str:
    """Start Windows service."""
    try:
        result = subprocess.run(['sc', 'start', service_name], capture_output=True, text=True)
        return f"Started service {service_name}:\n{result.stdout}"
    except Exception as e:
        return f"Error starting service: {str(e)}"

@tool
def stop_service(service_name: str) -> str:
    """Stop Windows service."""
    try:
        result = subprocess.run(['sc', 'stop', service_name], capture_output=True, text=True)
        return f"Stopped service {service_name}:\n{result.stdout}"
    except Exception as e:
        return f"Error stopping service: {str(e)}"

@tool
def restart_service(service_name: str) -> str:
    """Restart Windows service."""
    try:
        stop_result = subprocess.run(['sc', 'stop', service_name], capture_output=True, text=True)
        time.sleep(2)
        start_result = subprocess.run(['sc', 'start', service_name], capture_output=True, text=True)
        return f"Restarted service {service_name}:\nStop: {stop_result.stdout}\nStart: {start_result.stdout}"
    except Exception as e:
        return f"Error restarting service: {str(e)}"

# =============================================================================
# ENVIRONMENT & SYSTEM
# =============================================================================

@tool
def environment_variables() -> str:
    """List environment variables."""
    try:
        env_vars = []
        for key, value in os.environ.items():
            env_vars.append(f"{key}={value}")
        return f"Environment variables ({len(env_vars)}):\n" + "\n".join(sorted(env_vars))
    except Exception as e:
        return f"Error listing environment variables: {str(e)}"

@tool
def set_environment_variable(name: str, value: str) -> str:
    """Set environment variable."""
    try:
        os.environ[name] = value
        return f"Set environment variable {name}={value}"
    except Exception as e:
        return f"Error setting environment variable: {str(e)}"

@tool
def get_environment_variable(name: str) -> str:
    """Get environment variable."""
    try:
        value = os.environ.get(name)
        return f"Environment variable {name}: {value if value else 'NOT SET'}"
    except Exception as e:
        return f"Error getting environment variable: {str(e)}"

@tool
def system_uptime() -> str:
    """Get system uptime."""
    try:
        if PSUTIL_AVAILABLE:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            return f"System uptime: {days} days, {hours} hours, {minutes} minutes"
        else:
            return "System uptime requires psutil"
    except Exception as e:
        return f"Error getting system uptime: {str(e)}"

@tool
def logged_in_users() -> str:
    """List logged in users."""
    try:
        if PSUTIL_AVAILABLE:
            users = psutil.users()
            user_list = []
            for user in users:
                user_list.append(f"{user.name} on {user.terminal} since {datetime.fromtimestamp(user.started)}")
            return f"Logged in users:\n" + "\n".join(user_list)
        else:
            result = subprocess.run(['query', 'user'], capture_output=True, text=True)
            return f"Logged in users:\n{result.stdout}"
    except Exception as e:
        return f"Error getting logged in users: {str(e)}"

# =============================================================================
# PROGRAMMING LANGUAGE EXECUTION
# =============================================================================

@tool
def node_execute(code: str, file_path: str = '') -> str:
    """Execute JavaScript/Node.js."""
    try:
        if file_path:
            resolved_path = resolve_path(file_path)
            if not os.path.exists(resolved_path):
                return f"JavaScript file {resolved_path} does not exist"
            result = subprocess.run(['node', resolved_path], timeout=30, capture_output=True, text=True)
        else:
            result = subprocess.run(['node', '-e', code], timeout=30, capture_output=True, text=True)
        
        output = [f"Node.js execution completed", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error executing Node.js: {str(e)}"

@tool
def java_execute(file_path: str, class_name: str) -> str:
    """Execute Java programs."""
    try:
        resolved_path = resolve_path(file_path)
        if not os.path.exists(resolved_path):
            return f"Java file {resolved_path} does not exist"
        
        # Compile first
        compile_result = subprocess.run(['javac', resolved_path], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return f"Java compilation failed:\n{compile_result.stderr}"
        
        # Run
        result = subprocess.run(['java', class_name], timeout=30, capture_output=True, text=True)
        
        output = [f"Java execution completed", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Error executing Java: {str(e)}"

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

@tool
def sqlite_query(db_path: str, query: str) -> str:
    """Execute SQLite queries."""
    try:
        resolved_path = resolve_path(db_path)
        conn = sqlite3.connect(resolved_path)
        cursor = conn.cursor()
        
        cursor.execute(query)
        
        if query.strip().lower().startswith('select'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            output = [f"Query results ({len(results)} rows):"]
            output.append("Columns: " + ", ".join(columns))
            for row in results[:50]:  # Limit output
                output.append(str(row))
        else:
            conn.commit()
            output = [f"Query executed successfully"]
            if cursor.rowcount >= 0:
                output.append(f"Rows affected: {cursor.rowcount}")
        
        conn.close()
        return "\n".join(output)
    except Exception as e:
        return f"Error executing SQLite query: {str(e)}"

@tool
def sqlite_create_table(db_path: str, table_name: str, schema: str) -> str:
    """Create SQLite table."""
    try:
        resolved_path = resolve_path(db_path)
        conn = sqlite3.connect(resolved_path)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
        conn.commit()
        conn.close()
        
        return f"Table '{table_name}' created in {resolved_path}"
    except Exception as e:
        return f"Error creating SQLite table: {str(e)}"

# Tools will be defined at end

# =============================================================================
# COMPRESSION & ARCHIVES
# =============================================================================

@tool
def create_zip(files: str, zip_path: str) -> str:
    """Create ZIP archive."""
    try:
        resolved_zip = resolve_path(zip_path)
        file_list = files.split(',')
        
        with zipfile.ZipFile(resolved_zip, 'w') as zipf:
            for file in file_list:
                file_path = resolve_path(file.strip())
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
        
        return f"ZIP archive created: {resolved_zip} with {len(file_list)} files"
    except Exception as e:
        return f"Error creating ZIP: {str(e)}"

@tool
def extract_zip(zip_path: str, destination: str) -> str:
    """Extract ZIP archive."""
    try:
        resolved_zip = resolve_path(zip_path)
        resolved_dest = resolve_path(destination)
        
        with zipfile.ZipFile(resolved_zip, 'r') as zipf:
            zipf.extractall(resolved_dest)
            file_count = len(zipf.namelist())
        
        return f"Extracted {file_count} files from {resolved_zip} to {resolved_dest}"
    except Exception as e:
        return f"Error extracting ZIP: {str(e)}"

# =============================================================================
# SYSTEM MONITORING
# =============================================================================

@tool
def monitor_cpu(duration: int = 60) -> str:
    """Monitor CPU usage over time."""
    try:
        if not PSUTIL_AVAILABLE:
            return "CPU monitoring requires psutil"
        
        samples = []
        for i in range(min(duration, 10)):  # Limit samples
            cpu_percent = psutil.cpu_percent(interval=1)
            samples.append(cpu_percent)
        
        avg_cpu = sum(samples) / len(samples)
        return f"CPU monitoring ({len(samples)} seconds): Average {avg_cpu:.1f}%, Peak {max(samples):.1f}%"
    except Exception as e:
        return f"Error monitoring CPU: {str(e)}"

@tool
def monitor_memory(duration: int = 60) -> str:
    """Monitor memory usage over time."""
    try:
        if not PSUTIL_AVAILABLE:
            return "Memory monitoring requires psutil"
        
        samples = []
        for i in range(min(duration // 10, 6)):  # Sample every 10 seconds
            mem = psutil.virtual_memory()
            samples.append(mem.percent)
            time.sleep(1)
        
        avg_mem = sum(samples) / len(samples)
        return f"Memory monitoring: Average {avg_mem:.1f}%, Peak {max(samples):.1f}%"
    except Exception as e:
        return f"Error monitoring memory: {str(e)}"

@tool
def system_logs(log_type: str = 'system', count: int = 100) -> str:
    """Read system logs."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['wevtutil', 'qe', log_type, '/c:' + str(count), '/f:text'], 
                                  capture_output=True, text=True)
            return f"System logs ({log_type}):\n{result.stdout[:5000]}"  # Limit output
        else:
            return "System logs require Windows Event Viewer"
    except Exception as e:
        return f"Error reading system logs: {str(e)}"

# =============================================================================
# SCHEDULED TASKS
# =============================================================================

@tool
def list_scheduled_tasks() -> str:
    """List Windows scheduled tasks."""
    try:
        result = subprocess.run(['schtasks', '/query', '/fo', 'csv'], capture_output=True, text=True)
        return f"Scheduled tasks:\n{result.stdout[:5000]}"  # Limit output
    except Exception as e:
        return f"Error listing scheduled tasks: {str(e)}"

@tool
def create_scheduled_task(name: str, command: str, schedule: str) -> str:
    """Create scheduled task."""
    try:
        result = subprocess.run(['schtasks', '/create', '/tn', name, '/tr', command, '/sc', schedule], 
                              capture_output=True, text=True)
        return f"Created scheduled task '{name}':\n{result.stdout}"
    except Exception as e:
        return f"Error creating scheduled task: {str(e)}"

@tool
def delete_scheduled_task(name: str) -> str:
    """Delete scheduled task."""
    try:
        result = subprocess.run(['schtasks', '/delete', '/tn', name, '/f'], capture_output=True, text=True)
        return f"Deleted scheduled task '{name}':\n{result.stdout}"
    except Exception as e:
        return f"Error deleting scheduled task: {str(e)}"

# =============================================================================
# WINDOWS-SPECIFIC FEATURES
# =============================================================================

@tool
def installed_programs() -> str:
    """List installed programs."""
    try:
        result = subprocess.run(['wmic', 'product', 'get', 'name,version', '/format:csv'], 
                              capture_output=True, text=True)
        return f"Installed programs:\n{result.stdout[:5000]}"  # Limit output
    except Exception as e:
        return f"Error listing installed programs: {str(e)}"

@tool
def windows_features() -> str:
    """List Windows features."""
    try:
        result = subprocess.run(['dism', '/online', '/get-features', '/format:table'], 
                              capture_output=True, text=True)
        return f"Windows features:\n{result.stdout[:5000]}"  # Limit output
    except Exception as e:
        return f"Error listing Windows features: {str(e)}"

@tool
def windows_firewall_status() -> str:
    """Get Windows Firewall status."""
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                              capture_output=True, text=True)
        return f"Windows Firewall status:\n{result.stdout}"
    except Exception as e:
        return f"Error getting firewall status: {str(e)}"

# Complete tool list - all 82 implemented tools
DAVID_TOOLS = [
    # File operations (13)
    read_file, write_file, append_file, delete_file, copy_file, move_file, 
    file_exists, file_info, edit_line, find_replace, file_permissions, 
    file_search, file_hash,
    
    # Directory operations (11)
    list_directory, create_directory, delete_directory, copy_directory,
    move_directory, directory_exists, directory_size, find_directories,
    directory_tree, get_current_directory, change_directory,
    
    # System operations (4)
    execute_command, python_execute, system_info, get_status,
    
    # Process management (5)
    list_processes, process_info, start_process, kill_process, process_exists,
    
    # Network operations (5)
    ping_host, nslookup, traceroute, netstat, network_interfaces,
    
    # System commands (2)
    execute_powershell, execute_batch,
    
    # Hardware access (4)
    cpu_usage, memory_usage, disk_usage, disk_list,
    
    # Registry access (2)
    registry_read, registry_write,
    
    # UI automation (5)
    screenshot, click_coordinates, type_text, key_combination, window_list,
    
    # Service management (5)
    list_services, service_status, start_service, stop_service, restart_service,
    
    # Environment & system (5)
    environment_variables, set_environment_variable, get_environment_variable,
    system_uptime, logged_in_users,
    
    # Programming languages (2)
    node_execute, java_execute,
    
    # Database operations (2)
    sqlite_query, sqlite_create_table,
    
    # Compression & archives (2)
    create_zip, extract_zip,
    
    # System monitoring (3)
    monitor_cpu, monitor_memory, system_logs,
    
    # Scheduled tasks (3)
    list_scheduled_tasks, create_scheduled_task, delete_scheduled_task,
    
    # Windows-specific features (3)
    installed_programs, windows_features, windows_firewall_status,
]
