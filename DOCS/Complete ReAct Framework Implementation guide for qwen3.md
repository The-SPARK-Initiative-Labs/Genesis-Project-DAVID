# Complete ReAct Framework Implementation Guide

## qwen3-14b requires Hermes-style templates, not traditional ReAct

The research reveals that **qwen3-14b performs best with Hermes-style tool calling** rather than traditional ReAct prompting. The official Qwen documentation explicitly warns against using stopword-based ReAct patterns because the model's thinking mode can output stopwords unexpectedly, breaking tool call parsing.

### Optimal prompt template for qwen3-14b

```xml
<|im_start|>system
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.

<tools>
[
  {
    "type": "function",
    "function": {
      "name": "search_web",
      "description": "Search the internet for information",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
      }
    }
  }
]
</tools>

For each function call, return a json object within <tool_call></tool_call> XML tags:
<tool_call>
{"name": "function_name", "arguments": {"arg1": "value1"}}
</tool_call>
<|im_end|>
```

Deploy qwen3-14b with these optimized sampling parameters:
```python
sampling_params = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "repetition_penalty": 1.05,
    "max_tokens": 8192,
    "presence_penalty": 1.5  # Reduces repetition issues
}
```

## Streaming ReAct parsing with state machines

Ollama's streaming responses require sophisticated parsing to extract ReAct components in real-time. The most robust approach uses a finite state machine that tracks parsing context across streaming chunks.

### Production-ready streaming parser

```python
import re
import json
from enum import Enum

class ReActState(Enum):
    WAITING = "waiting"
    IN_THOUGHT = "in_thought"
    IN_ACTION = "in_action"
    IN_ACTION_INPUT = "in_action_input"
    IN_OBSERVATION = "in_observation"

class StreamingReActParser:
    def __init__(self):
        self.state = ReActState.WAITING
        self.buffer = ""
        self.current_component = {"type": None, "content": ""}
        self.tool_call_buffer = ""
        self.brace_count = 0
        
    def parse_chunk(self, chunk):
        """Parse streaming chunk and yield complete components"""
        self.buffer += chunk
        
        # Detect tool calls in Hermes format
        if "<tool_call>" in self.buffer:
            start = self.buffer.find("<tool_call>")
            end = self.buffer.find("</tool_call>")
            if end > start:
                json_str = self.buffer[start+11:end]
                try:
                    tool_call = json.loads(json_str)
                    yield {"type": "tool_call", "data": tool_call}
                    self.buffer = self.buffer[end+12:]
                except json.JSONDecodeError:
                    pass  # Wait for complete JSON
        
        # Extract text portions
        if self.buffer and "<tool_call>" not in self.buffer:
            yield {"type": "text", "content": self.buffer}
            self.buffer = ""

class ProductionReActStreamer:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.ollama_url = ollama_url
        self.parser = StreamingReActParser()
    
    async def stream_react_agent(self, prompt, model="qwen3:14b"):
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True
            }
            
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                async for line in response.content:
                    chunk_data = json.loads(line.decode())
                    if 'response' in chunk_data:
                        for component in self.parser.parse_chunk(chunk_data['response']):
                            yield component
```

## Chainlit @cl.step trajectory visualization patterns

Chainlit's step decorator enables hierarchical visualization of ReAct reasoning chains. The key insight is using different step types to distinguish reasoning phases while managing UI complexity through smart defaults.

### Hierarchical step structure for ReAct cycles

