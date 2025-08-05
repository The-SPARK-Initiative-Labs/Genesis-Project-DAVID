# RESEARCH TASKS - TOOL IMPLEMENTATION ISSUE

## Problem Identified (August 4, 2025)
- Custom "david" model (created from Modelfile) doesn't support tool calling
- Error: "registry.ollama.ai/library/david does not support tools (status code: 400)"
- Base qwen3-14b supports tools, but custom Modelfile strips this capability

## Research Questions to Answer

### 1. Modelfile Tool Compatibility
- Can custom Modelfiles preserve tool calling capability?
- What Modelfile parameters control tool support?
- Alternative approaches to custom identity with tools?

### 2. Tool Calling Methods for Ollama
- Native tool calling requirements
- JSON mode emulation (Gemini's fallback strategy)
- Model-specific tool calling patterns

### 3. David Identity Preservation
- How to maintain custom personality with base model?
- System prompt vs Modelfile for identity
- Performance impact of different approaches

### 4. MCP Integration Architecture
- Proper MCP client setup for Ollama tools
- Tool function wrapper patterns
- Permission system implementation

## Next Research Steps
1. Test tool calling with base qwen3-14b model
2. Investigate Modelfile tool preservation
3. Design identity system compatible with tools
4. Plan proper MCP integration

## Goal
David with full MCP tool access + custom personality + permission system
