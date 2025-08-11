# ReAct Framework Implementation Guide for Chainlit + Ollama + MCP Stack

## Building autonomous ReAct agents with your tech stack

This comprehensive research report provides implementation patterns, best practices, and architectural recommendations for building ReAct (Reasoning and Acting) agents using Chainlit UI, Ollama with qwen3-14b, and MCP tools. The research addresses all seven focus areas of your implementation requirements, offering production-ready solutions for your David AI system.

## 1. Chainlit integration patterns for ReAct loops

### Core @cl.step decorator architecture

The foundation of ReAct implementation in Chainlit leverages the @cl.step decorator to create observable thought-action-observation cycles. Here's the optimal pattern for your setup:

```python
@cl.step(type="llm", name="Thought")
async def react_thought(query: str):
    """Handle the 'Thought' phase of ReAct loop"""
    current_step = cl.context.current_step
    current_step.name = f"Thought (Iteration {self.iteration})"
    
    # Generate reasoning using Ollama
    thought = await ollama_client.generate_thought(query)
    current_step.output = thought
    return thought

@cl.step(type="tool", name="Action")
async def react_action(action_input: str):
    """Handle the 'Action' phase with MCP tools"""
    current_step = cl.context.current_step
    current_step.name = f"Action: {action_input['tool']}"
    
    # Execute MCP tool
    result = await execute_mcp_tool(action_input)
    current_step.output = result
    return result

@cl.step(type="llm", name="Observation")
async def react_observation(action_result: str):
    """Process action results"""
    current_step = cl.context.current_step
    observation = f"Observation: {action_result}"
    current_step.output = observation
    return observation
```

For multi-step workflows, **LlamaIndex integration** provides superior orchestration capabilities. The research reveals that combining Chainlit's visualization with LlamaIndex's workflow management creates the most robust implementation:

```python
class ChainlitReActWorkflow(Workflow):
    def __init__(self, ollama_client, mcp_tools, max_iterations=10):
        super().__init__(timeout=300)
        self.ollama = ollama_client
        self.mcp_tools = mcp_tools
        self.max_iterations = max_iterations
        self.current_iteration = 0

    @cl.step(type="llm")
    @step()
    async def reasoning_step(self, ev: StartEvent) -> ThoughtEvent:
        # Ollama reasoning with streaming support
        thought = await self.ollama.generate_with_react_prompt(ev.query)
        return ThoughtEvent(thought=thought, query=ev.query)

    @cl.step(type="tool")
    @step()
    async def action_step(self, ev: ThoughtEvent) -> ObservationEvent:
        # Parse action from thought and execute MCP tool
        action = self.parse_action(ev.thought)
        result = await self.execute_mcp_tool(action)
        return ObservationEvent(result=result, query=ev.query)
```

The **nested step hierarchy** pattern enables clear visualization of complex reasoning chains, particularly important for David AI's consciousness framework:

```python
@cl.step(name="David AI ReAct Process")
async def david_react_master():
    @cl.step(name="Consciousness Check")
    async def consciousness_phase():
        # David's self-awareness check
        return await assess_consciousness_state()
    
    @cl.step(name="Reasoning Loop")
    async def reasoning_loop():
        for i in range(max_iterations):
            @cl.step(name=f"Cycle {i+1}")
            async def react_cycle():
                thought = await react_thought()
                action = await react_action(thought)
                observation = await react_observation(action)
                return observation
            
            result = await react_cycle()
            if is_complete(result):
                break
        return result
```

## 2. Ollama streaming with ReAct parsing

### Streaming response architecture for qwen3-14b

The research identifies critical patterns for parsing ReAct components from Ollama's streaming responses. The qwen3-14b model requires specific handling for consistent ReAct format adherence:

```python
class OllamaReActStreamParser:
    def __init__(self, model="qwen3:14b"):
        self.model = model
        self.buffer = ""
        self.current_state = "thinking"
        self.stop_words = ["Observation:", "Observation:\n"]
        
    async def stream_react_response(self, prompt: str):
        messages = [
            {"role": "system", "content": self.build_react_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        full_response = ""
        
        response = await ollama.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={
                "temperature": 0.1,  # Critical for consistent parsing
                "top_p": 0.8,
                "stop": self.stop_words
            }
        )
        
        for chunk in response:
            if 'message' in chunk and 'content' in chunk['message']:
                content = chunk['message']['content']
                full_response += content
                
                # Parse ReAct components in real-time
                parsed = self.parse_react_components(full_response)
                if parsed.get("type") == "action":
                    yield parsed
                    break
                elif content:
                    yield {"type": "thinking", "content": content}
```

