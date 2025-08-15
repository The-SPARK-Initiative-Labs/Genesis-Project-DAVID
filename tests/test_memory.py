import os
import sys
import types
import re
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

sys.modules.setdefault(
    "chainlit",
    types.SimpleNamespace(
        Step=None,
        on_chat_start=lambda f: f,
        on_message=lambda f: f,
        on_stop=lambda f: f,
        Message=type("Message", (), {}),
    ),
)
sys.modules.setdefault("ollama", types.SimpleNamespace(AsyncClient=None))

import src.app as app
from src.app import ReActAgent


class DummyStep:
    calls = []
    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type
        self.input = None
        self.output = None
    async def __aenter__(self):
        DummyStep.calls.append(self.name)
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def stream_token(self, token):
        pass

class MemoryAsyncClient:
    def chat(self, model, messages, stream, options):
        number = None
        for m in messages:
            match = re.search(r"\b\d+\b", m.get("content", ""))
            if match:
                number = match.group(0)
        token = f"The number you gave me was {number}." if number else "I don't remember any number."
        tokens = [token]
        class Response:
            def __init__(self, toks):
                self.toks = toks
            def __await__(self):
                async def _wrap():
                    return self
                return _wrap().__await__()
            def __aiter__(self):
                async def gen():
                    for t in self.toks:
                        yield {"message": {"content": t}}
                return gen()
        return Response(tokens)

class ForgetfulAsyncClient:
    def chat(self, model, messages, stream, options):
        tokens = ["I don't remember any number."]
        class Response:
            def __init__(self, toks):
                self.toks = toks
            def __await__(self):
                async def _wrap():
                    return self
                return _wrap().__await__()
            def __aiter__(self):
                async def gen():
                    for t in self.toks:
                        yield {"message": {"content": t}}
                return gen()
        return Response(tokens)


def test_recalls_number(monkeypatch):
    monkeypatch.setattr(app, "cl", types.SimpleNamespace(Step=DummyStep))
    monkeypatch.setattr(app.ollama, "AsyncClient", MemoryAsyncClient)
    messages = [
        {"role": "user", "content": "Remember 7890"},
        {"role": "assistant", "content": "I'll remember 7890"},
    ]
    agent = ReActAgent()
    result = asyncio.run(agent._execute_react_loop("What number did I tell you?", messages))
    assert "7890" in result


def test_refuses_memory_loss(monkeypatch):
    monkeypatch.setattr(app, "cl", types.SimpleNamespace(Step=DummyStep))
    monkeypatch.setattr(app.ollama, "AsyncClient", ForgetfulAsyncClient)
    messages = [
        {"role": "user", "content": "Remember 55"},
    ]
    agent = ReActAgent()
    result = asyncio.run(agent._execute_react_loop("What number did I tell you?", messages))
    assert "cannot claim memory loss" in result.lower()
