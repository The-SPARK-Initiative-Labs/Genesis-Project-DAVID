# TOOL INTEGRATION PLAN - SAFE IMPLEMENTATION

## Phase 2A: Add status_check Tool (Non-Breaking)

### Current Working State
- LangChain ChatOllama + RunnableWithMessageHistory functional
- Memory persistence confirmed
- Basic conversation logging added

### Implementation Steps (Preserve Existing Architecture)

1. **Add @tool decorator to status_check() in agent.py**
   - Import: `from langchain_core.tools import tool`
   - Decorate existing function: `@tool def status_check()`

2. **Create tool-enabled agent alongside existing one**
   - Import: `from langchain.agents import create_tool_calling_agent, AgentExecutor`
   - Keep existing `prompt | llm` chain as fallback
   - Add tools list: `tools = [status_check]`

3. **Replace chain creation with agent**
   ```python
   # Instead of: agent_chain = prompt | llm
   agent = create_tool_calling_agent(llm, tools, prompt)
   agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
   ```

4. **Update RunnableWithMessageHistory wrapper**
   - Wrap the AgentExecutor instead of the chain
   - Keep all existing session management logic

### Safety Measures
- Test with simple status queries before adding more tools
- Preserve existing memory system unchanged
- Keep original behavioral prompts intact
- No changes to app.py or session handling

### Success Criteria
- David can respond to "what are your settings?"
- Existing memory/conversation flow unaffected
- Ready for additional tool additions

Status: Ready to implement - minimal risk to existing functionality