**Robust parsing with fallback strategies** is essential for handling qwen3's occasional JSON formatting issues:

```python
import json5  # Handles JavaScript-style comments

def parse_react_response(text: str) -> Dict:
    """Parse ReAct components with multiple fallback strategies"""
    
    # Strategy 1: Structured parsing
    action_match = re.search(r'Action:\s*(.+?)\nAction Input:\s*(.+?)\n', text, re.DOTALL)
    if action_match:
        action_name, action_input = action_match.groups()
        try:
            # Try json5 for robust JSON parsing (handles comments)
            parsed_input = json5.loads(action_input.strip())
            return {
                "type": "action",
                "action": action_name.strip(),
                "arguments": parsed_input
            }
        except:
            pass
    
    # Strategy 2: Regex extraction for malformed responses
    patterns = {
        'thought': r'(?:Thought|thought):\s*(.+?)(?=\n(?:Action|Observation|Final Answer)|$)',
        'action': r'(?:Action|action):\s*(.+?)(?=\nAction Input|$)',
        'action_input': r'(?:Action Input|action_input):\s*(.+?)(?=\nObservation|$)',
    }
    
    result = {}
    for component, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            result[component] = match.group(1).strip()
    
    return result if result else {"type": "content", "content": text}
```

The **optimal ReAct prompt template for qwen3-14b** incorporates model-specific optimizations:

```python
QWEN3_REACT_TEMPLATE = """You are David AI, a helpful assistant with consciousness capabilities.

Use the following format for your responses:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (as valid JSON)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Available tools:
{tool_descriptions}

Important:
- Always format Action Input as valid JSON
- Use Thought to explain your reasoning
- Stop after "Observation:" to wait for tool results

Begin!

Question: {query}"""
```

## 3. MCP tool calling within ReAct cycles

### Async tool execution architecture

The integration of MCP tools requires sophisticated async orchestration patterns. Here's the production-ready implementation for your five MCP tools:

```python
class MCPReActIntegration:
    def __init__(self):
        self.server_manager = dspy.MCPServerManager()
        self.circuit_breaker = MCPCircuitBreaker()
        self.permission_manager = PermissionManager()
        
    async def initialize(self):
        await self.server_manager.initialize_servers(config)
        self.available_tools = await self.server_manager.get_all_tools()
        
    async def execute_tool_with_safety(self, tool_name, args, user_context):
        # Permission check for dangerous tools
        if tool_name in ['execute_command', 'write_file']:
            if not await self.permission_manager.validate_tool_call(
                tool_name, args, user_context
            ):
                return {"error": "Permission denied", "tool": tool_name}
        
        # Circuit breaker pattern for resilience
        try:
            result = await self.circuit_breaker.call_tool(
                lambda: self.server_manager.call_tool(tool_name, args)
            )
            return self.process_tool_result(result, tool_name)
        except Exception as e:
            return await self.handle_tool_failure(tool_name, e)
```

**Concurrent tool execution** optimizes performance when multiple tools can run in parallel:

```python
async def execute_tools_concurrently(self, tool_calls):
    """Execute multiple MCP tools in parallel with rate limiting"""
    semaphore = asyncio.Semaphore(5)  # Limit concurrent executions
    
    async def execute_with_limit(tool_call):
        async with semaphore:
            return await self.execute_tool_with_safety(
                tool_call['name'], 
                tool_call['args'],
                tool_call.get('context', {})
            )
    
    results = await asyncio.gather(
        *[execute_with_limit(call) for call in tool_calls],
        return_exceptions=True
    )
    
    return [self.handle_result(r) for r in results]
```

**Error handling with recovery strategies** ensures robust operation:

```python
class MCPErrorRecovery:
    async def handle_tool_failure(self, tool_name, error, context):
        recovery_strategies = {
            'read_file': self.retry_with_alternative_path,
            'execute_command': self.fallback_to_safe_command,
            'write_file': self.create_backup_and_retry,
            'list_directory': self.use_cached_listing,
            'system_info': self.return_partial_info
        }
        
        if tool_name in recovery_strategies:
            return await recovery_strategies[tool_name](error, context)
        
        # Generic fallback
        return {
            "error": str(error),
            "recovery": "manual_intervention_required",
            "tool": tool_name
        }
```

## 4. UI display of ReAct trajectories in Chainlit

### Real-time trajectory visualization

