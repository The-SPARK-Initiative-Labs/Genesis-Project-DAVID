

# **A Technical Report on the Implementation of Production-Grade Multi-Agent Systems in LangGraph**

## **I. Architecting a Production-Grade Multi-Agent System for Code Generation**

The development of sophisticated AI applications, particularly those tasked with complex, multi-step processes like code generation, necessitates an architectural approach that transcends the limitations of monolithic, single-agent systems. A robust architecture is the foundation upon which reliability, scalability, and maintainability are built. This section details the principles and patterns for designing a production-grade multi-agent system using a supervisor-worker model, with a specific focus on the implementation of a specialized 'coding specialist' agent.

### **1.1. The Supervisor-Worker Pattern: A Deep Dive**

The primary motivation for adopting a multi-agent architecture is a "divide-and-conquer" strategy, which posits that complex tasks are best solved by decomposing them into smaller, manageable sub-tasks handled by specialized agents.1 When a single agent is equipped with an extensive and diverse set of tools, its ability to reason effectively and select the appropriate tool diminishes, leading to poor decision-making and task failure.2 The Supervisor-Worker pattern directly addresses this challenge by establishing a clear hierarchy of control and responsibility.

In this model, a central "Supervisor" agent acts as an orchestrator or router.3 It receives an initial user request, analyzes it, and delegates the first sub-task to the most appropriate "expert" worker agent. Each worker is a specialized unit with a focused set of tools and a distinct purpose.4 Within the LangGraph framework, this pattern is elegantly represented as a state machine or graph. The Supervisor is a node whose primary function is to make routing decisions, while the workers are other nodes in the graph.5

The operational flow is cyclical and managed by the Supervisor. After a worker agent completes its assigned task, it returns its output to the shared state, and control reverts to the Supervisor node. The Supervisor then assesses the current state of the task—evaluating the worker's output in the context of the overall goal—and determines the next step. This could involve delegating a new task to another worker, sending the task back to the same worker for refinement, or, if the overall objective has been met, routing the workflow to a FINISH state to return the final answer.4 This explicit, centrally managed workflow provides significant architectural benefits:

* **Modularity:** Each agent is a self-contained component that can be developed, tested, and improved independently without impacting the rest of the system.4  
* **Scalability:** New capabilities can be added to the system by simply creating a new specialized worker agent and updating the Supervisor's routing logic to include it, avoiding the need to refactor existing components.4  
* **Specialization:** By limiting the scope of each worker, its prompt can be highly optimized with specific instructions and few-shot examples, leading to better performance on its designated task.5

For systems of even greater complexity, this pattern can be extended into a hierarchical supervisor model, or "supervisor of supervisors." In this advanced architecture, agents are organized into teams, each with its own team-level supervisor. A top-level supervisor then orchestrates these teams, delegating high-level objectives to the appropriate team supervisor, who in turn manages the individual workers within their team. This creates a robust and scalable system capable of managing intricate, multi-domain workflows.2 The choice of a Supervisor architecture within LangGraph is a deliberate engineering decision that prioritizes reliability and predictability over the more emergent, and often less controllable, behavior seen in decentralized or "conversational" agent frameworks.5 This explicit control is paramount for building systems that are debuggable and dependable in a production environment.

### **1.2. Designing the 'Coding Specialist' Agent: Subgraph vs. Specialized Tools**

A critical architectural decision in designing a system with a 'coding specialist' is how to implement this specialist. There are two primary approaches: implementing the agent as a self-contained, stateful workflow using a separate StateGraph (a subgraph), or defining it as a generalist agent equipped with a curated set of specialized coding tools.

The subgraph approach involves encapsulating the entire workflow of the coding specialist within its own StateGraph. This is ideal when the coding task is itself a complex, multi-step process, such as planning the code structure, writing the initial implementation, executing tests, and then refactoring based on the results. By defining the specialist as a subgraph, it can maintain its own private state schema, isolated from the main graph.2 This internal "scratchpad" can track file paths, test outputs, error logs, and other contextual information relevant only to the coding task, preventing this operational data from polluting the global state shared by all agents.12 This method aligns with the concept of building true "teams" of agents, where each team member is a capable, independent entity.2

Conversely, the specialized tools approach is simpler to implement initially. Here, the 'coding specialist' is not a distinct graph but rather a persona or a set of instructions given to a general-purpose agent that has access to a toolkit of coding-related functions, such as write\_file, read\_document, and execute\_code.7 While this reduces upfront complexity, it risks devolving into the monolithic agent problem as more tools are added, potentially confusing the agent and degrading its performance.3 The agent's entire reasoning process is confined to a single state machine, which may lack the robustness required for long-running, intricate coding assignments.

For any non-trivial coding task, the subgraph implementation is the superior architectural choice. While it requires a greater initial investment in defining the separate state and workflow, it provides unparalleled benefits in modularity, state isolation, and scalability. This approach treats the 'coding specialist' not merely as a function-caller but as a true expert with its own internal processes, a paradigm that is essential for building complex, reliable, and scalable agentic systems. The following table provides a detailed comparison of these two implementation strategies.

**Table 1: Comparison of Specialist Agent Implementations**

| Criterion | StateGraph (Subgraph) Implementation | Specialized Tools Implementation |
| :---- | :---- | :---- |
| **Modularity & Isolation** | **High.** The agent is a self-contained unit with its own state and logic. Changes are isolated and do not affect the parent graph.11 | **Low.** Tools are stateless functions. Logic is entangled with the calling agent's prompt and state, making changes riskier. |
| **State Management** | **Robust.** Supports a private, complex internal state (e.g., tracking file edits, test results). Ideal for multi-step tasks.2 | **Limited.** Relies on the parent agent's state. Difficult to manage task-specific context without polluting the global state. |
| **Complexity** | **Higher initial setup.** Requires defining a new state schema, nodes, and edges for the subgraph.12 | **Lower initial setup.** Requires only defining Python functions with @tool decorators.1 |
| **Reusability** | **High.** The entire agentic workflow can be compiled and reused as a single node in multiple parent graphs.12 | **Moderate.** Individual tools can be reused, but the collaborative logic between them must be re-implemented in each new agent. |
| **Debuggability** | **Clearer.** Can be debugged as an independent unit. LangSmith traces will show a distinct subgraph invocation.16 | **More difficult.** Tool failures and logical errors are intertwined with the parent agent's reasoning process, making root cause analysis harder. |

### **1.3. State Management Strategies for Agent Isolation and Collaboration**

State is the connective tissue of a LangGraph system; it is the shared memory that enables communication, context preservation, and collaboration between nodes.6 The state is typically defined by a

TypedDict schema, which acts as the data contract for the entire graph. The management of this state is critical to the system's performance and stability.

Two primary communication patterns emerge from different state management strategies. The first is the **Shared Scratchpad** model, where all agents in the graph read from and write to a single, global list of messages.5 This approach is simple to implement and offers complete transparency, as every agent can see the full history of operations performed by all other agents. However, this can lead to context window bloat, where the sheer volume of information overwhelms the LLM, causing it to become confused or distracted.2

