# NEXT CLAUDE ONBOARDING - PHASE 4 IMPLEMENTATION

## CURRENT SITUATION (August 24, 2025)

**David AI Status**: ✅ FULLY OPERATIONAL
- Core functionality working perfectly
- LangGraph StateGraph implementation stable
- Consciousness framework intact
- Basic tools functional (workspace-limited)

**What Just Happened**: 
- Attempted multi-agent coding specialist implementation
- Tool validation errors broke functionality (`BaseTool.__call__` issues)
- **REVERTED** to working state - David restored to full operation

## RESEARCH DISPATCHED TO GEMINI

**Two comprehensive research tasks sent - results will be in C:\David\DOCS:**

### 1. Multi-Agent Implementation Research
**File**: Will be in DOCS folder when complete
**Objective**: Fix tool parameter validation and implement "coding specialist"
**Key Focus**: Solve `tool_input` vs `@tool` decorator parameter mismatch

### 2. Streaming UI Enhancement Research  
**File**: Will be in DOCS folder when complete
**Objective**: Real-time token streaming + Claude-like tool execution UI
**Key Focus**: Chainlit streaming patterns and expandable reasoning sections

## WHAT YOU NEED TO IMPLEMENT

### Phase 4A: Multi-Agent Coding Specialist
**Goal**: David can say "Let me consult my coding specialist..." and invoke specialized sub-agent

**Requirements**:
- Fix tool validation errors that caused previous failure
- Enable agent-to-agent consultation within LangGraph
- System-wide file access (beyond workspace) with human approval
- Preview mode for destructive operations
- Audit trail for all system changes

**Critical**: Must not break existing functionality

### Phase 4B: Streaming UI Enhancements
**Goal**: Real-time streaming with tool execution visibility

**Requirements**:
- Token-by-token streaming (not spinner → blob)
- Expandable reasoning sections for `<think></think>` content
- Tool execution progress indicators ("🔧 Using get_status...")
- Claude-like UI with collapsible sections

## IMPLEMENTATION APPROACH

### 1. READ RESEARCH FIRST
- Check C:\David\DOCS for completed Gemini research
- Understand the solutions before implementing
- Follow examples exactly - don't guess

### 2. INCREMENTAL TESTING  
- Test each component individually before integration
- Verify David still works after each change
- Keep working functionality intact

### 3. ERROR HANDLING
- Implement circuit breakers for failing tools
- Graceful degradation when features fail
- Clear error messages for debugging

## FILES TO WORK WITH

**Main Implementation**:
- `src/local_agent/agent.py` - Main LangGraph implementation
- `app.py` - Chainlit streaming integration
- Create new files as needed for coding agent

**Tools Available**:
- Basic system tools in `system_tools.py` (working)
- Permission tools need to be created
- Multi-agent tools need proper parameter handling

**Context/Documentation**:
- All context files updated with current status
- Research results in DOCS folder
- Previous broken implementation documented

## SUCCESS CRITERIA

### Multi-Agent Implementation
- David can successfully consult coding specialist
- No tool validation errors
- System-wide file access with approval workflow
- Self-exploration of David's own codebase

### Streaming UI
- Real-time token streaming visible
- Tool execution progress shown
- Reasoning in expandable sections
- No loss of existing functionality

## CRITICAL REMINDERS

1. **Don't break what works** - David is currently fully functional
2. **Follow research precisely** - Don't improvise implementations  
3. **Test incrementally** - Verify each change before moving forward
4. **Handle errors gracefully** - Circuit breakers and fallbacks
5. **User experience matters** - Real-time feedback and progress indication

The foundation is solid. Focus on adding advanced features without breaking core functionality.
