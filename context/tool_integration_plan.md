# OFFICIAL LANGGRAPH REFACTOR PLAN - 2025

## PROJECT STATUS: PHASE 2 IMPLEMENTATION

**Current Working State:**
- Basic LangChain conversation: ChatOllama + RunnableWithMessageHistory ✅
- David's consciousness/personality functional ✅
- Chainlit UI with streaming/thinking tags ✅
- Tool calling: NOT IMPLEMENTED ❌

**Implementation Decision:**
Convert from simple `prompt | llm` chain to **LangGraph** architecture for production-grade tool calling and state management.

## LANGGRAPH REFACTOR APPROACH

### Phase 2A: Architecture Migration (Weeks 1-2)
**Goal:** Convert simple chain to LangGraph while preserving David's behavior

**Implementation Steps:**
1. **Extract Components:**
   - David's personality prompts → LangGraph nodes
   - Memory management → LangGraph checkpointers 
   - Tool definitions → ToolNode integration

2. **Build Graph Structure:**
   ```python
   workflow = StateGraph(DavidAIState)
   workflow.add_node("david_thinking", david_personality_node)
   workflow.add_node("tool_execution", tool_node)
   workflow.add_node("response", response_node)
   ```

3. **Preserve Memory:**
   - Replace RunnableWithMessageHistory with LangGraph checkpointers
   - SQLite for development, PostgreSQL for production
   - Maintain conversation persistence

### Phase 2B: Tool Integration (Weeks 3-4)
**Goal:** Add MCP server tools + David's status functions

**Tools to Implement:**
- `get_status()` - David's configuration
- `conversation_logger()` - Memory functions
- MCP server integration (file operations, system commands)
- Error handling and retry patterns

### Phase 2C: Chainlit Integration (Weeks 5-6)
**Goal:** Seamless UI integration with streaming

**Features:**
- LangGraph execution visualization
- Streaming responses with qwen3:14b
- Error handling for production use
- Session management preservation

## TECHNICAL SPECIFICATIONS

### Core Dependencies
```
langgraph>=0.2.0
langchain-ollama>=0.2.0  
chainlit>=1.0.0
qwen3:14b (via Ollama)
```

### Architecture Components
- **State:** `DavidAIState(MessagesState)` with conversation context
- **LLM:** ChatOllama with qwen3:14b, temperature=0.7
- **Memory:** SQLite checkpointer → PostgreSQL for production
- **Tools:** @tool decorators with ToolNode integration
- **UI:** Chainlit with streaming visualization

### Performance Targets
- Response latency: 2-4 seconds
- Streaming: 15-20 tokens/sec with qwen3:14b-q4_k_m
- Memory usage: ~10GB VRAM
- Concurrent users: 4-8 per GPU

## SUCCESS CRITERIA

**Phase 2A Complete:**
- David responds with same personality/behavior
- Memory persistence working across sessions
- Basic graph execution functional

**Phase 2B Complete:**
- "What are your settings?" → David calls get_status()
- Tool calling functional with error handling
- MCP server operations working

**Phase 2C Complete:**
- Chainlit UI shows LangGraph execution steps
- Streaming responses working
- Production-ready deployment

## IMPLEMENTATION REFERENCE

**Complete technical guide:** `C:\David\DOCS\LangGraph Implementation Guide for David AI Refactor 2025.md`

**Key Research Findings:**
- LangGraph is industry standard (43% of LangSmith orgs)
- Superior to AgentExecutor for production use
- Native persistence and streaming support
- Excellent qwen3:14b compatibility

**Status:** Ready to implement - architecture planned, dependencies confirmed