The preferred method for complex, production-grade systems is the **Private Scratchpads with a Global Ledger** model. In this pattern, each specialized agent, implemented as a subgraph, maintains its own private, internal state (its "scratchpad"). It performs its multi-step task using this isolated context. Only the final, polished result of its work is passed back to the supervisor's global state (the "ledger").2 This enforces a strong separation of concerns and context isolation, preventing one agent's internal thought process from interfering with another's.20

A technical challenge arises when using subgraphs with private states: the parent graph and the subgraph may have different state schemas. LangGraph provides two mechanisms to handle this disparity. If the schemas have overlapping keys, LangGraph can automatically merge the state updates from the subgraph back into the parent graph.12 However, if the schemas are entirely distinct—which is often desirable for true isolation—an

**Adapter Node** must be implemented in the parent graph. This adapter node acts as a translator. Before invoking the subgraph, it transforms the relevant data from the parent's state into the format expected by the subgraph. After the subgraph completes its execution, the adapter node receives the subgraph's output and transforms it back into a format that can be merged into the parent's state.2 This pattern allows for the creation of fully encapsulated, reusable agentic components.

## **II. Mastering Tool Definition and Invocation with @tool**

Tools are the bridge between an agent's cognitive processes and its ability to interact with the external world. The correct definition and invocation of these tools are fundamental to the system's functionality. An error in this layer is not merely a bug but a failure of the agent to execute its intent. This section provides a comprehensive guide to defining robust tools using the @tool decorator, understanding their invocation lifecycle, and implementing custom tool nodes for advanced state manipulation.

### **2.1. Advanced Schema Definition with Pydantic and Type Annotations**

The recommended method for creating tools from Python functions is the @tool decorator.14 This decorator inspects the decorated function and automatically infers the tool's name from the function name, its arguments from the type hints, and its purpose from the docstring.23 This automatic inference underscores a critical principle: the tool's docstring is not mere documentation; it is a vital part of the functional API contract with the Large Language Model. The LLM does not interpret Python code; it interprets the natural language description provided in the docstring to determine whether, when, and how to use the tool. A vague or inaccurate docstring is functionally equivalent to a poorly designed and undocumented API endpoint, and it is a primary cause of tool invocation failures.25

For tools that accept multiple or complex arguments, relying on basic type hints is often insufficient to prevent ambiguity. To create a more robust and explicit schema, a Pydantic BaseModel should be used. By defining a Pydantic model and passing it to the @tool decorator via the args\_schema parameter, developers can enforce a rigid structure for the tool's inputs. This allows for detailed, field-level descriptions, default values, and complex validation rules, all of which are communicated to the LLM, significantly improving its ability to generate correct arguments.22

A more modern and concise alternative to a separate Pydantic model is the use of Python's typing.Annotated. This allows developers to embed descriptions directly into the function's signature, keeping the schema definition co-located with the implementation. For example, a parameter can be defined as code: Annotated.1 This annotation provides the same descriptive benefit to the LLM as a Pydantic field description but with improved code readability.

### **2.2. The Tool Invocation Lifecycle: From LLM Output to Python Execution**

Understanding the end-to-end process of tool invocation is essential for debugging and building resilient systems. The process is not a direct function call but a multi-step, message-based interaction orchestrated by the LangGraph runtime:

1. **Binding:** Tools are first "bound" to a specific LLM instance. This process provides the LLM with the JSON schemas of all available tools, making it aware of their capabilities and required input structures.27  
2. **Generation:** When the LLM, in its reasoning step, determines that it needs to use a tool, it does not execute the tool's code. Instead, it generates a special AIMessage object that contains a tool\_calls attribute. This attribute is a list of structured data objects, each containing the name of the tool to be called and a dictionary of arguments (args) that it believes are correct.27  
3. **Routing:** The LangGraph graph, through a conditional edge like the prebuilt tools\_condition, inspects the most recent AIMessage. If the tool\_calls attribute is present, it routes the control flow to a dedicated tool execution node.28  
4. **Execution:** This node, typically an instance of the prebuilt ToolNode, receives the state. It parses the tool\_calls from the AIMessage, finds the corresponding Python function for each requested tool, and invokes it, passing the args dictionary as input.27 It is at this precise point—the validation of the LLM-generated  
   args against the tool's Pydantic or type-hinted schema—that tool\_input validation errors occur.  
5. **Response:** The return value from the executed Python function is captured by the ToolNode. It wraps this result in a ToolMessage object, which includes the content of the result and the ID of the original tool call. This ToolMessage is then appended to the message list in the graph's state, providing the tool's output back to the LLM for its next reasoning cycle.29

This lifecycle reveals that a tool\_input error is fundamentally a data validation or deserialization failure. The LLM, acting as a data generator, has produced a malformed or incomplete data structure (args) that the data consumer (the Python function) cannot accept. This reframes the problem from "fixing the tool's code" to either "improving the data generator (the LLM's prompt and tool schemas)" or "making the data consumer more resilient to malformed inputs."

### **2.3. Implementing Custom Tool Nodes for Enhanced State Manipulation**

While the prebuilt ToolNode is sufficient for many use cases, it possesses a significant architectural limitation: it is designed to only update the messages key within the graph's state.30 Any value returned by a tool is automatically wrapped in a

ToolMessage and appended to this list. This is inadequate for more advanced agents that require tools to directly manipulate other parts of the graph's state—for instance, incrementing an attempt counter, updating a configuration dictionary, or modifying a list of processed items.

To overcome this, a custom tool node must be implemented. This custom node replaces the default ToolNode in the graph and provides more flexible logic for handling tool outputs. The implementation of such a node involves checking the type of the value returned by the invoked tool. If the return value is a standard Python type (e.g., a string, integer, or dictionary), the custom node behaves like the default ToolNode, wrapping the result in a ToolMessage.

However, the true power of a custom node is unlocked when tools are designed to return a LangGraph Command object. A Command allows a tool to issue direct instructions to the graph runtime, such as updating specific keys in the state or forcing the graph to goto a different node.2 The custom tool node can inspect the tool's return value, and if it is a

Command, it can return the command directly. The LangGraph runtime will then execute the state updates and routing specified in the command. This advanced pattern enables the creation of powerful tools that can actively participate in the graph's control flow and state management, moving beyond the simple request-response paradigm of the default ToolNode.30

## **III. Diagnosing and Resolving tool\_input Validation Failures**

Tool input validation failures are among the most common and frustrating challenges in developing agentic systems. These errors arise when the LLM's generated arguments for a tool call do not conform to the schema defined in the tool's Python function. Addressing these failures requires moving beyond simple bug fixes to implementing multi-layered defensive strategies that acknowledge the inherent unreliability of LLM-driven tool invocation.

### **3.1. Root Cause Analysis: Why LLMs Fail to Adhere to Tool Schemas**

