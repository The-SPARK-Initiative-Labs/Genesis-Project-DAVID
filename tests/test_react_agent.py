import sys
import types
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

# Stub external dependencies
class DummyStep:
    def __init__(self, *args, **kwargs):
        self.input = None
        self.output = None
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def stream_token(self, token):
        pass

class DummyMessage:
    def __init__(self, content=""):
        self.content = content
    async def send(self):
        pass

class DummyUserSession(dict):
    def set(self, key, value):
        self[key] = value
    def get(self, key, default=None):
        return super().get(key, default)

def _decorator(func):
    return func

sys.modules['chainlit'] = types.SimpleNamespace(
    Step=DummyStep,
    Message=DummyMessage,
    user_session=DummyUserSession(),
    on_chat_start=_decorator,
    on_message=_decorator,
    on_stop=_decorator,
)

class DummyAsyncClient:
    async def chat(self, *args, **kwargs):
        yield {"message": {"content": ""}}

sys.modules['ollama'] = types.SimpleNamespace(AsyncClient=lambda: DummyAsyncClient())

from app import ReActAgent


def test_simple_query_bypasses_react():
    agent = ReActAgent()
    assert agent._needs_react_reasoning("What tools do you have available?") is False


def test_complex_query_triggers_react():
    agent = ReActAgent()
    query = "Can you analyze and compare the sizes of files in the directory?"
    assert agent._needs_react_reasoning(query) is True
