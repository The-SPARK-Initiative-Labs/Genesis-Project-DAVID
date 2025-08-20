from src.local_agent.agent import status_check


class DummyLLM:
    def __init__(self):
        self.model = "dummy-model"
        self.temperature = 0.5
        self.num_ctx = 1024


def test_status_check_with_llm_instance():
    dummy = DummyLLM()
    cfg = status_check(dummy)
    assert cfg == {
        "model_name": "dummy-model",
        "temperature": 0.5,
        "context_window": 1024,
    }