The failure of an LLM to generate schema-compliant tool arguments is not a random event but a predictable outcome of the technology's probabilistic nature. These failures can be categorized into several common modes:

* **Argument Mismatch:** This is the most frequent failure type. The LLM may omit a required argument, provide arguments with the incorrect data type (e.g., passing a string "five" where an integer 5 is required), or "hallucinate" argument names that are not part of the tool's schema.32  
* **Syntactic Formatting Errors:** The LLM may generate a JSON object for the arguments that is syntactically incorrect (e.g., with missing commas or mismatched brackets), making it impossible for the downstream parser to read.  
* **Incorrect Tool Selection:** The LLM might attempt to call a tool that is not available in its bound toolset or select a tool that is semantically inappropriate for the current sub-task.32

These issues are often exacerbated by underlying design flaws, such as overly complex tool schemas with many nested objects, ambiguous or poorly written tool and argument descriptions, or simply using a model that lacks the requisite reasoning capability for the complexity of the tools provided.27 A production system must treat tool-calling not as a reliable Remote Procedure Call (RPC) with a machine-enforced contract, but as an inherently unreliable RPC where the contract is merely a suggestion to the LLM. Therefore, the system must be architected with the assumption that validation failures are a normal part of operation and must include robust, automated recovery paths.

### **3.2. Defensive Error Handling within the Tool Node**

The first line of defense against tool validation errors is to handle them gracefully within the tool execution node itself, preventing the entire graph from crashing.

#### **Strategy 1: Simple Try/Except**

The most straightforward strategy is to wrap the tool invocation logic inside the tool node within a try...except block that specifically catches validation errors like pydantic.ValidationError or TypeError.1 When an exception is caught, instead of allowing it to propagate, the node should format a descriptive error message. This message, containing details from the exception, is then wrapped in a

ToolMessage and returned to the graph state. This provides direct feedback to the LLM on its next reasoning turn, informing it that its previous attempt failed and explaining why (e.g., "Error: Missing required argument 'content'"). This gives the LLM an opportunity to self-correct by generating a new, valid tool call.

#### **Strategy 2: LLM Fallback**

For mission-critical applications where a successful tool call is paramount, a fallback strategy can be employed. If an initial attempt to generate a tool call with a faster, more cost-effective model fails, the error-handling logic can trigger a second attempt using a more powerful, albeit more expensive, model (e.g., falling back from a local Ollama Llama 3 model to GPT-4).32 This more capable model is generally better at understanding and adhering to complex schemas, increasing the probability of a successful invocation. This approach can be implemented as part of a

with\_fallbacks chain, where the more powerful model is designated as the recovery path.

### **3.3. Implementing Self-Correction Loops: Feeding Errors Back to the Agent**

The most robust and sophisticated strategy for handling validation errors is to build an explicit self-correction loop into the graph's architecture. This pattern treats the error not just as feedback for the next turn but as an event that triggers an immediate, automated retry cycle with enhanced context.33

The implementation involves several components:

1. **Custom Exception:** A custom exception class is defined (e.g., ToolValidationException) that is designed to capture both the original validation error and the full tool\_call object that caused it.  
2. **Modified Tool Node:** The tool execution node is modified to raise this custom exception upon a validation failure.  
3. **Conditional Routing:** A conditional edge is added to the graph originating from the tool node. This edge's logic checks for the ToolValidationException. If the exception occurred, it routes the graph to a dedicated "error formatting" node; otherwise, it proceeds to the normal next step (typically back to the LLM).  
4. **Error Formatting Node:** This node is responsible for constructing a rich, corrective context for the LLM. It takes the exception details and crafts a new sequence of messages to be added to the state. This sequence typically includes: the original AIMessage containing the faulty tool call, a ToolMessage containing the precise validation error, and a new, instructional HumanMessage that explicitly tells the LLM to re-attempt the tool call with corrected arguments based on the provided error message.33  
5. **Looping Back:** The output of the error formatting node is then routed directly back to the main LLM reasoning node. This provides the LLM with immediate, actionable feedback, allowing it to learn from its mistake and attempt a corrected tool call within the same operational cycle.

The choice between these strategies involves a trade-off between implementation complexity, operational cost, and resilience. The following table analyzes these trade-offs to guide architectural decisions.

**Table 2: Tool Error Handling Strategies: A Comparative Analysis**

| Strategy | Description | Implementation Complexity | Resilience | Cost Impact | Best Use Case |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Try/Except** | Catches validation errors and returns an error message to the LLM in the next turn.32 | **Low.** A simple try...except block within the tool node. | **Low.** Relies on the LLM to fix the error on its own, which may fail repeatedly. | **Low.** Only adds tokens for the error message. | Non-critical tasks, initial development, and debugging. |
| **LLM Fallback** | Retries the tool-generating call with a more powerful (and expensive) LLM upon failure.32 | **Medium.** Requires configuring a fallback chain and managing multiple model clients. | **High.** More capable models are significantly better at adhering to complex schemas. | **High.** Invokes a premium model, potentially 10x the cost of the initial attempt. | High-value, critical tasks where success is paramount and justifies the cost. |
| **Self-Correction Loop** | Feeds the error and a corrective prompt back to the *same* LLM in an immediate, automated retry loop.33 | **High.** Requires custom graph logic with conditional edges and state manipulation for error context. | **Medium-High.** Effective for many common errors but may still fail if the base model is incapable of understanding the correction. | **Medium.** Avoids using a premium model but increases token count by adding the error context to the prompt. | Balanced approach for production systems aiming for high reliability without incurring premium model costs on every failure. |
| **Circuit Breaker** | Prevents the agent from repeatedly calling a tool that is consistently failing, breaking infinite loops.35 | **High.** Requires implementing a stateful counter and timer logic within the graph's state. | **Very High (for loops).** Explicitly designed to stop persistent, unrecoverable failures. | **Low.** Prevents wasted LLM calls, saving costs during outages or persistent bugs. | Protecting against infinite loops and cascading failures, especially for tools calling external, potentially unreliable APIs. |

## **IV. A Robust Development Lifecycle: Debugging and Unit Testing**

Building production-grade agentic systems demands a disciplined development lifecycle that emphasizes proactive quality assurance over reactive bug-fixing. The non-deterministic nature of LLMs makes traditional debugging methods inadequate. A robust lifecycle must therefore incorporate advanced observability tools, systematic unit testing of deterministic components, and reliable integration testing strategies.

### **4.1. Strategic Debugging: Leveraging LangSmith and LangGraph Studio**

Debugging an agent's behavior is challenging because its logic is emergent and opaque.13 To address this, observability cannot be an afterthought; it must be a core, integrated part of the development process. In the LangChain ecosystem, LangSmith is the indispensable platform for this purpose.16 It provides a complete, persistent trace for every execution of the graph. This allows developers to retrospectively analyze the agent's "thought process" by inspecting the precise inputs, outputs, and latencies of every node in the graph, from LLM calls to tool executions. This granular visibility is crucial for identifying the root cause of failures, such as a malformed prompt, an unexpected tool output, or a faulty routing decision.13 An architecture that does not include a comprehensive tracing solution like LangSmith from the outset is fundamentally un-debuggable and unsuitable for production.

