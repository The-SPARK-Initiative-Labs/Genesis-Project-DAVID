from datetime import datetime
from pathlib import Path
import os

from src.local_agent.agent import session_histories

# Track which sessions already have files created
_session_files = {}

def log_conversation_summary(session_id: str, conversations_dir: str = "Conversations") -> None:
    """Log conversation to individual session file - one file per session.

    Creates ONE file per session and appends all messages to that same file.
    
    Args:
        session_id: The unique session identifier
        conversations_dir: Directory to store conversation files (default: "Conversations")
    """
    history = session_histories.get(session_id)
    if history is None:
        return

    # Update from LangGraph state before logging
    if hasattr(history, 'update_from_graph'):
        history.update_from_graph()

    # Create conversations directory if it doesn't exist
    conversations_path = Path(conversations_dir)
    conversations_path.mkdir(exist_ok=True)

    # Check if we already have a file for this session
    if session_id not in _session_files:
        # First time logging this session - create new file
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        short_session = session_id[:8]
        filename = f"{timestamp}_session-{short_session}.txt"
        file_path = conversations_path / filename
        _session_files[session_id] = file_path
        
        # Write session header
        with file_path.open("w", encoding="utf-8") as f:
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Started: {timestamp}\n")
            f.write("="*50 + "\n\n")
    else:
        # Use existing file for this session
        file_path = _session_files[session_id]

    # Append current conversation state (overwrite content section)
    lines = []
    for i, message in enumerate(history.messages, 1):
        # Handle both LangChain and LangGraph message types
        if hasattr(message, 'type'):
            role = "User" if message.type == "human" else "AI"
        elif hasattr(message, '__class__'):
            class_name = message.__class__.__name__
            if 'Human' in class_name:
                role = "User"
            elif 'AI' in class_name:
                role = "AI"
            else:
                role = "System"
        else:
            role = "Unknown"
            
        content = getattr(message, 'content', str(message))
        lines.append(f"[{i:03d}] {role}: {content}")
        lines.append("")

    # Read existing header and rewrite with updated conversation
    with file_path.open("r", encoding="utf-8") as f:
        header_lines = []
        for line in f:
            header_lines.append(line.rstrip())
            if line.strip() == "="*50:
                break
    
    # Write header + updated conversation
    with file_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(header_lines) + "\n\n")
        f.write(f"Messages: {len(history.messages)}\n")
        f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("\n".join(lines))

    # Also append to legacy log for backward compatibility
    legacy_log_path = Path("conversation_logs.txt")
    summary = " | ".join([f"{role}: {getattr(msg, 'content', str(msg))[:50]}..." 
                         for msg in history.messages[-1:]])  # Only last message
    timestamp_iso = datetime.utcnow().isoformat()
    log_entry = f"{timestamp_iso} - Session {session_id} - {summary}\n"

    with legacy_log_path.open("a", encoding="utf-8") as f:
        f.write(log_entry)