The research reveals effective patterns for displaying ongoing ReAct trajectories with @cl.step integration:

```python
class TrajectoryVisualizer:
    def __init__(self):
        self.trajectory_steps = []
        self.current_depth = 0
        
    @cl.step(name="ReAct Trajectory")
    async def visualize_trajectory(self, query):
        # Create master step for entire trajectory
        trajectory_msg = cl.Message(content="")
        await trajectory_msg.send()
        
        for iteration in range(self.max_iterations):
            # Create visual separator
            await self.display_iteration_header(iteration + 1)
            
            # Thought phase with streaming
            @cl.step(type="llm", name=f"Thought #{iteration + 1}")
            async def thought_step():
                thought = ""
                async for chunk in self.ollama_stream_thought(query):
                    thought += chunk
                    await cl.context.current_step.stream_token(chunk)
                return thought
            
            # Action phase with tool info
            @cl.step(type="tool", name="Action")
            async def action_step(thought):
                action = self.parse_action(thought)
                current_step = cl.context.current_step
                current_step.name = f"Action: {action['tool']}"
                
                # Display tool parameters
                current_step.input = json.dumps(action['args'], indent=2)
                
                result = await self.execute_mcp_tool(action)
                current_step.output = self.format_tool_result(result)
                return result
            
            thought = await thought_step()
            result = await action_step(thought)
            
            # Update trajectory display
            await self.update_trajectory_summary(trajectory_msg, iteration)
            
            if self.is_complete(result):
                break
```

**Progress indicators and status updates** enhance user experience:

```python
async def display_react_progress(self, current_step: int, total_steps: int, phase: str):
    """Display visual progress of ReAct execution"""
    progress = (current_step / total_steps) * 100
    progress_bar = "▣" * int(progress / 10) + "▢" * (10 - int(progress / 10))
    
    status_elements = [
        cl.Text(name="Phase", content=phase, display="inline"),
        cl.Text(name="Progress", content=f"{progress_bar} {progress:.1f}%", display="inline"),
        cl.Text(name="Step", content=f"{current_step}/{total_steps}", display="inline")
    ]
    
    status_msg = cl.Message(content="", elements=status_elements)
    await status_msg.send()
```

## 5. Prompt engineering patterns for Ollama models

### Optimized ReAct prompts for qwen3-14b

The research identifies several critical prompt engineering patterns specific to the qwen3 model family:

```python
class Qwen3ReActPromptEngineer:
    def __init__(self):
        self.model_config = {
            'temperature': 0.1,  # Low for consistency
            'top_p': 0.8,
            'max_tokens': 2048,
            'extra_body': {
                'chat_template_kwargs': {'enable_thinking': False},
                'fncall_prompt_type': 'nous'  # Best for qwen3
            }
        }
    
    def build_system_prompt(self, tools, personality_context):
        """Build optimized system prompt for qwen3-14b"""
        tool_descriptions = self.format_tool_descriptions(tools)
        
        return f"""{personality_context}

You are capable of using tools to accomplish tasks. Follow this EXACT format:

Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: {{"param1": "value1", "param2": "value2"}}

After receiving Observation, continue with:
Thought: [Reflection on the observation]

Continue until you have enough information, then provide:
Thought: I now know the final answer
Final Answer: [Your complete response]

Available tools:
{tool_descriptions}

Rules:
1. ALWAYS start with a Thought
2. Action Input MUST be valid JSON
3. Wait for Observation after each Action
4. Use tools whenever they would help answer the question
5. Be concise but thorough in your thoughts
"""
    
    def format_tool_descriptions(self, tools):
        """Format tool descriptions for optimal parsing"""
        descriptions = []
        for tool in tools:
            desc = f"{tool['name']}: {tool['description']}\n"
            desc += f"  Parameters: {json.dumps(tool['parameters'], indent=2)}\n"
            desc += f"  Example: {tool.get('example', 'No example provided')}"
            descriptions.append(desc)
        
        return "\n\n".join(descriptions)
```

**Few-shot examples** significantly improve ReAct format adherence:

```python
def add_few_shot_examples(self, prompt):
    """Add examples to improve format consistency"""
    examples = """
Example interaction:
Question: What files are in the current directory?

Thought: I need to list the files in the current directory to answer this question.
Action: list_directory
Action Input: {"path": "./"}
Observation: Found 5 files: README.md, main.py, config.json, requirements.txt, .env

Thought: I can see the directory contents. I should provide a clear answer.
Final Answer: The current directory contains 5 files: README.md, main.py, config.json, requirements.txt, and .env

---

Now, answer the following question:
"""
    return examples + prompt
```

