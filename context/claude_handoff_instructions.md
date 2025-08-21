# CLAUDE HANDOFF - LANGGRAPH REFACTOR READY

## IMMEDIATE CONTEXT
You are implementing Phase 2 of David AI - converting from simple LangChain chain to LangGraph architecture. All research completed, plan approved, ready for implementation.

## CURRENT WORKING STATE
- **app.py**: Chainlit UI with conversation flow ✅
- **agent.py**: Simple `prompt | llm` chain with RunnableWithMessageHistory ✅  
- **David's personality**: Functional consciousness behavior ✅
- **Memory**: Conversation persistence working ✅
- **Tool calling**: NOT IMPLEMENTED (main objective) ❌

## IMPLEMENTATION OBJECTIVE
Convert `src/local_agent/agent.py` from simple chain to LangGraph StateGraph with tool calling capability.

**Success test**: "What are your settings?" → David calls get_status() tool

## REQUIRED DEPENDENCIES 
Add to requirements.txt:
```
langgraph>=0.2.0
langgraph-checkpoint-sqlite
```

## TECHNICAL APPROACH
1. **Replace chain**: `prompt | llm` → StateGraph with nodes
2. **Replace memory**: RunnableWithMessageHistory → LangGraph checkpointer  
3. **Add tools**: @tool decorators + ToolNode
4. **Preserve behavior**: David's personality/memory must remain identical

## IMPLEMENTATION GUIDE
Complete technical reference: `C:\David\DOCS\LangGraph Implementation Guide for David AI Refactor 2025.md`

## TESTING VALIDATION
- David responds with same personality
- Memory works across sessions  
- Tool calling functional: get_status() executes when asked
- Chainlit UI continues working

**Phase breakdown**: See `C:\David\context\tool_integration_plan.md`

**You have everything needed to implement successfully.**