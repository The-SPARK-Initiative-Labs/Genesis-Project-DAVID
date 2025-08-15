import sys
import types
import asyncio
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
    assert agent._needs_react_reasoning("What tools do you have?") is False


def test_long_simple_query_bypasses_react():
    agent = ReActAgent()
    query = "I am curious about the tools you have in this environment today"
    assert agent._needs_react_reasoning(query) is False


def test_complex_query_triggers_react():
    agent = ReActAgent()
    query = "Can you analyze and compare the sizes of files in the directory?"
    assert agent._needs_react_reasoning(query) is True


def test_random_number_query_bypasses_react_loop(monkeypatch):
    agent = ReActAgent()

    called = {"simple": False, "react": False}

    async def fake_execute(query, messages):
        called["react"] = True
        return "react"

    async def fake_simple(query, messages):
        called["simple"] = True
        return "simple"

    monkeypatch.setattr(agent, "_execute_react_loop", fake_execute)
    monkeypatch.setattr(agent, "_simple_response", fake_simple)

    result = asyncio.run(agent.process_with_react("Give me a random number", []))

    assert result == "simple"
    assert called["react"] is False
    assert called["simple"] is True