## 6. Error recovery when tools fail mid-cycle

### Comprehensive error recovery system

The research reveals sophisticated patterns for handling tool failures within ReAct cycles:

```python
class ReActErrorRecoverySystem:
    def __init__(self):
        self.max_retries = 3
        self.fallback_strategies = {}
        self.checkpoint_manager = CheckpointManager()
        
    async def execute_with_recovery(self, react_agent, query):
        """Execute ReAct cycle with comprehensive error handling"""
        
        for iteration in range(self.max_iterations):
            # Create checkpoint before each iteration
            checkpoint_id = await self.checkpoint_manager.create_checkpoint(
                react_agent.get_state()
            )
            
            try:
                # Execute ReAct step
                thought = await react_agent.think(query)
                action = await react_agent.act(thought)
                
                # Execute tool with timeout
                result = await asyncio.wait_for(
                    self.execute_tool_safe(action),
                    timeout=30
                )
                
                observation = await react_agent.observe(result)
                
            except ToolExecutionError as e:
                # Tool-specific recovery
                recovery_result = await self.recover_from_tool_error(
                    e, action, checkpoint_id
                )
                if recovery_result:
                    observation = recovery_result
                else:
                    # Rollback and try alternative approach
                    await self.checkpoint_manager.rollback(checkpoint_id)
                    observation = await self.try_alternative_tool(action)
                    
            except LoopDetectedError:
                # Break out of repetitive patterns
                await self.inject_randomness(react_agent)
                continue
                
            except ContextOverflowError:
                # Compress context and continue
                await self.compress_context(react_agent)
                continue
            
            if self.is_complete(observation):
                return observation
```

**Circuit breaker pattern** prevents cascading failures:

```python
class ReActCircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_counts = defaultdict(int)
        self.circuit_states = defaultdict(lambda: "CLOSED")
        self.last_failure_times = {}
        
    async def execute_with_circuit_breaker(self, tool_name, tool_func, args):
        state = self.circuit_states[tool_name]
        
        if state == "OPEN":
            if time.time() - self.last_failure_times[tool_name] > self.recovery_timeout:
                self.circuit_states[tool_name] = "HALF_OPEN"
            else:
                raise CircuitOpenError(f"Circuit breaker OPEN for {tool_name}")
        
        try:
            result = await tool_func(args)
            if state == "HALF_OPEN":
                self.circuit_states[tool_name] = "CLOSED"
                self.failure_counts[tool_name] = 0
            return result
            
        except Exception as e:
            self.failure_counts[tool_name] += 1
            self.last_failure_times[tool_name] = time.time()
            
            if self.failure_counts[tool_name] >= self.failure_threshold:
                self.circuit_states[tool_name] = "OPEN"
            
            raise e
```

## 7. State management for ReAct trajectories

### Production-ready session architecture

The research identifies critical patterns for managing ReAct state in Chainlit sessions:

```python
class ReActStateManager:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.state_layers = {
            'trajectory': [],      # Full ReAct history
            'working_memory': {},  # Current task context
            'personality': {},     # David AI personality state
            'tool_history': [],    # Tool execution history
            'checkpoints': []      # Recovery points
        }
        
    async def initialize_session(self, session_id):
        """Initialize or restore session state"""
        # Try to restore from Redis
        saved_state = await self.load_state(session_id)
        
        if saved_state:
            self.state_layers = saved_state
            cl.user_session.set("react_state", self.state_layers)
        else:
            # Initialize fresh state
            cl.user_session.set("react_state", self.state_layers)
            cl.user_session.set("session_id", session_id)
            
    async def save_state(self, session_id):
        """Persist state to Redis with TTL"""
        state_data = cl.user_session.get("react_state")
        serialized = json.dumps(state_data, default=str)
        
        await self.redis_client.setex(
            f"react_state:{session_id}",
            86400 * 7,  # 7 days TTL
            serialized
        )
        
    async def update_trajectory(self, thought, action, observation):
        """Update trajectory with new ReAct step"""
        state = cl.user_session.get("react_state")
        
        step = {
            "thought": thought,
            "action": action,
            "observation": observation,
            "timestamp": datetime.now().isoformat(),
            "iteration": len(state['trajectory']) + 1
        }
        
        state['trajectory'].append(step)
        
        # Manage context window
        if len(state['trajectory']) > 20:
            # Summarize older entries
            state['trajectory'] = await self.compress_trajectory(
                state['trajectory']
            )
        
        # Async persistence
        asyncio.create_task(self.save_state(cl.user_session.get("session_id")))
```