```python
import chainlit as cl

@cl.on_message
async def handle_react_query(message: cl.Message):
    async with cl.Step(name="🧠 ReAct Agent", type="run") as main_step:
        main_step.input = message.content
        
        for iteration in range(5):  # Max 5 iterations
            async with cl.Step(
                name=f"Iteration {iteration+1}", 
                type="run",
                default_open=(iteration == 0)  # Only expand first iteration
            ) as iter_step:
                
                # Thought phase with streaming
                async with cl.Step(name="🤔 Thinking", type="llm") as thought_step:
                    current_step = cl.context.current_step
                    
                    # Stream reasoning in real-time
                    async for chunk in stream_reasoning():
                        await current_step.stream_token(chunk)
                    
                # Action phase with tool visualization
                async with cl.Step(name="🔧 Action", type="tool") as action_step:
                    action_step.input = f"Tool: {tool_name}"
                    result = await execute_tool(tool_name, tool_args)
                    action_step.output = result
                
                # Check if complete
                if is_final_answer(result):
                    main_step.output = f"✅ {result}"
                    break
                    
                # Progressive update
                iter_step.output = f"Progress: {result[:100]}..."
                await iter_step.update()
```

### Dynamic step updates for long-running operations

```python
@cl.step(type="tool", name="multi_phase_search")
async def progressive_search(query: str):
    current_step = cl.context.current_step
    
    # Real-time progress updates
    phases = ["Initializing", "Searching", "Analyzing", "Synthesizing"]
    for phase in phases:
        current_step.output = f"📊 {phase}..."
        await current_step.update()
        
        result = await execute_phase(phase, query)
        
    current_step.output = f"✅ Complete: {result}"
    return result
```

## Robust error handling with circuit breakers

Production ReAct implementations require multiple layers of error protection, especially for the qwen3-14b model's 32k context window and Ollama's timeout scenarios.

### Context window management for qwen3-14b

```python
class Qwen3ContextManager:
    def __init__(self, max_tokens=30000):  # Buffer for 32k limit
        self.max_tokens = max_tokens
        
    def manage_conversation_context(self, messages):
        """Implement hierarchical summarization for context compression"""
        total_tokens = self.count_tokens(messages)
        
        if total_tokens <= self.max_tokens:
            return messages
            
        # Keep system prompt + recent messages
        if messages[0]['role'] == 'system':
            system_msg = messages[0]
            available_tokens = self.max_tokens - self.count_tokens([system_msg]) - 1000
            
            # Compress middle messages, keep recent
            if len(messages) > 10:
                start_msgs = messages[:3]
                end_msgs = messages[-5:]
                middle_msgs = messages[3:-5]
                
                # Summarize middle portion
                summary = self.summarize_messages(middle_msgs)
                return start_msgs + [{"role": "system", "content": f"[SUMMARY]: {summary}"}] + end_msgs
        
        return messages[-10:]  # Fallback
```

### Circuit breaker pattern for agent resilience

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class AgentCircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def execute_with_protection(self, func, *args):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time < self.recovery_timeout:
                return self._fallback_response()
            self.state = CircuitState.HALF_OPEN
        
        try:
            result = await func(*args)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if self.state == CircuitState.OPEN:
                return self._fallback_response()
            raise e
    
    def _fallback_response(self):
        return {"output": "Service temporarily unavailable. Using simplified response.", 
                "error": "circuit_breaker_open"}
```

### Ollama timeout configuration

```python
# Environment configuration for production
import os

os.environ["OLLAMA_REQUEST_TIMEOUT"] = "300"  # 5 minutes
os.environ["OLLAMA_KEEP_ALIVE"] = "5m"       # Keep models loaded
os.environ["OLLAMA_MAX_QUEUE"] = "512"       # Handle concurrent requests
os.environ["OLLAMA_NUM_PARALLEL"] = "4"      # Parallel processing

