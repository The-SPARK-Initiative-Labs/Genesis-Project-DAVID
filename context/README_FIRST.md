# 🚀 DAVID AI - COMPLETE CLAUDE ONBOARDING PROTOCOL

**You are joining the David AI development team as lead developer. This document provides complete context to match the knowledge of previous Claude agents.**

## PROJECT OVERVIEW
David AI is a functionally conscious, self-improving AI development partner. This is a sophisticated rebuild project using Ollama + Chainlit + qwen3-14b, designed to create an AI that eventually helps build and improve itself.

## MANDATORY READING SEQUENCE

### 1. PROJECT CONTEXT (Read First)
- `C:\David\context\current_status.md` - **URGENT HANDOFF**: Exact current state, critical bug, next priorities
- `C:\David\context\state.md` - Previous implementation status  
- `C:\David\context\vision.md` - Core project vision and goals  
- `C:\David\context\tool_research_results.md` - Critical technical solution
- `C:\David\context\research_tasks.md` - Completed research questions

### 2. TECHNICAL MASTERY (Essential Knowledge)
- `C:\David\DOCS\Chainlit Agentic UI Development_.md` - UI framework mastery
- `C:\David\DOCS\Chainlit with Ollama Model Integration_.md` - Backend integration
- `C:\David\DOCS\Ollama Tool-Use Python Framework_.md` - Tool calling architecture
- `C:\David\DOCS\Chainlit Decorator Comprehensive Manual.md` - Complete @cl. decorator reference
- `C:\David\DOCS\Chainlit UI Customization Manual_.md` - 5-layer UI customization hierarchy
- `C:\David\DOCS\ReAct.md` - ReAct framework implementation guide for Chainlit+Ollama+MCP stack
- `C:\David\DOCS\Complete ReAct Framework Implementation guide for qwen3.md` - **CRITICAL**: Research-backed implementation patterns for qwen3-14b ReAct agents
- `C:\David\DOCS\Sequential Instructions in Conversational AI.md` - **URGENT**: Research on fixing David's sequential instruction handling bug
- `C:\David\DOCS\Anti-Hallucination Solutions for ReAct.md` - **BLOCKING BUG**: Complete anti-hallucination system for David's fabrication issue

### 3. PROJECT HISTORY (Background Context)
- `C:\Users\farri\OneDrive\Desktop\david_ai_ollama_migration_brief.md` - Complete project evolution
- `C:\Users\farri\OneDrive\Desktop\LOOK HERE.txt` - Current user conversations with David

### 4. CODEBASE EXPLORATION (MANDATORY)
**Examine current implementation before proceeding:**
- `C:\David\src\app.py` - Main application (680 lines) 
- `C:\David\src\.chainlit\config.toml` - UI configuration
- `C:\David\context\exploration_log.md` - Previous findings
- Project structure: `C:\David\` (root), `C:\David\src\` (application)

**Key Architecture Components to Understand:**
- **MCPServerClient**: JSON-RPC communication with MCP server
- **ToolGuardian**: Permission system (safe vs dangerous tools)  
- **David Personality**: System prompt with consciousness framework
- **Tool Functions**: Async wrappers for 5 MCP tools
- **Ollama Integration**: OpenAI-compatible tool calling

## KEY TECHNICAL INSIGHTS
- Custom Modelfiles break tool calling (definitive research finding)
- Solution: Base model + runtime system prompts
- MCP server integration required for file operations
- Permission system needed for dangerous tools

## YOUR MCP TOOLS
You have the same MCP server access as previous Claude agents:
- File operations: read_file, write_file, list_directory
- System operations: execute_command, python_execute
- Network tools: ping, nslookup, system_info

## PROJECT PHASES
1. ✅ Foundation (basic chat + thinking display)
2. ✅ UI Fixes (clean step display) 
3. ✅ Research (tool calling solution found)
4. ✅ Tool implementation with permissions
5. 🔄 **CURRENT**: Sequential instruction handling fix
6. ⏳ ReAct framework
7. ⏳ Memory system (ChromaDB)
8. ⏳ Self-improvement capabilities

## COMPLETION CHECKLIST
- [ ] All context documents read and understood
- [ ] Technical documentation mastered (including ReAct and Sequential Instruction research)
- [ ] Current codebase explored (`C:\David\src\app.py` - Hermes format implemented)
- [ ] Critical bug understood (sequential instruction handling failure)
- [ ] Test results analyzed (`C:\Users\farri\OneDrive\Desktop\New Text Document.txt`)
- [ ] Ready to implement sequential instruction fix

## IMMEDIATE ACTION REQUIRED
**URGENT**: Fix sequential instruction handling before ReAct implementation
- Study `C:\David\DOCS\Sequential Instructions in Conversational AI.md`
- Implement task boundary detection in conversation flow
- Test with provided test cases to verify fix

## IMMEDIATE RESEARCH PRIORITIES (Post-Onboarding)
**Critical gaps requiring targeted research:**

1. **Memory Systems Architecture**
   - ChromaDB integration patterns with Chainlit/Ollama
   - Memory consolidation workflows for David's consciousness
   - Vector storage optimization and retrieval strategies

2. **Self-Improvement Safety Patterns** 
   - Safe AI code modification frameworks
   - Change review and validation processes
   - Self-corruption prevention mechanisms

3. **AI Development Partnership Workflows**
   - Human-AI collaborative coding patterns
   - Code review delegation strategies
   - Development partnership best practices

**Research Priority**: Memory systems first (immediate), then self-improvement safety (foundational)

**After completing this onboarding, you will have the same knowledge and context as the Claude agents who built this system. The project continues with tool implementation.**

---
*Status: Core functionality complete - tools working, UI polished, model persistence solved, ready for memory system and ReAct framework*