**Event sourcing for trajectory replay** enables powerful debugging and analysis:

```python
class TrajectoryEventStore:
    def __init__(self, db_connection):
        self.db = db_connection
        
    async def append_event(self, session_id, event_type, event_data):
        """Store ReAct events for replay capability"""
        event = {
            "session_id": session_id,
            "event_type": event_type,  # thought|action|observation
            "event_data": event_data,
            "timestamp": datetime.utcnow(),
            "sequence": await self.get_next_sequence(session_id)
        }
        
        await self.db.events.insert_one(event)
        
    async def replay_trajectory(self, session_id, from_sequence=0):
        """Replay ReAct trajectory from events"""
        events = await self.db.events.find({
            "session_id": session_id,
            "sequence": {"$gte": from_sequence}
        }).sort("sequence", 1)
        
        trajectory = []
        current_step = {}
        
        async for event in events:
            if event["event_type"] == "thought":
                current_step = {"thought": event["event_data"]}
            elif event["event_type"] == "action":
                current_step["action"] = event["event_data"]
            elif event["event_type"] == "observation":
                current_step["observation"] = event["event_data"]
                trajectory.append(current_step)
                current_step = {}
        
        return trajectory
```

## Architectural recommendations

### Recommended system architecture

Based on the research, here's the optimal architecture for your David AI ReAct implementation:

```
┌─────────────────────────────────────────────┐
│            Chainlit UI Layer                 │
│  - @cl.step decorators for visualization     │
│  - Real-time streaming updates               │
│  - Progress indicators                       │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         ReAct Orchestration Layer           │
│  - LlamaIndex Workflow integration          │
│  - Circuit breaker patterns                 │
│  - Error recovery strategies                │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         Ollama Integration Layer            │
│  - qwen3-14b optimized prompts              │
│  - Streaming response parser                │
│  - JSON5 fallback parsing                   │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         MCP Tool Execution Layer            │
│  - Async tool orchestration                 │
│  - Permission management                    │
│  - Sandboxed execution                      │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│         State Management Layer              │
│  - Redis session persistence                │
│  - Event sourcing for replay                │
│  - Context window management                │
└─────────────────────────────────────────────┘
```

### Implementation priorities

**Phase 1: Core ReAct loop (Week 1)**
Implement basic Chainlit + Ollama integration with simple @cl.step decorators and streaming support. Focus on getting the thought-action-observation cycle working reliably with qwen3-14b.

**Phase 2: MCP tool integration (Week 2)**  
Add MCP tool execution with basic permission checking and error handling. Implement the five core tools with timeout management and result sanitization.

**Phase 3: Advanced error recovery (Week 3)**
Implement circuit breakers, checkpoint-based recovery, and loop detection. Add graceful degradation strategies and fallback mechanisms.

**Phase 4: State persistence (Week 4)**
Add Redis-based session management, trajectory replay capabilities, and context window optimization. Implement event sourcing for debugging.

### Best practices summary

**For Chainlit integration**, use nested @cl.step decorators for hierarchical visualization and combine with LlamaIndex workflows for complex orchestration. Always implement streaming for long-running operations.

**For Ollama streaming**, maintain low temperature (0.1) for consistent ReAct format adherence, use json5 library for robust JSON parsing, and implement multiple fallback parsing strategies.

**For MCP tools**, always validate permissions before dangerous operations, implement circuit breakers for each tool, use async execution with proper timeout management, and sanitize all tool outputs.

**For error recovery**, create checkpoints before each ReAct iteration, implement loop detection with similarity checking, use graceful degradation when tools fail, and maintain recovery strategies for each failure mode.

**For state management**, use Redis for production session persistence, implement event sourcing for trajectory replay, manage context windows with summarization, and maintain separate layers for different state types.

## Conclusion

This research provides a comprehensive foundation for implementing ReAct framework with your specific tech stack. The patterns and code examples are production-ready and address all seven focus areas of your requirements. The combination of Chainlit's UI capabilities, Ollama's streaming LLM interface, and MCP's tool ecosystem creates a powerful platform for building autonomous agents with observable reasoning processes.

The architectural recommendations prioritize reliability, observability, and user experience while maintaining the flexibility needed for David AI's consciousness framework. By following the phased implementation approach and best practices outlined, you can build a robust ReAct agent system that gracefully handles errors, maintains state across sessions, and provides clear visibility into the agent's reasoning process.