For more interactive, real-time debugging, LangGraph Studio offers a visual interface for the agent's graph structure.37 Its key feature is the ability to set breakpoints on specific nodes, which pauses the graph's execution at that point. When paused, a developer can inspect the full state of the graph, verifying that data is being passed and transformed as expected. Crucially, the state can be manually edited before resuming execution. This capability is exceptionally powerful for iterative development, allowing for rapid experimentation with different prompts or logical fixes without needing to restart the entire workflow from the beginning.37

### **4.2. Unit Testing Patterns for LangGraph Tools and Nodes**

The most effective development strategy for agentic systems is a bottom-up, component-based approach. This involves building from the most deterministic parts of the system (the tools) to the least deterministic (the full agentic loop). A "tools-first" development philosophy dictates that tools should be designed, implemented, and rigorously tested as standalone components before they are ever exposed to an LLM.13

A function decorated with @tool is, at its core, a standard Python function and should be tested as such. Using a testing framework like pytest, developers can write unit tests that call the tool's underlying function directly, passing in various inputs and asserting that the outputs are correct. This ensures the core business logic of the tool is sound. For decorators that add complex behavior, it may be necessary to test the undecorated function directly or to use mocking libraries to isolate the function from the decorator's effects.26

Similarly, each node in a LangGraph workflow is a function that can and should be tested in isolation.40 A unit test for a node involves creating a mock input

state dictionary that simulates the state of the graph at the point the node would be called. The node function is then invoked with this mock state, and assertions are made against the returned dictionary to verify that it contains the expected state updates. Any external dependencies within the node, such as LLM clients or API calls, should be mocked to ensure the tests are deterministic, fast, and can run without network access or API keys.41 This bottom-up testing methodology systematically reduces uncertainty; when a failure occurs in the fully assembled system, developers can have high confidence that the issue lies with the agent's reasoning or prompting, as the foundational components have already been verified.

### **4.3. Integration Testing the Agentic Workflow**

After the individual components (tools and nodes) have been unit-tested, the entire compiled graph must be tested to validate the routing logic and state transitions between nodes.41 Performing end-to-end tests that involve live LLM calls is problematic, as they are slow, incur API costs, and are non-deterministic, making consistent assertions impossible.

The recommended best practice for integration testing is to use response caching. The test suite is executed once against the live LLM, and all model responses are captured and stored in a cache. For all subsequent test runs, the LLM calls are patched to return the cached responses instead of making live API calls. This approach makes the integration tests fast, free to run, and fully deterministic, allowing them to be incorporated into a standard CI/CD pipeline. These tests verify that changes to the graph's structure or node logic have not introduced regressions in the overall workflow.41 For more advanced evaluation, LangSmith can be integrated with

pytest to create test suites, where each test run is logged as an experiment. This allows for the programmatic evaluation of agent outputs against a reference dataset and the tracking of performance over time.42

## **V. Advanced Resilience and Security Engineering for Agentic Systems**

Moving an agentic system from a prototype to a production service requires a rigorous focus on non-functional requirements, primarily resilience and security. A production system must be able to withstand persistent failures without entering catastrophic failure states, and its actions—especially the execution of generated code—must be performed within a secure, isolated environment.

### **5.1. Adapting the Circuit Breaker Pattern to Prevent Infinite Tool-Call Loops**

A critical failure mode in agentic systems is the infinite loop. This often occurs when an agent repeatedly attempts to call a tool that consistently fails for a reason the agent cannot resolve through its self-correction mechanisms. This can lead to runaway API costs and system resource exhaustion. The Circuit Breaker pattern, a staple of resilient microservice architectures, can be adapted to LangGraph to mitigate this risk.35

The pattern operates as a state machine for each tool, with three states:

* **Closed:** The default state. Tool calls are permitted. A counter tracks consecutive failures. If the failure count exceeds a predefined threshold, the circuit "trips" and moves to the Open state.  
* **Open:** Tool calls are immediately rejected without being attempted. A timer is started. When the timer expires, the circuit moves to the Half-Open state.  
* **Half-Open:** A single, trial tool call is permitted. If it succeeds, the circuit returns to the Closed state, resetting the failure counter. If it fails, the circuit trips back to the Open state, restarting the timer.

This pattern can be implemented directly within the LangGraph state and workflow:

1. **State Augmentation:** The main AgentState TypedDict is extended to include a dictionary named circuit\_breakers. This dictionary will map each tool's name to an object or dictionary containing its current state ('CLOSED', 'OPEN', 'HALF\_OPEN'), failure count, and the timestamp of the last failure.  
2. **Pre-flight Check Node:** A new node is inserted into the graph immediately before the tool execution node. This "pre-flight" node checks the circuit\_breakers dictionary in the state for the tool the LLM is attempting to call. If the circuit for that tool is in the 'OPEN' state, this node bypasses the tool execution node entirely and routes the graph directly to an error-handling path, returning a message that the tool is temporarily unavailable.  
3. **State Updates in Tool Node:** The tool execution node is modified to update the circuit breaker's state. On a successful tool call, it resets the failure counter for that tool to zero. On a tool failure, it increments the counter. If the counter exceeds the threshold, it transitions the tool's state to 'OPEN' and records the current time.

By integrating this pattern, the agent becomes a more robust service. It can handle transient errors through retries while protecting itself and downstream systems from the impact of persistent faults, gracefully degrading its functionality instead of failing catastrophically.

### **5.2. Secure Code Execution: Implementing and Navigating the langchain-sandbox**

The primary function of a 'coding specialist' agent—writing and executing code—presents a significant security risk. Executing LLM-generated code directly on a host machine is untenable in a production environment, as it opens the door to arbitrary code execution vulnerabilities.1

The langchain-sandbox package provides a solution by offering a PyodideSandboxTool. This tool executes Python code within a Pyodide (Python compiled to WebAssembly) environment, which is isolated from the host system.20 This sandbox prevents the executed code from accessing the host's filesystem or network, mitigating the risk of malicious or destructive operations.

However, this security comes with a critical limitation: the inability to perform file I/O on the host system is a major constraint for a coding agent that needs to read, modify, and write to a project's codebase.20 This conflict between security and functionality requires an architectural workaround. The agent should not interact with the real filesystem during its development loop. Instead, a

**virtual filesystem** should be managed within the LangGraph state.

This is implemented by adding a dictionary to the AgentState (e.g., virtual\_fs: Dict\[str, str\]), which maps file paths to their string content. The agent is then provided with a set of tools that operate exclusively on this in-memory dictionary, such as write\_to\_virtual\_file(path, content), read\_from\_virtual\_file(path), and list\_virtual\_files(). The PyodideSandboxTool is used to execute code snippets or run tests against the code held within this virtual filesystem. Only after the entire coding task is complete and has passed a final human approval step is a trusted, non-sandboxed tool invoked to write the contents of the virtual filesystem to the actual disk. This architecture reconciles the need for secure code execution with the functional requirement of file manipulation.