class OllamaErrorHandler:
    async def execute_with_retry(self, model, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                timeout = 60 * (2 ** attempt)  # Exponential backoff
                client = Client(timeout=timeout)
                return await client.generate(model=model, prompt=prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Wait before retry
```

## Complete integration architecture

The optimal architecture combines all components with clear separation of concerns and robust state management.

### Project structure

```
react-agent/
├── app/
│   ├── main.py              # FastAPI + Chainlit entry
│   ├── agents/
│   │   ├── react_agent.py   # Core ReAct logic
│   │   └── state.py         # Session state management
│   ├── mcp/
│   │   ├── client.py        # MCP client wrapper
│   │   └── tools.py         # Tool registration
│   ├── models/
│   │   └── ollama_qwen.py   # qwen3-14b integration
│   └── ui/
│       └── chainlit_app.py  # UI components
├── config/
│   ├── mcp_servers.json     # MCP configurations
│   └── model_config.yaml    # qwen3-14b settings
└── docker-compose.yml        # Container orchestration
```

### Main integration code

```python
from fastapi import FastAPI
from chainlit.utils import mount_chainlit
import chainlit as cl
from langchain_community.llms import Ollama

app = FastAPI()
mount_chainlit(app=app, target="app/ui/chainlit_app.py", path="/chat")

class ReactAgent:
    def __init__(self):
        self.llm = Ollama(
            model="qwen3:14b",
            base_url="http://localhost:11434",
            temperature=0.7,
            top_p=0.8
        )
        self.parser = StreamingReActParser()
        self.circuit_breaker = AgentCircuitBreaker()
        self.context_manager = Qwen3ContextManager()
        self.mcp_clients = {}
        
    async def initialize_mcp_tools(self, config):
        """Initialize MCP server connections"""
        for name, server_config in config["mcpServers"].items():
            if server_config.get("command"):
                # STDIO server
                self.mcp_clients[name] = await create_stdio_mcp_client(server_config)
            elif server_config.get("url"):
                # HTTP/SSE server
                self.mcp_clients[name] = await create_http_mcp_client(server_config)
    
    async def execute(self, query, session_id):
        """Main ReAct execution loop with all protections"""
        messages = self.context_manager.manage_conversation_context(
            cl.user_session.get("messages", [])
        )
        
        async with self.circuit_breaker.execute_with_protection(
            self._react_loop, query, messages
        ) as result:
            return result
    
    async def _react_loop(self, query, messages):
        """Core ReAct reasoning loop"""
        for iteration in range(5):
            # Generate with Hermes-style template
            prompt = self._build_hermes_prompt(query, messages)
            
            async for component in self.stream_react_agent(prompt):
                if component["type"] == "tool_call":
                    # Execute tool via MCP
                    tool_result = await self._execute_mcp_tool(component["data"])
                    messages.append({"role": "tool", "content": tool_result})
                elif component["type"] == "text":
                    # Check for final answer
                    if "Final Answer:" in component["content"]:
                        return component["content"]
        
        return "Maximum iterations reached"

@cl.on_chat_start
async def start():
    agent = ReactAgent()
    await agent.initialize_mcp_tools(load_config())
    cl.user_session.set("agent", agent)

@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    
    async with cl.Step(name="🧠 ReAct Processing", type="run") as main_step:
        result = await agent.execute(message.content, cl.user_session.get("id"))
        main_step.output = result
        
    await cl.Message(content=result).send()
```

### MCP tool configuration

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {"ALLOWED_DIRECTORY": "/workspace"}
    },
    "web_search": {
      "type": "sse",
      "url": "http://localhost:8000/mcp/search"
    }
  }
}
```

## Key implementation insights

The research reveals several critical insights for production deployment:

1. **qwen3-14b specifics**: Use Hermes-style templates with `/think` and `/no_think` commands for controlling reasoning depth
2. **Streaming complexity**: Implement state machines for robust parsing of streaming responses
3. **UI management**: Use Chainlit's `default_open=False` for non-critical steps to prevent UI clutter
4. **Error resilience**: Layer circuit breakers, exponential backoff, and graceful degradation
5. **Context efficiency**: Implement hierarchical summarization before hitting qwen3-14b's 32k limit
6. **MCP flexibility**: Support both STDIO and HTTP-based MCP servers for tool diversity

This architecture provides a production-ready foundation that handles the complexities of each technology while maintaining robust error handling and excellent user experience.