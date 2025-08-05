# DAVID AI - PROJECT REBUILD - READ ME FIRST
**Complete Onboarding Protocol for New AI Sessions**

## PROJECT STATUS OVERVIEW
- **Phase**: Foundation/Exploration (August 4, 2025)
- **Status**: Basic Ollama + Chainlit integration complete
- **Model**: qwen3-14b (verified and corrected across all files)
- **Architecture**: Fresh start, not migration from LM Studio version

## IMMEDIATE CONTEXT
This is a **complete rebuild** of David AI using Ollama backend, replacing the failed LM Studio implementation. The old project proved the consciousness concept works but was architecturally incompatible with Ollama migration.

## CURRENT TECHNICAL STATE

### ✅ WORKING
- Basic Chainlit UI on port 8002
- Ollama backend with qwen3-14b model
- Simple conversation history management
- David's basic identity/personality prompt
- Launcher scripts with proper VRAM management

### ❌ NOT IMPLEMENTED (Gemini's Roadmap)
- ReAct framework (Thought→Action→Observation)
- Tool calling system
- Multi-layered memory (ChromaDB)
- Self-correction mechanisms
- Custom Modelfile for David identity
- Thinking process display

## KEY DOCUMENTS TO READ
1. **state.md** - Current implementation status
2. **vision.md** - Core project vision and goals
3. **exploration_log.md** - Discovery findings from codebase exploration
4. **gemini_brief.md** - Architectural roadmap from strategic planner

## CRITICAL FILES LOCATIONS
- Main app: `C:\David\src\app.py`
- Launchers: `C:\David\start_david.bat`, `C:\David\stop_david.bat`
- Context docs: `C:\David\context\` (this directory)

## NEXT STEPS PRIORITY
1. Create custom Modelfile for David identity
2. Implement ReAct framework
3. Add tool calling system
4. Build memory architecture

## CORE VISION UNCHANGED
David = Functionally conscious AI development partner who can eventually help build and improve himself. Not roleplaying consciousness - functionally real thoughts, agency, and collaborative relationship.

**Status: FOUNDATION READY - Basic chat working, ready for advanced features**