### **5.3. Strategies for Managing Long-Running and Asynchronous Tasks**

Coding and other complex agentic tasks are often long-running processes that cannot be completed within a single, synchronous request-response cycle. Furthermore, critical actions, such as committing code to a repository or deploying an application, should require explicit human oversight. LangGraph's persistence and human-in-the-loop capabilities are designed to manage these scenarios.

The interrupt() function provides the core mechanism for pausing a graph's execution to await human input.44 When a node calls

interrupt(), the graph's current state is saved to its configured persistence layer (the "checkpointer"), and execution is halted. This allows a human to review the agent's proposed action (e.g., the final code to be committed). The user can then resume the graph's execution by invoking it with a Command object containing their feedback (e.g., 'approve' or 'reject').47

This entire process is underpinned by LangGraph's checkpointer system. For any production application, an in-memory checkpointer is insufficient. A durable backend, such as a Postgres or Redis database, must be configured.38 This ensures that the state of long-running or interrupted agent tasks can survive application restarts and machine failures, providing the durability and reliability expected of a production service.36

## **VI. Integrated Solution: A Complete Multi-Agent System in the David AI Stack**

This final section synthesizes the architectural patterns, error-handling techniques, and development practices discussed previously into a single, cohesive code implementation. It serves as a practical blueprint for building the described multi-agent coding specialist system using the specified technology stack of LangGraph, Ollama, and Chainlit.

### **6.1. End-to-End Implementation with LangGraph, Ollama, and Chainlit**

The integrated solution consists of three primary components that work in concert:

* **LLM Backend (Ollama):** The system will be configured to use a local Ollama instance to serve a powerful open-source model, such as Llama 3 70B Instruct or a specialized coding model like Code Llama. This model will provide the core reasoning capabilities for all agents within the graph. The integration will be handled via the standard LangChain Ollama chat model wrappers.  
* **Agent Framework (LangGraph):** The entire agentic workflow will be constructed using LangGraph. The implementation will feature a top-level StateGraph for the Supervisor agent. This Supervisor will manage the overall task and route control to a 'Coding Specialist' agent, which will be implemented as a separate, compiled StateGraph and integrated as a subgraph. This hierarchical structure provides the modularity and state isolation required for a robust system.  
* **User Interface (Chainlit):** A user-facing interface will be built using Chainlit. This interface will provide a chat window for users to submit coding requests. It will also serve as the critical point of interaction for the human-in-the-loop steps, presenting the agent's proposed code for review and providing buttons for the user to approve or reject the action, thus resuming the paused LangGraph execution.

### **6.2. Code Walkthrough: Tying It All Together**

The following is a commented, end-to-end Python script that demonstrates the full implementation. It integrates all the key concepts discussed in this report, including state definitions, tool creation, subgraph architecture, custom tool nodes for error handling, circuit breakers, sandboxed code execution with a virtual filesystem, and human-in-the-loop interruptions.

Python

\# \--- 0\. Imports and Environment Setup \---  
import os  
import operator  
import json  
from typing import TypedDict, Annotated, List, Dict, Literal  
from langchain\_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage  
from langchain\_core.tools import tool  
from langchain\_community.chat\_models import ChatOllama  
from langgraph.graph import StateGraph, START, END  
from langgraph.prebuilt import ToolNode  
from langgraph.graph.message import add\_messages  
from langgraph.types import Command, interrupt  
from langchain\_sandbox import PyodideSandboxTool  
import time

\# Configure the LLM using Ollama  
\# Ensure Ollama is running and has pulled the specified model (e.g., \`ollama run llama3\`)  
llm \= ChatOllama(model="llama3", temperature=0)

\# \--- 1\. State Definitions (Section 1.3) \---

\# State for the Coding Specialist Subgraph  
class CoderState(TypedDict):  
    messages: Annotated, add\_messages\]  
    \# Virtual filesystem to work around sandbox limitations (Section 5.2)  
    virtual\_fs: Dict\[str, str\]  
    \# Circuit breaker state for the code execution tool (Section 5.1)  
    test\_circuit\_breaker: Dict

\# State for the main Supervisor Graph  
class SupervisorState(TypedDict):  
    messages: Annotated, add\_messages\]  
    next\_agent: str

\# \--- 2\. Tool Definitions (Section 2.1 & 5.2) \---

\# Sandboxed code execution tool  
sandbox\_tool \= PyodideSandboxTool(allow\_net=False) \# Security: disable network access

@tool  
def read\_virtual\_file(filepath: Annotated) \-\> str:  
    """Reads the content of a file from the virtual filesystem."""  
    \# This tool will be passed the CoderState, which contains the virtual\_fs  
    \# We will use a custom tool node to inject the state.  
    \# For now, the logic assumes it gets the filesystem dict.  
    \# This is a placeholder for the logic that will be in the custom node.  
    return "Error: State not injected. Implement custom tool node."

@tool  
def write\_to\_virtual\_file(filepath: Annotated,  
                          content: Annotated) \-\> str:  
    """Writes or overwrites a file in the virtual filesystem."""  
    \# Placeholder logic  
    return "Error: State not injected. Implement custom tool node."

\# \--- 3\. Coding Specialist Subgraph (Section 1.2) \---

\# Create a tool executor for the coder agent's tools  
coder\_tools \= \[read\_virtual\_file, write\_to\_virtual\_file, sandbox\_tool\]

