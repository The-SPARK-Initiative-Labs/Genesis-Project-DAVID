import sys
sys.path.append('src')
from local_agent.agent import status_check

class DummyLLM:
    def __init__(self):
        self.model = "dummy-model"
        self.temperature = 0.5
        self.num_ctx = 1024

dummy = DummyLLM()
result = status_check(dummy)
expected = {
    "model_name": "dummy-model",
    "temperature": 0.5,
    "context_window": 1024,
}

if result == expected:
    print("Test passed!")
else:
    print("Test failed")
    print("Got:", result)
    print("Expected:", expected)
