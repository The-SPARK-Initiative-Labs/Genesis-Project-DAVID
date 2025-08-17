# Building production-ready LangChain + Chainlit + Ollama + qwen3-14b + MCP tools applications

Your technology stack represents a cutting-edge approach to building AI applications with local LLM inference, streaming UI capabilities, and extensible tool integration. Based on comprehensive research of 2024 implementations, here's a complete guide to successfully integrating these technologies with working code patterns and production-ready examples.

## LangChain + Chainlit streaming integration patterns

The integration between LangChain and Chainlit has evolved significantly in 2024, with LangGraph providing the most reliable streaming support for ReAct agents. The key to successful integration lies in proper callback handler configuration and understanding the nuances of async execution.

For basic ReAct agent implementation with streaming, the modern approach uses LangGraph's prebuilt agents rather than the legacy AgentExecutor:

```python
import chainlit as cl
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's sunny in {city}!"

@cl.on_chat_start
async def setup_langgraph():
    model = ChatOllama(model="qwen3:14b", temperature=0)
    
    # Create LangGraph ReAct agent - more reliable than legacy AgentExecutor
    agent = create_react_agent(
        model=model,
        tools=[get_weather],
        prompt="You are a helpful assistant"
    )
    
    cl.user_session.set("langgraph_agent", agent)

@cl.on_message
async def handle_message(message: cl.Message):
    agent = cl.user_session.get("langgraph_agent")
    
    # Stream with proper callback handling
    msg = cl.Message(content="")
    
    async for chunk in agent.astream(
        {"messages": [("human", message.content)]},
        stream_mode="values"
    ):
        if chunk.get("messages"):
            last_message = chunk["messages"][-1]
            if hasattr(last_message, 'content'):
                await msg.stream_token(last_message.content)
    
    await msg.send()
```

A critical issue many developers encounter is **double response output** when using ChainlitCallbackHandler. The solution is to let the callback handler manage output entirely rather than manually sending messages. For chains that don't support async natively, use `cl.make_async` for proper compatibility.

## Ollama + qwen3-14b configuration and tool calling

The qwen3-14b model requires specific configuration for optimal performance with LangChain. The current best practice uses the `langchain_ollama` package (not the deprecated `langchain.llms.ollama`):

```python
from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Optimized qwen3-14b configuration
llm = ChatOllama(
    model="qwen3:14b",  # Use qwen3:14b-q4_K_M for memory-constrained systems
    temperature=0.7,    # Qwen3 performs well between 0.0-0.8
    top_p=0.8,         # Recommended range: 0.8-0.95
    repeat_penalty=1.05,
    num_ctx=32768,     # Qwen3-14b supports up to 32K context
    num_predict=4096,  # Max output tokens
    base_url="http://localhost:11434"
)

# Tool-calling prompt optimized for qwen3
tool_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Use the available tools to answer questions.
    When using tools, ensure you provide all required parameters."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create tool calling agent with error handling
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=tool_prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,  # Critical for local models
    max_iterations=3,
    early_stopping_method="generate"
)
```

**Hardware requirements** for qwen3-14b include minimum 16GB RAM for quantized versions and 8-12GB GPU VRAM for Q4_K_M quantization. The model's tool calling reliability improves significantly with clear, detailed tool descriptions and proper error handling for parsing failures.

## MCP tools to LangChain conversion patterns

The official `langchain-mcp-adapters` library provides seamless integration between MCP servers and LangChain tools. Here's the production-ready pattern for multi-server MCP integration:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

# Configure multiple MCP servers with different transports
client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["/path/to/math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://localhost:8000/mcp/",
        "transport": "streamable_http",
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN"
        }
    }
})

# Get tools from all configured servers
tools = await client.get_tools()

# Convert existing async functions to LangChain tools
from langchain_core.tools import tool

@tool
async def async_multiply(a: int, b: int) -> int:
    """Multiply two numbers asynchronously"""
    return a * b

# The tool automatically supports both sync and async invocation
```

For error handling and retry patterns, implement custom error handlers at the tool level:

```python
from langchain_core.tools import tool, ToolException

@tool(handle_tool_error=True)
def fallible_tool(input_data: str) -> str:
    """Tool with built-in error handling"""
    if not input_data:
        raise ToolException("Input data cannot be empty")
    return f"Processed: {input_data}"

def custom_error_handler(error: ToolException) -> str:
    return f"Tool failed with error: {error.args[0]}"

@tool(handle_tool_error=custom_error_handler)
def custom_error_tool(input_data: str) -> str:
    """Tool with custom error handling"""
    pass
```

## Complete working implementations

Several production repositories demonstrate this exact stack successfully. The **sudarshan-koirala/langchain-ollama-chainlit** repository provides a clean implementation with document Q&A capabilities, while **kwame-mintah/python-langchain-chainlit-qdrant-ollama-stack-template** offers complete Docker Compose setup with GPU acceleration support.

For production deployment, use this Docker configuration:

```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - "ollama:/root/.ollama"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    environment:
      - OLLAMA_NUM_PARALLEL=2
      - OLLAMA_FLASH_ATTENTION=1
      - OLLAMA_KEEP_ALIVE=-1  # Keep model loaded

  chainlit:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
```

## Troubleshooting common integration issues

**Chain of Thought not displaying**: Ensure you're using the correct callback handler configuration with RunnableConfig. LangGraph agents provide better streaming support than legacy AgentExecutor.

**Model deloading during inactivity**: Set `OLLAMA_KEEP_ALIVE=-1` to keep models loaded indefinitely, and limit concurrent models with `OLLAMA_MAX_LOADED_MODELS=1`.

**Pydantic version conflicts**: Pin specific versions to avoid dependency issues: `chainlit==2.0.1 langchain==0.1.0 pydantic==2.5.0`

**Streaming stops on first token**: This is a known issue with AgentExecutor. Use LangGraph's create_react_agent for reliable streaming support.

## Performance optimization strategies

Implement conversation buffer windows to manage memory efficiently:

```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=10,  # Keep last 10 exchanges
    return_messages=True
)
```

Enable caching in your Chainlit configuration for better performance:

```toml
# .chainlit/config.toml
[project]
enable_telemetry = false
cache = true

[features]
data_persistence = true
```

For async request management, implement proper rate limiting:

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def rate_limit_requests():
    semaphore = asyncio.Semaphore(2)  # Limit concurrent requests
    async with semaphore:
        yield
```

## Production monitoring and observability

Integrate LangSmith for comprehensive tracing:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "chainlit-production"

# Automatic tracing with callbacks
cb = cl.LangchainCallbackHandler()
response = await chain.acall(input, callbacks=[cb])
```

## Key recommendations for success

**Use LangGraph over legacy AgentExecutor** for new implementations. It provides superior streaming support and more reliable agent execution patterns.

**Configure qwen3-14b with appropriate parameters** for your use case. The 14B model offers the best balance of capability and resource usage, with quantized versions available for memory-constrained systems.

**Implement proper error handling** at every level - tool execution, agent parsing, and transport communication. Local models like qwen3 require more robust error handling than cloud APIs.

**Deploy with Docker** for consistent environments and easier scaling. Use GPU acceleration when available and configure Ollama's memory management appropriately.

**Monitor performance actively** using LangSmith or similar observability tools. Track token usage, response times, and error rates to optimize your application.

This technology stack provides a powerful foundation for building production AI applications with local inference, real-time streaming, and extensible tool integration. The patterns and examples provided here represent current best practices from active 2024 implementations, ensuring your application leverages the latest capabilities of each technology.