import os
import sys
import types
import asyncio
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Provide a minimal stub for the chainlit module used by src.app
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
    """Minimal async context manager to simulate chainlit.Step"""

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

    async def stream_token(self, token):  # pragma: no cover - behaviour not tested
        pass


class DummyAsyncClient:
    """Mock of ollama.AsyncClient streaming preset responses per call."""

    responses = []

    def chat(self, model, messages, stream, options):
        tokens = list(self.responses.pop(0) if self.responses else [])

        class Response:
            def __init__(self, toks):
                self.toks = toks

            def __await__(self):
                async def _wrap():
                    return self
                return _wrap().__await__()

            def __aiter__(self):
                async def gen():  # pragma: no cover - behaviour not tested
                    for t in self.toks:
                        yield {"message": {"content": t}}
                return gen()

        return Response(tokens)

def test_direct_answer_exits_in_one_iteration(monkeypatch):
    # Patch chainlit.Step and ollama.AsyncClient
    monkeypatch.setattr(app, "cl", types.SimpleNamespace(Step=DummyStep))
    monkeypatch.setattr(app.ollama, "AsyncClient", DummyAsyncClient)

    DummyStep.calls = []
    DummyAsyncClient.responses = [["Paris is the capital of France."]]

    agent = ReActAgent()
    result = asyncio.run(agent._execute_react_loop("What is the capital of France?", []))

    assert result == "Paris is the capital of France."
    reasoning_cycles = [n for n in DummyStep.calls if n and n.startswith("Reasoning Cycle")]
    assert len(reasoning_cycles) == 1


def test_rejects_fake_observation(monkeypatch):
    monkeypatch.setattr(app, "cl", types.SimpleNamespace(Step=DummyStep))
    monkeypatch.setattr(app.ollama, "AsyncClient", DummyAsyncClient)

    DummyStep.calls = []
    DummyAsyncClient.responses = [
        ["Thought: check file\nAction: read_file\nAction Input: {\"path\": \"foo.txt\"}\nObservation: fake"],
        ["Final Answer: done"],
    ]

    agent = ReActAgent()
    result = asyncio.run(agent._execute_react_loop("Read file", []))

    assert result.strip() == "done"
    reasoning_cycles = [n for n in DummyStep.calls if n and n.startswith("Reasoning Cycle")]
    assert len(reasoning_cycles) == 2