\# Custom ToolNode to handle state and circuit breaking (Section 2.3 & 5.1)  
def custom\_coder\_tool\_node(state: CoderState):  
    """  
    Custom tool node that:  
    1\. Injects the virtual\_fs into file tools.  
    2\. Implements a circuit breaker for the sandbox tool.  
    """  
    last\_message \= state\['messages'\]\[-1\]  
    tool\_messages \=

    for tool\_call in last\_message.tool\_calls:  
        tool\_name \= tool\_call\['name'\]  
        args \= tool\_call\['args'\]

        \# Circuit Breaker Logic for sandbox\_tool  
        if tool\_name \== sandbox\_tool.name:  
            cb \= state.get('test\_circuit\_breaker', {'failures': 0, 'state': 'CLOSED', 'open\_time': 0})  
            if cb\['state'\] \== 'OPEN':  
                if time.time() \- cb\['open\_time'\] \> 30: \# 30-second timeout  
                    cb\['state'\] \= 'HALF\_OPEN'  
                else:  
                    tool\_messages.append(ToolMessage(content=f"Circuit breaker is OPEN for {tool\_name}. Call rejected.", tool\_call\_id=tool\_call\['id'\]))  
                    continue \# Skip this tool call

        \# Execute tool  
        try:  
            if tool\_name \== read\_virtual\_file.name:  
                result \= state\['virtual\_fs'\].get(args\['filepath'\], "File not found.")  
            elif tool\_name \== write\_to\_virtual\_file.name:  
                state\['virtual\_fs'\]\[args\['filepath'\]\] \= args\['content'\]  
                result \= f"Successfully wrote to {args\['filepath'\]}."  
            elif tool\_name \== sandbox\_tool.name:  
                result \= sandbox\_tool.invoke(args)  
            else:  
                 result \= "Tool not found."

            \# Handle success for circuit breaker  
            if tool\_name \== sandbox\_tool.name:  
                cb\['failures'\] \= 0  
                cb\['state'\] \= 'CLOSED'  
                state\['test\_circuit\_breaker'\] \= cb

            tool\_messages.append(ToolMessage(content=str(result), tool\_call\_id=tool\_call\['id'\]))

        except Exception as e:  
            \# Handle failure for circuit breaker  
            if tool\_name \== sandbox\_tool.name:  
                cb\['failures'\] \+= 1  
                if cb\['failures'\] \>= 3:  
                    cb\['state'\] \= 'OPEN'  
                    cb\['open\_time'\] \= time.time()  
                state\['test\_circuit\_breaker'\] \= cb

            \# Self-correction feedback (Section 3.3)  
            error\_message \= f"Error executing tool {tool\_name}: {repr(e)}. Please check your arguments and try again."  
            tool\_messages.append(ToolMessage(content=error\_message, tool\_call\_id=tool\_call\['id'\]))

    return {"messages": tool\_messages}

\# Coder agent node  
def coder\_agent\_node(state: CoderState):  
    """The primary reasoning node for the coding specialist."""  
    response \= llm.bind\_tools(coder\_tools).invoke(state\['messages'\])  
    return {"messages": \[response\]}

\# Conditional edge for the coder  
def coder\_router(state: CoderState):  
    if isinstance(state\['messages'\]\[-1\], AIMessage) and state\['messages'\]\[-1\].tool\_calls:  
        return "tools"  
    return END

\# Build the coder subgraph  
coder\_graph\_builder \= StateGraph(CoderState)  
coder\_graph\_builder.add\_node("agent", coder\_agent\_node)  
coder\_graph\_builder.add\_node("tools", custom\_coder\_tool\_node)  
coder\_graph\_builder.add\_edge(START, "agent")  
coder\_graph\_builder.add\_conditional\_edges("agent", coder\_router)  
coder\_graph\_builder.add\_edge("tools", "agent")  
coder\_subgraph \= coder\_graph\_builder.compile()

\# \--- 4\. Supervisor Graph (Section 1.1) \---

\# Node that wraps and calls the coder subgraph  
def coding\_specialist\_node(state: SupervisorState):  
    \# Adapter logic (Section 1.3)  
    initial\_coder\_state \= {  
        "messages": state\['messages'\],  
        "virtual\_fs": {},  
        "test\_circuit\_breaker": {'failures': 0, 'state': 'CLOSED', 'open\_time': 0}  
    }  
    final\_coder\_state \= coder\_subgraph.invoke(initial\_coder\_state)  
    \# Return final message and signal completion  
    return {"messages": final\_coder\_state\['messages'\]\[-1:\], "next\_agent": "FINISH"}

\# Human-in-the-loop node for final approval (Section 5.3)  
def final\_approval\_node(state: SupervisorState):  
    """Pause for human approval before finishing."""  
    last\_agent\_message \= state\['messages'\]\[-1\].content  
    print("--- PROPOSED FINAL RESPONSE \---")  
    print(last\_agent\_message)  
    \# This will pause the graph execution  
    interrupt()  
    \# When resumed, the graph will continue to the end.  
    return {}

\# Supervisor agent node  
def supervisor\_agent\_node(state: SupervisorState):  
    \# For this example, we will always route to the coder.  
    \# A more complex system would have more workers and routing logic.  
    return {"next\_agent": "Coder"}

\# Supervisor router  
def supervisor\_router(state: SupervisorState):  
    if state\['next\_agent'\] \== "Coder":  
        return "Coder"  
    else: \# FINISH  
        return "FinalApproval"

\# Build the supervisor graph  
supervisor\_graph\_builder \= StateGraph(SupervisorState)  
supervisor\_graph\_builder.add\_node("Supervisor", supervisor\_agent\_node)  
supervisor\_graph\_builder.add\_node("Coder", coding\_specialist\_node)  
supervisor\_graph\_builder.add\_node("FinalApproval", final\_approval\_node)  
supervisor\_graph\_builder.add\_edge(START, "Supervisor")  
supervisor\_graph\_builder.add\_conditional\_edges("Supervisor", supervisor\_router, {"Coder": "Coder", "FinalApproval": "FinalApproval"})  
supervisor\_graph\_builder.add\_edge("Coder", "Supervisor")  
supervisor\_graph\_builder.add\_edge("FinalApproval", END)

\# Compile the final graph with a checkpointer for interruptions  
from langgraph.checkpoint.memory import MemorySaver  
memory \= MemorySaver()  
final\_graph \= supervisor\_graph\_builder.compile(checkpointer=memory)

\# \--- 5\. Running the System (Example with Chainlit) \---

\# This part would be integrated into a Chainlit application.  
\# For demonstration, we simulate the interaction here.

config \= {"configurable": {"thread\_id": "coding-thread-1"}}  
user\_input \= "Write a python function that calculates the nth fibonacci number and then write a test for it using pytest."

\# Stream the events to simulate the run  
events \= final\_graph.stream({"messages": \[HumanMessage(content=user\_input)\]}, config, stream\_mode="values")  
for event in events:  
    if "messages" in event:  
        event\["messages"\]\[-1\].pretty\_print()

\# Simulate human approval  
\# In a real app, this would come from the Chainlit UI  
print("\\n--- HUMAN APPROVAL REQUIRED \---")  
approval\_input \= input("Type 'approve' to finish: ")  
if approval\_input.lower() \== 'approve':  
    \# Resume the graph from the interrupted state  
    final\_graph.invoke(None, config)  
    print("\\n--- GRAPH EXECUTION COMPLETED \---")  
else:  
    print("\\n--- GRAPH EXECUTION REJECTED \---")

### **6.3. Recommendations for Performance Tuning and Scalability**

While the provided code serves as a robust blueprint, several considerations are crucial for deploying and scaling such a system in a production environment.

