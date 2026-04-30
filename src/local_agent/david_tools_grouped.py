# C:\David\src\local_agent\david_tools_grouped.py
# Grouped David tools for reduced context usage

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

def resolve_path(path: str) -> str:
    """Resolve relative paths to C:\\David default"""
    if not os.path.isabs(path):
        return os.path.join("C:\\David", path)
    return path

# =============================================================================
# GROUPED TOOLS
# =============================================================================

@tool
def file_operations(action: str, path: str, content: str = None, destination: str = None, 
                   line_number: int = None, find: str = None, replace: str = None, 
                   permissions: str = None, algorithm: str = 'md5', regex: bool = False) -> str:
    """File operations: read, write, append, delete, copy, move, exists, info, edit_line, find_replace, permissions, search, hash"""
    try:
        resolved_path = resolve_path(path)
        
        if action == 'read':
            with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_read = f.read()
            return f"File content ({len(content_read)} chars):\n{content_read}"
            
        elif action == 'write':
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {resolved_path}"
            
        elif action == 'append':
            with open(resolved_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully appended {len(content)} characters to {resolved_path}"
            
        elif action == 'delete':
            os.remove(resolved_path)
            return f"Successfully deleted {resolved_path}"
            
        elif action == 'copy':
            resolved_dest = resolve_path(destination)
            os.makedirs(os.path.dirname(resolved_dest), exist_ok=True)
            shutil.copy2(resolved_path, resolved_dest)
            return f"Successfully copied {resolved_path} to {resolved_dest}"
            
        elif action == 'move':
            resolved_dest = resolve_path(destination)
            os.makedirs(os.path.dirname(resolved_dest), exist_ok=True)
            shutil.move(resolved_path, resolved_dest)
            return f"Successfully moved {resolved_path} to {resolved_dest}"
            
        elif action == 'exists':
            return f"File {resolved_path}: {'EXISTS' if os.path.exists(resolved_path) else 'DOES NOT EXIST'}"
            
        elif action == 'info':
            if not os.path.exists(resolved_path):
                return f"Path {resolved_path} does not exist"
            stat = os.stat(resolved_path)
            info = []
            info.append(f"Path: {resolved_path}")
            info.append(f"Size: {stat.st_size} bytes")
            info.append(f"Modified: {datetime.fromtimestamp(stat.st_mtime)}")
            info.append(f"Created: {datetime.fromtimestamp(stat.st_ctime)}")
            info.append(f"Type: {'File' if os.path.isfile(resolved_path) else 'Directory'}")
            return "\n".join(info)
            
        elif action == 'edit_line':
            with open(resolved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if line_number < 1 or line_number > len(lines):
                return f"Error: Line {line_number} out of range (1-{len(lines)})"
            lines[line_number - 1] = content + '\n'
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return f"Successfully edited line {line_number} in {resolved_path}"
            
        elif action == 'find_replace':
            with open(resolved_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            if regex:
                import re
                new_content = re.sub(find, replace, file_content)
            else:
                new_content = file_content.replace(find, replace)
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"Find/replace completed in {resolved_path}"
            
        elif action == 'permissions':
            if platform.system() == "Windows":
                subprocess.run(['icacls', resolved_path, '/grant', f'Everyone:{permissions}'], check=True)
            else:
                os.chmod(resolved_path, int(permissions, 8))
            return f"Permissions changed for {resolved_path}"
            
        elif action == 'search':
            import glob
            search_pattern = os.path.join(resolve_path(path), content)  # content as pattern
            matches = glob.glob(search_pattern, recursive=True)
            if not matches:
                return f"No files found matching '{content}' in {resolve_path(path)}"
            return f"Found {len(matches)} files:\n" + "\n".join(matches)
            
        elif action == 'hash':
            hash_obj = hashlib.new(algorithm)
            with open(resolved_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return f"{algorithm.upper()} hash of {resolved_path}: {hash_obj.hexdigest()}"
            
        else:
            return f"Unknown file action: {action}"
            
    except Exception as e:
        return f"Error in file operation '{action}': {str(e)}"

@tool
def directory_operations(action: str, path: str = ".", destination: str = None, 
                        pattern: str = None, max_depth: int = None, recursive: bool = False) -> str:
    """Directory operations: list, create, delete, copy, move, exists, size, find, tree, get_current, change"""
    try:
        resolved_path = resolve_path(path)
        
        if action == 'list':
            if not os.path.exists(resolved_path):
                return f"Directory {resolved_path} does not exist"
            items = []
            for item in sorted(os.listdir(resolved_path)):
                item_path = os.path.join(resolved_path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    try:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({size} bytes)")
                    except:
                        items.append(f"📄 {item}")
            if not items:
                return f"Directory {resolved_path} is empty"
            return f"Contents of {resolved_path}:\n" + "\n".join(items)
            
        elif action == 'create':
            os.makedirs(resolved_path, exist_ok=True)
            return f"Directory created: {resolved_path}"
            
        elif action == 'delete':
            if recursive:
                shutil.rmtree(resolved_path)
            else:
                os.rmdir(resolved_path)
            return f"Directory deleted: {resolved_path}"
            
        elif action == 'copy':
            resolved_dest = resolve_path(destination)
            shutil.copytree(resolved_path, resolved_dest)
            return f"Directory copied from {resolved_path} to {resolved_dest}"
            
        elif action == 'move':
            resolved_dest = resolve_path(destination)
            shutil.move(resolved_path, resolved_dest)
            return f"Directory moved from {resolved_path} to {resolved_dest}"
            
        elif action == 'exists':
            return f"Directory {resolved_path}: {'EXISTS' if os.path.isdir(resolved_path) else 'DOES NOT EXIST'}"
            
        elif action == 'size':
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(resolved_path)
                for filename in filenames
            )
            return f"Directory size of {resolved_path}: {total_size:,} bytes ({total_size / (1024**2):.2f} MB)"
            
        elif action == 'find':
            matches = []
            for dirpath, dirnames, filenames in os.walk(resolved_path):
                for dirname in dirnames:
                    if pattern.lower() in dirname.lower():
                        matches.append(os.path.join(dirpath, dirname))
            if not matches:
                return f"No directories found matching '{pattern}' in {resolved_path}"
            return f"Found {len(matches)} directories:\n" + "\n".join(matches)
            
        elif action == 'tree':
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
            
        elif action == 'get_current':
            return f"Current directory: {os.getcwd()}"
            
        elif action == 'change':
            os.chdir(resolved_path)
            return f"Changed directory to: {os.getcwd()}"
            
        else:
            return f"Unknown directory action: {action}"
            
    except Exception as e:
        return f"Error in directory operation '{action}': {str(e)}"

@tool
def process_management(action: str, pid_or_name: str = None, executable: str = None, 
                      args: str = None, working_dir: str = None) -> str:
    """Process operations: list, info, start, kill, exists"""
    try:
        if action == 'list':
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
                
        elif action == 'info':
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
                
        elif action == 'start':
            cmd = [executable]
            if args:
                cmd.extend(args.split())
            working_dir = resolve_path(working_dir) if working_dir else None
            proc = subprocess.Popen(cmd, cwd=working_dir)
            return f"Started process: {executable} (PID: {proc.pid})"
            
        elif action == 'kill':
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
                
        elif action == 'exists':
            if PSUTIL_AVAILABLE:
                exists = any(p.name().lower() == pid_or_name.lower() for p in psutil.process_iter())
                return f"Process '{pid_or_name}': {'RUNNING' if exists else 'NOT RUNNING'}"
            else:
                result = subprocess.run(['tasklist', '/fi', f'imagename eq {pid_or_name}'], capture_output=True, text=True)
                exists = pid_or_name.lower() in result.stdout.lower()
                return f"Process '{pid_or_name}': {'RUNNING' if exists else 'NOT RUNNING'}"
                
        else:
            return f"Unknown process action: {action}"
            
    except Exception as e:
        return f"Error in process operation '{action}': {str(e)}"

@tool
def network_operations(action: str, target: str, count: int = 4, options: str = '') -> str:
    """Network operations: ping, nslookup, traceroute, netstat, interfaces"""
    try:
        if action == 'ping':
            cmd = ['ping', '-n', str(count), target] if platform.system() == "Windows" else ['ping', '-c', str(count), target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return f"Ping results for {target}:\n{result.stdout}"
            
        elif action == 'nslookup':
            result = subprocess.run(['nslookup', target], capture_output=True, text=True, timeout=10)
            return f"DNS lookup for {target}:\n{result.stdout}"
            
        elif action == 'traceroute':
            cmd = ['tracert', target] if platform.system() == "Windows" else ['traceroute', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return f"Traceroute to {target}:\n{result.stdout}"
            
        elif action == 'netstat':
            cmd = ['netstat'] + options.split() if options else ['netstat']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return f"Network status:\n{result.stdout}"
            
        elif action == 'interfaces':
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
                
        else:
            return f"Unknown network action: {action}"
            
    except Exception as e:
        return f"Error in network operation '{action}': {str(e)}"

@tool
def system_commands(action: str, command: str, working_dir: str = ".", timeout: int = 30, 
                   code: str = None, file_path: str = None) -> str:
    """System command execution: execute, powershell, batch, python"""
    try:
        working_dir = resolve_path(working_dir)
        
        if action == 'execute':
            result = subprocess.run(
                command, shell=True, cwd=working_dir, timeout=timeout,
                capture_output=True, text=True
            )
            output = [f"Command: {command}", f"Exit code: {result.returncode}"]
            if result.stdout:
                output.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output.append(f"STDERR:\n{result.stderr}")
            return "\n".join(output)
            
        elif action == 'powershell':
            result = subprocess.run(
                ['powershell', '-Command', command],
                cwd=working_dir, timeout=timeout, capture_output=True, text=True
            )
            output = [f"PowerShell: {command}", f"Exit code: {result.returncode}"]
            if result.stdout:
                output.append(f"Output:\n{result.stdout}")
            if result.stderr:
                output.append(f"Error:\n{result.stderr}")
            return "\n".join(output)
            
        elif action == 'batch':
            result = subprocess.run(
                ['cmd', '/c', command],
                cwd=working_dir, timeout=timeout, capture_output=True, text=True
            )
            output = [f"Batch: {command}", f"Exit code: {result.returncode}"]
            if result.stdout:
                output.append(f"Output:\n{result.stdout}")
            if result.stderr:
                output.append(f"Error:\n{result.stderr}")
            return "\n".join(output)
            
        elif action == 'python':
            if file_path:
                resolved_path = resolve_path(file_path)
                if not os.path.exists(resolved_path):
                    return f"Python file {resolved_path} does not exist"
                result = subprocess.run(['python', resolved_path], timeout=timeout, capture_output=True, text=True)
            elif code:
                result = subprocess.run(['python', '-c', code], timeout=timeout, capture_output=True, text=True)
            else:
                return "Python execution requires either 'code' or 'file_path' parameter"
            
            output = [f"Python execution completed", f"Exit code: {result.returncode}"]
            if result.stdout:
                output.append(f"Output:\n{result.stdout}")
            if result.stderr:
                output.append(f"Error:\n{result.stderr}")
            return "\n".join(output)
            
        else:
            return f"Unknown system command action: {action}"
            
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error in system command '{action}': {str(e)}"

@tool
def hardware_info(action: str, drive: str = 'C:') -> str:
    """Hardware information: cpu_usage, memory_usage, disk_usage, disk_list"""
    try:
        if action == 'cpu_usage':
            if PSUTIL_AVAILABLE:
                usage = psutil.cpu_percent(interval=1)
                return f"CPU usage: {usage}%"
            else:
                return "CPU usage info requires psutil"
                
        elif action == 'memory_usage':
            if PSUTIL_AVAILABLE:
                mem = psutil.virtual_memory()
                return f"Memory: {mem.percent}% used ({mem.used // (1024**3)} GB / {mem.total // (1024**3)} GB)"
            else:
                return "Memory usage info requires psutil"
                
        elif action == 'disk_usage':
            if PSUTIL_AVAILABLE:
                usage = psutil.disk_usage(drive)
                return f"Disk {drive}: {usage.percent}% used ({usage.used // (1024**3)} GB / {usage.total // (1024**3)} GB)"
            else:
                usage = shutil.disk_usage(drive)
                return f"Disk {drive}: {usage.used // (1024**3)} GB used / {usage.total // (1024**3)} GB total"
                
        elif action == 'disk_list':
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
                
        else:
            return f"Unknown hardware action: {action}"
            
    except Exception as e:
        return f"Error getting hardware info '{action}': {str(e)}"

@tool
def registry_operations(action: str, key_path: str, value_name: str, value: str = None, value_type: str = 'REG_SZ') -> str:
    """Registry operations: read, write"""
    try:
        if not WINREG_AVAILABLE:
            return "Registry access requires Windows"
            
        if action == 'read':
            key_parts = key_path.split('\\', 1)
            hive = getattr(winreg, key_parts[0])
            subkey = key_parts[1] if len(key_parts) > 1 else ""
            
            with winreg.OpenKey(hive, subkey) as key:
                reg_value, _ = winreg.QueryValueEx(key, value_name)
                return f"Registry value {key_path}\\{value_name}: {reg_value}"
                
        elif action == 'write':
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
                
        else:
            return f"Unknown registry action: {action}"
            
    except Exception as e:
        return f"Error in registry operation '{action}': {str(e)}"

@tool
def ui_automation(action: str, file_path: str = None, x: int = None, y: int = None, 
                 text: str = None, keys: str = None) -> str:
    """UI automation: screenshot, click, type, key_combination, window_list"""
    try:
        if action == 'screenshot':
            if not PYAUTOGUI_AVAILABLE:
                return "Screenshot requires pyautogui"
            if not file_path:
                file_path = f"screenshot_{int(time.time())}.png"
            resolved_path = resolve_path(file_path)
            screenshot = pyautogui.screenshot()
            screenshot.save(resolved_path)
            return f"Screenshot saved to {resolved_path}"
            
        elif action == 'click':
            if not PYAUTOGUI_AVAILABLE:
                return "Mouse control requires pyautogui"
            pyautogui.click(x, y)
            return f"Clicked at coordinates ({x}, {y})"
            
        elif action == 'type':
            if not PYAUTOGUI_AVAILABLE:
                return "Text input requires pyautogui"
            pyautogui.typewrite(text)
            return f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}"
            
        elif action == 'key_combination':
            if not PYAUTOGUI_AVAILABLE:
                return "Key input requires pyautogui"
            key_list = [k.strip() for k in keys.split('+')]
            pyautogui.hotkey(*key_list)
            return f"Sent key combination: {keys}"
            
        elif action == 'window_list':
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist', '/fo', 'csv'], capture_output=True, text=True)
                return f"Open windows:\n{result.stdout}"
            else:
                return "Window list requires Windows"
                
        else:
            return f"Unknown UI action: {action}"
            
    except Exception as e:
        return f"Error in UI automation '{action}': {str(e)}"

@tool
def service_management(action: str, service_name: str) -> str:
    """Service management: list, status, start, stop, restart"""
    try:
        if action == 'list':
            result = subprocess.run(['sc', 'query'], capture_output=True, text=True)
            return f"Windows services:\n{result.stdout}"
            
        elif action == 'status':
            result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
            return f"Service {service_name} status:\n{result.stdout}"
            
        elif action == 'start':
            result = subprocess.run(['sc', 'start', service_name], capture_output=True, text=True)
            return f"Started service {service_name}:\n{result.stdout}"
            
        elif action == 'stop':
            result = subprocess.run(['sc', 'stop', service_name], capture_output=True, text=True)
            return f"Stopped service {service_name}:\n{result.stdout}"
            
        elif action == 'restart':
            stop_result = subprocess.run(['sc', 'stop', service_name], capture_output=True, text=True)
            time.sleep(2)
            start_result = subprocess.run(['sc', 'start', service_name], capture_output=True, text=True)
            return f"Restarted service {service_name}:\nStop: {stop_result.stdout}\nStart: {start_result.stdout}"
            
        else:
            return f"Unknown service action: {action}"
            
    except Exception as e:
        return f"Error in service management '{action}': {str(e)}"

@tool
def environment_management(action: str, name: str = None, value: str = None) -> str:
    """Environment and system management: list_vars, set_var, get_var, uptime, users, system_info"""
    try:
        if action == 'list_vars':
            env_vars = []
            for key, val in os.environ.items():
                env_vars.append(f"{key}={val}")
            return f"Environment variables ({len(env_vars)}):\n" + "\n".join(sorted(env_vars))
            
        elif action == 'set_var':
            os.environ[name] = value
            return f"Set environment variable {name}={value}"
            
        elif action == 'get_var':
            val = os.environ.get(name)
            return f"Environment variable {name}: {val if val else 'NOT SET'}"
            
        elif action == 'uptime':
            if PSUTIL_AVAILABLE:
                boot_time = psutil.boot_time()
                uptime = time.time() - boot_time
                days = int(uptime // 86400)
                hours = int((uptime % 86400) // 3600)
                minutes = int((uptime % 3600) // 60)
                return f"System uptime: {days} days, {hours} hours, {minutes} minutes"
            else:
                return "System uptime requires psutil"
                
        elif action == 'users':
            if PSUTIL_AVAILABLE:
                users = psutil.users()
                user_list = []
                for user in users:
                    user_list.append(f"{user.name} on {user.terminal} since {datetime.fromtimestamp(user.started)}")
                return f"Logged in users:\n" + "\n".join(user_list)
            else:
                result = subprocess.run(['query', 'user'], capture_output=True, text=True)
                return f"Logged in users:\n{result.stdout}"
                
        elif action == 'system_info':
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
            
        else:
            return f"Unknown environment action: {action}"
            
    except Exception as e:
        return f"Error in environment management '{action}': {str(e)}"

@tool
def programming_execution(action: str, code: str = None, file_path: str = None, 
                         class_name: str = None, timeout: int = 30) -> str:
    """Programming language execution: python, node, java"""
    try:
        if action == 'python':
            if file_path:
                resolved_path = resolve_path(file_path)
                if not os.path.exists(resolved_path):
                    return f"Python file {resolved_path} does not exist"
                result = subprocess.run(['python', resolved_path], timeout=timeout, capture_output=True, text=True)
            elif code:
                result = subprocess.run(['python', '-c', code], timeout=timeout, capture_output=True, text=True)
            else:
                return "Python execution requires either 'code' or 'file_path'"
            
        elif action == 'node':
            if file_path:
                resolved_path = resolve_path(file_path)
                if not os.path.exists(resolved_path):
                    return f"JavaScript file {resolved_path} does not exist"
                result = subprocess.run(['node', resolved_path], timeout=timeout, capture_output=True, text=True)
            elif code:
                result = subprocess.run(['node', '-e', code], timeout=timeout, capture_output=True, text=True)
            else:
                return "Node.js execution requires either 'code' or 'file_path'"
            
        elif action == 'java':
            if not file_path or not class_name:
                return "Java execution requires both 'file_path' and 'class_name'"
            resolved_path = resolve_path(file_path)
            if not os.path.exists(resolved_path):
                return f"Java file {resolved_path} does not exist"
            
            # Compile first
            compile_result = subprocess.run(['javac', resolved_path], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return f"Java compilation failed:\n{compile_result.stderr}"
            
            # Run
            result = subprocess.run(['java', class_name], timeout=timeout, capture_output=True, text=True)
            
        else:
            return f"Unknown programming action: {action}"
        
        output = [f"{action.title()} execution completed", f"Exit code: {result.returncode}"]
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Error:\n{result.stderr}")
        return "\n".join(output)
        
    except subprocess.TimeoutExpired:
        return f"{action.title()} execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error in {action} execution: {str(e)}"

@tool
def database_operations(action: str, db_path: str, query: str = None, table_name: str = None, schema: str = None) -> str:
    """Database operations: sqlite_query, sqlite_create_table"""
    try:
        resolved_path = resolve_path(db_path)
        
        if action == 'query':
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
            
        elif action == 'create_table':
            conn = sqlite3.connect(resolved_path)
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            conn.commit()
            conn.close()
            return f"Table '{table_name}' created in {resolved_path}"
            
        else:
            return f"Unknown database action: {action}"
            
    except Exception as e:
        return f"Error in database operation '{action}': {str(e)}"

@tool
def compression_operations(action: str, path: str, files: str = None, destination: str = None) -> str:
    """Compression operations: create_zip, extract_zip"""
    try:
        if action == 'create_zip':
            resolved_zip = resolve_path(path)
            file_list = files.split(',')
            
            with zipfile.ZipFile(resolved_zip, 'w') as zipf:
                for file in file_list:
                    file_path = resolve_path(file.strip())
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            return f"ZIP archive created: {resolved_zip} with {len(file_list)} files"
            
        elif action == 'extract_zip':
            resolved_zip = resolve_path(path)
            resolved_dest = resolve_path(destination)
            
            with zipfile.ZipFile(resolved_zip, 'r') as zipf:
                zipf.extractall(resolved_dest)
                file_count = len(zipf.namelist())
            
            return f"Extracted {file_count} files from {resolved_zip} to {resolved_dest}"
            
        else:
            return f"Unknown compression action: {action}"
            
    except Exception as e:
        return f"Error in compression operation '{action}': {str(e)}"

@tool
def monitoring_operations(action: str, duration: int = 60, log_type: str = 'system', count: int = 100) -> str:
    """System monitoring: monitor_cpu, monitor_memory, system_logs"""
    try:
        if action == 'monitor_cpu':
            if not PSUTIL_AVAILABLE:
                return "CPU monitoring requires psutil"
            samples = []
            for i in range(min(duration, 10)):  # Limit samples
                cpu_percent = psutil.cpu_percent(interval=1)
                samples.append(cpu_percent)
            avg_cpu = sum(samples) / len(samples)
            return f"CPU monitoring ({len(samples)} seconds): Average {avg_cpu:.1f}%, Peak {max(samples):.1f}%"
            
        elif action == 'monitor_memory':
            if not PSUTIL_AVAILABLE:
                return "Memory monitoring requires psutil"
            samples = []
            for i in range(min(duration // 10, 6)):  # Sample every 10 seconds
                mem = psutil.virtual_memory()
                samples.append(mem.percent)
                time.sleep(1)
            avg_mem = sum(samples) / len(samples)
            return f"Memory monitoring: Average {avg_mem:.1f}%, Peak {max(samples):.1f}%"
            
        elif action == 'system_logs':
            if platform.system() == "Windows":
                result = subprocess.run(['wevtutil', 'qe', log_type, '/c:' + str(count), '/f:text'], 
                                      capture_output=True, text=True)
                return f"System logs ({log_type}):\n{result.stdout[:5000]}"  # Limit output
            else:
                return "System logs require Windows Event Viewer"
                
        else:
            return f"Unknown monitoring action: {action}"
            
    except Exception as e:
        return f"Error in monitoring operation '{action}': {str(e)}"

@tool
def task_management(action: str, name: str = None, command: str = None, schedule: str = None) -> str:
    """Scheduled task management: list, create, delete"""
    try:
        if action == 'list':
            result = subprocess.run(['schtasks', '/query', '/fo', 'csv'], capture_output=True, text=True)
            return f"Scheduled tasks:\n{result.stdout[:5000]}"  # Limit output
            
        elif action == 'create':
            result = subprocess.run(['schtasks', '/create', '/tn', name, '/tr', command, '/sc', schedule], 
                                  capture_output=True, text=True)
            return f"Created scheduled task '{name}':\n{result.stdout}"
            
        elif action == 'delete':
            result = subprocess.run(['schtasks', '/delete', '/tn', name, '/f'], capture_output=True, text=True)
            return f"Deleted scheduled task '{name}':\n{result.stdout}"
            
        else:
            return f"Unknown task action: {action}"
            
    except Exception as e:
        return f"Error in task management '{action}': {str(e)}"

@tool
def windows_features(action: str) -> str:
    """Windows features: installed_programs, features, firewall_status"""
    try:
        if action == 'installed_programs':
            result = subprocess.run(['wmic', 'product', 'get', 'name,version', '/format:csv'], 
                                  capture_output=True, text=True)
            return f"Installed programs:\n{result.stdout[:5000]}"  # Limit output
            
        elif action == 'features':
            result = subprocess.run(['dism', '/online', '/get-features', '/format:table'], 
                                  capture_output=True, text=True)
            return f"Windows features:\n{result.stdout[:5000]}"  # Limit output
            
        elif action == 'firewall_status':
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                  capture_output=True, text=True)
            return f"Windows Firewall status:\n{result.stdout}"
            
        else:
            return f"Unknown Windows features action: {action}"
            
    except Exception as e:
        return f"Error getting Windows features '{action}': {str(e)}"

@tool
def get_status() -> dict:
    """Get David's status."""
    model = os.getenv("OLLAMA_MODEL", "qwen3:14b")
    return {
        "model_name": model,
        "temperature": 0.6,
        "context_window": 8192,
        "status": "operational",
        "tools_available": len(DAVID_TOOLS_GROUPED),
        "tool_grouping": "enabled"
    }

# Grouped tools list - 16 grouped tools instead of 82 individual tools
DAVID_TOOLS_GROUPED = [
    file_operations,
    directory_operations,
    process_management,
    network_operations,
    system_commands,
    hardware_info,
    registry_operations,
    ui_automation,
    service_management,
    environment_management,
    programming_execution,
    database_operations,
    compression_operations,
    monitoring_operations,
    task_management,
    windows_features,
    get_status
]
