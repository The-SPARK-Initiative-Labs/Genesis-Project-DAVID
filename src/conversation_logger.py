from datetime import datetime
from pathlib import Path

from src.local_agent.agent import session_histories


def log_conversation_summary(session_id: str, file_path: str = "conversation_logs.txt") -> None:
    """Append a simple summary of the conversation to ``file_path``.

    The summary lists all messages in the conversation so far. Each call will
    write the current state of the conversation for ``session_id``.
    """
    history = session_histories.get(session_id)
    if history is None:
        return

    lines = []
    for message in history.messages:
        role = "User" if message.type == "human" else "AI"
        lines.append(f"{role}: {message.content}")

    summary = " | ".join(lines)
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"{timestamp} - Session {session_id} - {summary}\n"

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(log_entry)