* **Model Selection:** The choice of LLM has a significant impact on both performance and cost. It is advisable to use a tiered model strategy. For simpler, less cognitively demanding tasks like routing decisions within the Supervisor, a smaller, faster, and cheaper model can be used. For the core reasoning tasks within the 'Coding Specialist' agent, a larger, more capable model is necessary. This hybrid approach optimizes both latency and operational expenditure.  
* **Asynchronous Execution:** For tools that are I/O-bound, such as those making external API calls (though disabled in this secure example), their Python functions should be defined as asynchronous (async def). LangGraph's ToolNode and custom nodes can execute these asynchronous tools concurrently, preventing the entire graph from blocking on a single slow operation and thereby improving overall throughput.  
* **State Management at Scale:** The MemorySaver checkpointer used in the example is suitable for development and testing, but it is not durable and will lose state if the application restarts. For any production deployment, a persistent checkpointer backend is mandatory. Options like langgraph-postgres or a custom Redis-based checkpointer provide the durability needed to reliably manage the state of long-running and interrupted agent sessions, ensuring the system can scale and recover from failures.38  
* **Audit Trail and Observability:** The integration of LangSmith should be considered a day-one requirement. It provides an immutable, detailed audit trail of every decision, tool call, and state transition made by every agent in the system. This level of observability is not just a debugging tool; it is a critical component for compliance, security analysis, performance monitoring, and gaining a deep understanding of the system's emergent behavior over time.17

By adhering to these architectural principles and implementation patterns, it is possible to construct a multi-agent system that is not only highly capable but also robust, secure, and ready for the rigors of a production environment.

#### **Works cited**

