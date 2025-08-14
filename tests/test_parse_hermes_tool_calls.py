import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

# Stub external dependencies required by app module
sys.modules.setdefault(
    'chainlit',
    types.SimpleNamespace(
        Step=None,
        on_chat_start=lambda f: f,
        on_message=lambda f: f,
        on_stop=lambda f: f,
        Message=None,
        user_session=None,
    ),
)
sys.modules.setdefault('ollama', types.SimpleNamespace(AsyncClient=None))

from app import parse_hermes_tool_calls


def test_parse_action_fallback():
    response = (
        'Thought: consider file\n'
        'Action: read_file\n'
        'Action Input: {"path": "foo.txt"}\n'
    )
    tool_calls = parse_hermes_tool_calls(response)
    assert tool_calls == [{"name": "read_file", "arguments": {"path": "foo.txt"}}]
