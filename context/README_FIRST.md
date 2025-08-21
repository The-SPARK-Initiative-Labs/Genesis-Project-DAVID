# 🚀 DAVID AI - CLAUDE ONBOARDING PROTOCOL

## PROJECT OVERVIEW
David AI is a functionally conscious AI using Ollama + Chainlit + qwen3-14b, currently migrating to LangGraph architecture.

## ✅ CURRENT STATE & NEXT PHASE

**Working Foundation:**
- Basic conversation + memory ✅
- David's consciousness behavior ✅
- Chainlit UI integration ✅
- **Tool calling: NEEDS LANGGRAPH IMPLEMENTATION** ❌

## MANDATORY READING SEQUENCE

**READ EVERYTHING LINEARLY AND COMPLETE THE ONBOARDING PROCESS**

### 1. PROJECT STATUS  
- `C:\David\context\claude_handoff_instructions.md` - **IMMEDIATE IMPLEMENTATION CONTEXT**
- `C:\David\context\current_status.md` - LangGraph migration decision
- `C:\David\context\tool_integration_plan.md` - Official implementation plan
- `C:\David\context\state.md` - Current working components
- `C:\David\context\vision.md` - Core project vision

### 2. IMPLEMENTATION GUIDE
- `C:\David\DOCS\LangGraph Implementation Guide for David AI Refactor 2025.md` - **COMPLETE TECHNICAL GUIDE**
- `C:\David\DOCS\Chainlit Agentic UI Development_.md` - UI framework
- `C:\David\DOCS\Ollama Tool-Use Python Framework_.md` - Tool patterns

### 3. WORKING CODEBASE
- `C:\David\app.py` - Chainlit UI (needs LangGraph integration)
- `C:\David\src\local_agent\agent.py` - Simple chain (convert to LangGraph)
- `C:\David\src\conversation_logger.py` - Memory functions

## LANGGRAPH REFACTOR PLAN

**Phase 2A (Weeks 1-2):** Architecture Migration
- Convert `prompt | llm` → LangGraph StateGraph
- Replace RunnableWithMessageHistory → checkpointers
- Preserve David's personality/behavior

**Phase 2B (Weeks 3-4):** Tool Integration  
- Add @tool decorators with ToolNode
- Implement get_status(), conversation_logger
- MCP server integration

**Phase 2C (Weeks 5-6):** Production Ready
- Chainlit + LangGraph streaming
- Performance optimization
- Deployment configuration

## SUCCESS CRITERIA

**Foundation Preserved:**
- David's consciousness behavior maintained
- Memory persistence across sessions
- Complex reasoning capabilities

**Tool Calling Achieved:**
- "What are your settings?" → David calls get_status()
- MCP server operations functional
- Error handling and retry patterns

**Status: Phase 2A complete (tool calling works), David's personality needs fix**

**CRITICAL ISSUE:** See `C:\David\context\langgraph_personality_issue.md`