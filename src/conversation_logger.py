from datetime import datetime
from pathlib import Path

from src.local_agent.agent import session_histories


def log_conversation_summary(session_id: str, file_path: str = "conversation_logs.txt") -> None:
    """Append a simple summary of the conversation to ``file_path``.

    The summary lists all messages in the conversation so far. Each call will
    write the current state of the conversation for ``session_id``.
    
    Updated for LangGraph compatibility while maintaining same functionality.
    """
    history = session_histories.get(session_id)
    if history is None:
        return

    # Update from LangGraph state before logging
    if hasattr(history, 'update_from_graph'):
        history.update_from_graph()

    lines = []
    for message in history.messages:
        # Handle both old LangChain messages and new LangGraph messages
        if hasattr(message, 'type'):
            role = "User" if message.type == "human" else "AI"
        elif hasattr(message, '__class__'):
            # LangGraph message types
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
        lines.append(f"{role}: {content}")

    summary = " | ".join(lines)
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"{timestamp} - Session {session_id} - {summary}\n"

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(log_entry)