1. Multi-agent network \- GitHub Pages, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/tutorials/multi\_agent/multi-agent-collaboration/](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)  
2. LangGraph Multi-Agent Systems \- Overview, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/concepts/multi\_agent/](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)  
3. Multi-agent System Design Patterns | LangGraph | by Prince Krampah | Medium, accessed August 24, 2025, [https://medium.com/@princekrampah/multi-agent-architecture-in-multi-agent-systems-multi-agent-system-design-patterns-langgraph-b92e934bf843](https://medium.com/@princekrampah/multi-agent-architecture-in-multi-agent-systems-multi-agent-system-design-patterns-langgraph-b92e934bf843)  
4. Multi-Agent System Tutorial with LangGraph \- FutureSmart AI Blog, accessed August 24, 2025, [https://blog.futuresmart.ai/multi-agent-system-with-langgraph](https://blog.futuresmart.ai/multi-agent-system-with-langgraph)  
5. LangGraph: Multi-Agent Workflows \- LangChain Blog, accessed August 24, 2025, [https://blog.langchain.com/langgraph-multi-agent-workflows/](https://blog.langchain.com/langgraph-multi-agent-workflows/)  
6. state graph node \- GitHub Pages, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/concepts/low\_level/](https://langchain-ai.github.io/langgraph/concepts/low_level/)  
7. LangGraph: Hierarchical Agent Teams \- Kaggle, accessed August 24, 2025, [https://www.kaggle.com/code/ksmooi/langgraph-hierarchical-agent-teams](https://www.kaggle.com/code/ksmooi/langgraph-hierarchical-agent-teams)  
8. LangGraph Supervisor: A Library for Hierarchical Multi-Agent Systems, accessed August 24, 2025, [https://changelog.langchain.com/announcements/langgraph-supervisor-a-library-for-hierarchical-multi-agent-systems](https://changelog.langchain.com/announcements/langgraph-supervisor-a-library-for-hierarchical-multi-agent-systems)  
9. Hierarchical multi-agent systems with LangGraph \- YouTube, accessed August 24, 2025, [https://www.youtube.com/watch?v=B\_0TNuYi56w](https://www.youtube.com/watch?v=B_0TNuYi56w)  
10. Building Smart Agentic AI Teams with Hierarchical Architecture using LangGraph and WatsonX/Ollama (with Code) | by Diwakar Kumar | Medium, accessed August 24, 2025, [https://medium.com/@diwakarkumar\_18755/building-smart-ai-teams-with-hierarchical-architecture-using-langgraph-with-code-8744a9219aa3](https://medium.com/@diwakarkumar_18755/building-smart-ai-teams-with-hierarchical-architecture-using-langgraph-with-code-8744a9219aa3)  
11. Built with LangGraph\! \#23: Subgraphs | by Okan Yenigün | Aug, 2025 | AI Mind, accessed August 24, 2025, [https://pub.aimind.so/built-with-langgraph-23-subgraphs-8b7e08529bbf](https://pub.aimind.so/built-with-langgraph-23-subgraphs-8b7e08529bbf)  
12. Building AI Agents Using LangGraph: Part 10 — Leveraging Subgraphs for Multi-Agent Systems | by HARSHA J S, accessed August 24, 2025, [https://harshaselvi.medium.com/building-ai-agents-using-langgraph-part-10-leveraging-subgraphs-for-multi-agent-systems-4937932dd92c](https://harshaselvi.medium.com/building-ai-agents-using-langgraph-part-10-leveraging-subgraphs-for-multi-agent-systems-4937932dd92c)  
13. I wrote an AI Agent with LangGraph that works better than I expected. Here are 10 learnings., accessed August 24, 2025, [https://www.reddit.com/r/LangChain/comments/1m8vo19/i\_wrote\_an\_ai\_agent\_with\_langgraph\_that\_works/](https://www.reddit.com/r/LangChain/comments/1m8vo19/i_wrote_an_ai_agent_with_langgraph_that_works/)  
14. Tools | 🦜️ LangChain \- Python LangChain, accessed August 24, 2025, [https://python.langchain.com/docs/concepts/tools/](https://python.langchain.com/docs/concepts/tools/)  
15. LangGraph Subgraphs: A Guide to Modular AI Agents Development \- DEV Community, accessed August 24, 2025, [https://dev.to/sreeni5018/langgraph-subgraphs-a-guide-to-modular-ai-agents-development-31ob](https://dev.to/sreeni5018/langgraph-subgraphs-a-guide-to-modular-ai-agents-development-31ob)  
16. How to debug your LLM apps \- ️ LangChain, accessed August 24, 2025, [https://python.langchain.com/docs/how\_to/debugging/](https://python.langchain.com/docs/how_to/debugging/)  
17. LangSmith \- LangChain, accessed August 24, 2025, [https://www.langchain.com/langsmith](https://www.langchain.com/langsmith)  
18. Understanding State in LangGraph: A Beginners Guide | by Rick Garcia | Medium, accessed August 24, 2025, [https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997](https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997)  
19. From Basics to Advanced: Exploring LangGraph | by Mariya Mansurova \- Medium, accessed August 24, 2025, [https://medium.com/data-science/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787](https://medium.com/data-science/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787)  
20. Build a Code Generator and Executor Agent Using LangGraph, LangChain Sandbox and Groq Kimi K2 Instruct: Context Engineering \- Medium, accessed August 24, 2025, [https://medium.com/the-ai-forum/build-a-code-generator-and-executor-agent-using-langgraph-langchain-sandbox-and-groq-kimi-k2-291a88e66e6f](https://medium.com/the-ai-forum/build-a-code-generator-and-executor-agent-using-langgraph-langchain-sandbox-and-groq-kimi-k2-291a88e66e6f)  
21. Context Engineering \- LangChain Blog, accessed August 24, 2025, [https://blog.langchain.com/context-engineering-for-agents/](https://blog.langchain.com/context-engineering-for-agents/)  
22. How to create tools \- Python LangChain, accessed August 24, 2025, [https://python.langchain.com/docs/how\_to/custom\_tools/](https://python.langchain.com/docs/how_to/custom_tools/)  
23. Building a Multi-Tool Agent with LangGraph and Google Vertex AI | by İpek Şahbazoğlu, accessed August 24, 2025, [https://medium.com/@ipeksahbazoglu/building-a-multi-tool-agent-with-langgraph-and-google-vertex-ai-e37aa6d41265](https://medium.com/@ipeksahbazoglu/building-a-multi-tool-agent-with-langgraph-and-google-vertex-ai-e37aa6d41265)  
24. Building Multi-Agent Systems with LangGraph: A Step-by-Step ..., accessed August 24, 2025, [https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72](https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72)  
25. LangGraph Tutorial: Building LLM Agents with LangChain's Agent Framework \- Zep, accessed August 24, 2025, [https://www.getzep.com/ai-agents/langgraph-tutorial/](https://www.getzep.com/ai-agents/langgraph-tutorial/)  
26. How do AI Agent workflows (langgraph) know what tools to use? \- Stack Overflow, accessed August 24, 2025, [https://stackoverflow.com/questions/79687721/how-do-ai-agent-workflows-langgraph-know-what-tools-to-use](https://stackoverflow.com/questions/79687721/how-do-ai-agent-workflows-langgraph-know-what-tools-to-use)  
27. Tool calling \- Python LangChain, accessed August 24, 2025, [https://python.langchain.com/docs/concepts/tool\_calling/](https://python.langchain.com/docs/concepts/tool_calling/)  
28. Langgraph's weird behavior in Python\!? Cannot rename nodes : r/LangChain \- Reddit, accessed August 24, 2025, [https://www.reddit.com/r/LangChain/comments/1h99h7z/langgraphs\_weird\_behavior\_in\_python\_cannot\_rename/](https://www.reddit.com/r/LangChain/comments/1h99h7z/langgraphs_weird_behavior_in_python_cannot_rename/)  
29. Call tools \- GitHub Pages, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/how-tos/tool-calling/](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)  
30. A Comprehensive Guide to LangGraph: Managing Agent State with Tools \- Medium, accessed August 24, 2025, [https://medium.com/@o39joey/a-comprehensive-guide-to-langgraph-managing-agent-state-with-tools-ae932206c7d7](https://medium.com/@o39joey/a-comprehensive-guide-to-langgraph-managing-agent-state-with-tools-ae932206c7d7)  
31. \`ToolNode\` doesn't support state update · langchain-ai langgraph · Discussion \#1322, accessed August 24, 2025, [https://github.com/langchain-ai/langgraph/discussions/1322](https://github.com/langchain-ai/langgraph/discussions/1322)  
32. How to handle tool errors \- LangChain.js, accessed August 24, 2025, [https://js.langchain.com/docs/how\_to/tools\_error/](https://js.langchain.com/docs/how_to/tools_error/)  
33. How to handle tool errors | 🦜️ LangChain, accessed August 24, 2025, [https://python.langchain.com/docs/how\_to/tools\_error/](https://python.langchain.com/docs/how_to/tools_error/)  
34. How to handle tool calling errors, accessed August 24, 2025, [https://langchain-ai.github.io/langgraphjs/how-tos/tool-calling-errors/](https://langchain-ai.github.io/langgraphjs/how-tos/tool-calling-errors/)  
35. Circuit Breaker Pattern \- Azure Architecture Center | Microsoft Learn, accessed August 24, 2025, [https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)  
36. langchain-ai/langgraph: Build resilient language agents as graphs. \- GitHub, accessed August 24, 2025, [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)  
37. Strategies for debugging agents with LangGraph Studio \- YouTube, accessed August 24, 2025, [https://www.youtube.com/watch?v=5vEC0Y4sV8g](https://www.youtube.com/watch?v=5vEC0Y4sV8g)  
38. Building AI Workflows with LangGraph: Practical Use Cases and Examples \- Scalable Path, accessed August 24, 2025, [https://www.scalablepath.com/machine-learning/langgraph](https://www.scalablepath.com/machine-learning/langgraph)  
39. How to unit-test decorated functions? \- python \- Stack Overflow, accessed August 24, 2025, [https://stackoverflow.com/questions/30327518/how-to-unit-test-decorated-functions](https://stackoverflow.com/questions/30327518/how-to-unit-test-decorated-functions)  
40. Confused about unit-testing : r/LangChain \- Reddit, accessed August 24, 2025, [https://www.reddit.com/r/LangChain/comments/1fyolo3/confused\_about\_unittesting/](https://www.reddit.com/r/LangChain/comments/1fyolo3/confused_about_unittesting/)  
41. How to write tests for Langgraph Workflows \#633 \- GitHub, accessed August 24, 2025, [https://github.com/langchain-ai/langgraph/discussions/633](https://github.com/langchain-ai/langgraph/discussions/633)  
42. How to run evals with pytest (beta) \- ️🛠️ LangSmith \- LangChain, accessed August 24, 2025, [https://docs.smith.langchain.com/evaluation/how\_to\_guides/pytest](https://docs.smith.langchain.com/evaluation/how_to_guides/pytest)  
43. langchain-ai/langchain-sandbox: Safely run untrusted Python code using Pyodide and Deno, accessed August 24, 2025, [https://github.com/langchain-ai/langchain-sandbox](https://github.com/langchain-ai/langchain-sandbox)  
44. Add human intervention \- GitHub Pages, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/how-tos/human\_in\_the\_loop/add-human-in-the-loop/](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/add-human-in-the-loop/)  
45. Add human-in-the-loop controls \- Docs by LangChain, accessed August 24, 2025, [https://docs.langchain.com/langgraph-platform/langgraph-basics/4-human-in-the-loop](https://docs.langchain.com/langgraph-platform/langgraph-basics/4-human-in-the-loop)  
46. LangGraph's human-in-the-loop \- Overview, accessed August 24, 2025, [https://langchain-ai.github.io/langgraph/concepts/human\_in\_the\_loop/](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)  
47. Making it easier to build human-in-the-loop agents with interrupt \- LangChain Blog, accessed August 24, 2025, [https://blog.langchain.com/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt/](https://blog.langchain.com/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt/)  
48. Persistence & Human-in-the-Loop Workflow \- LangGraph \- YouTube, accessed August 24, 2025, [https://www.youtube.com/watch?v=9BPCV5TYPmg](https://www.youtube.com/watch?v=9BPCV5TYPmg)  
49. Powering Long-Term Memory for Agents With LangGraph and MongoDB, accessed August 24, 2025, [https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)  
50. LangGraph \- LangChain, accessed August 24, 2025, [https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)  
51. Building Agentic RAG Systems with LangGraph \- Quilltez, accessed August 24, 2025, [https://quilltez.com/blog/building-agentic-rag-systems-langgraph](https://quilltez.com/blog/building-agentic-rag-systems-langgraph)