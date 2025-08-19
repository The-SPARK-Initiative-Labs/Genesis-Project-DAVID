

# **Architecting Autonomous AI: A Development Guide for a Self-Improving Python Framework with Ollama**

## **Part I: Foundations \- Interfacing with Local LLMs via Ollama**

### **Chapter 1: Mastering the Ollama Ecosystem: From CLI to API**

#### **1.1. Architectural Overview: Ollama as a Local Inference Server**

Ollama has emerged as a foundational tool for developers seeking to run large language models (LLMs) on local hardware. Its core architectural principle is the simplification of a complex process: serving open-source LLMs like Llama 3.1, Mistral, and Gemma 3\.1 Ollama functions as a persistent background service that exposes a standardized REST API, effectively abstracting away the intricate details of model management, hardware acceleration (such as GPU utilization via CUDA or Metal), and runtime configuration.4 This approach has been likened to Docker for AI models; it bundles model weights, configurations, and data into a single, portable package managed by a

Modelfile, allowing developers to pull and run models with simple commands, such as ollama pull llama3.1 and ollama serve.4

The initial setup is streamlined across major operating systems, including macOS, Linux, and Windows (via the Windows Subsystem for Linux, or WSL).5 Once installed, Ollama manages the model files, typically storing them in

\~/.ollama/models on macOS or /usr/share/ollama/.ollama/models on Linux.5 This design provides a stable and consistent service layer. For a framework developer, this is a strategic advantage. It means the framework's lowest level of interaction is not with a disparate collection of model-specific loading scripts and hardware configurations, but with a single, well-defined API endpoint. This commoditization of local LLM serving allows the framework to focus on higher-level logic, such as agentic control, state management, and self-improvement, rather than the underlying complexities of model execution.

#### **1.2. Programmatic Control: A Tale of Two Approaches**

Interacting with the Ollama server programmatically can be achieved through two primary methods: using the official Python library or making direct REST API calls. Each approach presents a trade-off between convenience and control, a critical consideration in framework design.

**The ollama-python Library**

The official ollama-python library is the most straightforward method for integrating Ollama into a Python project.8 It requires Python 3.8 or higher and can be installed via

pip.9 The library provides a high-level, intuitive interface with both synchronous (

Client) and asynchronous (AsyncClient) clients to handle different application needs.9 Core functionalities include:

* **Chat and Generation:** Simple functions like ollama.chat() and ollama.generate() handle the most common use cases.9  
* **Streaming Responses:** By setting the stream=True parameter, the library returns a Python generator, allowing for real-time token-by-token processing of the model's output.9  
* **Model Management:** The library exposes APIs to programmatically list, show details of, copy, delete, and create models, mirroring the CLI's capabilities.8

**Direct REST API Interaction**

For a production-grade framework, interfacing directly with Ollama's REST API offers unparalleled control. While the official library is excellent for rapid development, building the core interaction logic using a library like requests decouples the framework from the ollama-python library's release cycle and its specific abstractions.13 This direct approach allows for granular control over HTTP headers, connection pooling, custom timeouts, and sophisticated error handling that might not be exposed by the client library.

The primary endpoints for a framework are /api/generate and /api/chat.6 A key challenge in this approach is correctly handling streaming responses. A standard

requests.post() call will fail with a JSONDecodeError because the server sends back a stream of multiple JSON objects, one per line.13 The correct implementation involves setting

stream=True in the request and then iterating over the response using response.iter\_lines(). Each line must then be decoded from bytes to a UTF-8 string and parsed as an individual JSON object.13 While more complex, this level of control is essential for building a robust framework that can gracefully handle network interruptions or malformed data chunks within a stream.

#### **1.3. Model Customization and Parameterization with Modelfile**

The Modelfile is Ollama's primary mechanism for creating customized model variants.2 It is a plain text file that specifies a base model using the

FROM instruction and then applies a series of modifications, such as setting a system prompt, defining model parameters, or even importing a model from a raw GGUF file.2 This allows developers to create specialized versions of a model tailored to specific tasks—for instance, a highly creative model with a high

temperature versus a deterministic, factual model with a temperature of 0\.12

The parameters that can be configured in a Modelfile or passed directly via the API's options object provide the essential levers for controlling an LLM's behavior. A deep understanding of these parameters is crucial for any agentic framework.

**Table 1: Ollama Model Parameter Deep Dive**

| Parameter | Data Type | Default | Description | Impact on Output | Example Usage (Modelfile) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| temperature | float | 0.8 | Controls the randomness of the output. | Higher values (e.g., 1.5) lead to more creative and diverse responses. Lower values (e.g., 0.2) produce more deterministic and focused text. | PARAMETER temperature 0.7 |
| num\_ctx | int | 2048 | Sets the size of the context window in tokens. | A larger context window allows the model to "remember" more of the preceding conversation or document, but requires more memory (RAM/VRAM). | PARAMETER num\_ctx 4096 |
| repeat\_penalty | float | 1.1 | Penalizes the model for repeating tokens. | Higher values (e.g., 1.5) strongly discourage repetition, while lower values (e.g., 0.9) are more lenient. | PARAMETER repeat\_penalty 1.2 |
| stop | string | N/A | A sequence of characters that will cause the model to stop generating text. | Useful for forcing the model to end its response at a specific point, such as after a certain phrase or a special token. Can be specified multiple times. | PARAMETER stop "User:" |
| mirostat | int | 0 | Enables Mirostat sampling to control perplexity. | 0=disabled, 1=Mirostat, 2=Mirostat 2.0. Aims to produce text of a consistent quality/surprisingness, preventing runaway creativity or dullness. | PARAMETER mirostat 1 |
| mirostat\_tau | float | 5.0 | Controls the balance between coherence and diversity in Mirostat. | Lower values result in more focused and coherent text. Higher values allow for more diversity. | PARAMETER mirostat\_tau 4.0 |
| mirostat\_eta | float | 0.1 | The learning rate for Mirostat. | Influences how quickly the algorithm adjusts to the generated text's feedback. | PARAMETER mirostat\_eta 0.2 |
| seed | int | 0 | Sets the random seed for generation. | Using a specific non-zero seed ensures that the model produces the same output for the same prompt, enabling reproducible results. | PARAMETER seed 42 |
| num\_gpu | int | 1 (macOS) | The number of layers to offload to the GPU. | Increasing this value can significantly speed up inference on systems with capable GPUs, but requires more VRAM. Set to 0 to disable GPU acceleration. | PARAMETER num\_gpu 50 |

Source Data: Extracted and synthesized from.8

### **Chapter 2: The State-Management Core \- Building a Stateful Conversation Server**

#### **2.1. The Stateless API vs. Stateful Agent Dichotomy**

A fundamental architectural challenge in building any conversational AI is the inherent conflict between stateless APIs and stateful agents. REST APIs, by their design principles, are stateless.16 Each request sent to the server is treated as an independent, isolated transaction, with the server retaining no memory of past interactions.17 The Ollama API adheres to this principle; it does not store any "conversational state" between calls.18

Conversely, a useful agent is fundamentally stateful. To maintain a coherent dialogue, ask follow-up questions, or build upon previous actions, the agent must remember the history of its interaction with the user.19 The mechanism Ollama provides to bridge this gap is the

messages array within the /api/chat endpoint's request body.18 This design places the burden of state management squarely on the client. The client must construct the entire conversation history—a list of alternating

user and assistant messages—and send it with *every single request*.21 The Ollama server processes this complete context to generate the next response and then promptly forgets it again.

This dichotomy dictates the primary responsibility of our framework's server component: it must act as a stateful wrapper around the stateless Ollama API. It is not an optional feature but the core value proposition of the server. It will receive a single, new message from an end-user, but it will be responsible for retrieving the historical context of that user's session, appending the new message, and sending the complete, ordered history to the Ollama API.

#### **2.2. Architectural Blueprint: A FastAPI Server for State Management**

FastAPI is an excellent choice for building this stateful server due to its high performance, native support for asynchronous operations (critical for handling I/O-bound LLM API calls without blocking), and a powerful dependency injection system that simplifies managing resources like database connections.22

The architectural blueprint for this server involves several key components:

* **Session Management:** To handle multiple users concurrently, each conversation must be isolated. FastAPI, built on Starlette, can leverage middleware like SessionMiddleware to manage unique user sessions, typically via signed cookies.23 This ensures that one user's conversation history does not leak into another's. A session manager class can be designed to handle the creation, retrieval, and termination of these sessions.24  
* **State Storage:** The conversation history for each session must be persisted. For development and simple use cases, an in-memory Python dictionary mapping session IDs to message lists is sufficient. However, for a production system where state must survive server restarts, a more robust solution is required. A lightweight database like SQLite is a good starting point, while a more scalable application might use PostgreSQL or a dedicated key-value store like Redis.25 The server's logic will abstract this storage layer, allowing it to be swapped out as needed.  
* **API Endpoints:** The server will expose a minimal set of endpoints to the outside world. A primary /chat endpoint will accept a new message and a session identifier, orchestrate the call to Ollama, update the session's state, and return the response. Additional endpoints, such as /session/create and /session/clear, can be added to manage the conversation lifecycle explicitly.24

#### **2.3. The Model Context Protocol (MCP) Gateway**

The Model Context Protocol (MCP) is a specification that standardizes how external applications, such as code editors like Cursor or the Claude Desktop app, can interact with local AI models.11 Implementing an MCP server is a key requirement, and it should be viewed not as a separate piece of software, but as a specialized adapter or gateway into our framework's core logic.

An analysis of an existing Ollama MCP server implementation reveals a simple contract: the external application invokes a command-line script (e.g., ollama-mcp-cli), which then communicates with the model.26 That reference implementation has significant limitations, explicitly stating it does not support multi-turn conversation history or context management.26 Our framework will overcome these limitations.

The implementation involves two parts:

1. **A CLI Entry Point:** A simple script (e.g., ollama-mcp-cli) that starts the FastAPI server. This script is what the external application (like Cursor) is configured to execute.  
2. **An MCP-Compliant Endpoint:** A dedicated endpoint within our FastAPI server (e.g., /mcp) designed to receive and parse requests conforming to the MCP specification. This endpoint will act as a translator, converting the MCP request into a call to our framework's internal agent and state management systems. It will then format the agent's final response back into the structure expected by the MCP client.

By architecting the system this way, the MCP gateway becomes a powerful entry point that exposes the full stateful, tool-using, and self-improving capabilities of our framework through a standardized interface, far surpassing the functionality of basic MCP implementations.

## **Part II: The Agentic Core \- Reasoning, Acting, and Learning**

### **Chapter 3: Enabling Action \- The Function Calling Mechanism**

#### **3.1. Principles of LLM Tool Use**

Function calling, or tool use, is a transformative capability that allows LLMs to interact with external systems, moving them from passive text generators to active problem-solving agents.27 It is crucial to understand that the LLM does not execute code directly. Instead, when presented with a user prompt and a list of available tools, a tool-enabled model will, when appropriate, generate a structured JSON object specifying which function to call and the arguments to pass to it.27

The framework is responsible for parsing this JSON output and executing the corresponding function in its own runtime environment. This creates a robust and secure loop that leverages the LLM's reasoning capabilities while maintaining control over execution.30 The standard operational flow is as follows:

1. **Prompt & Tools:** The user's prompt is sent to the LLM along with a schema defining the available tools (e.g., get\_current\_weather, search\_database).  
2. **Tool Call Generation:** The LLM analyzes the prompt and determines that a tool is needed. It responds not with a natural language answer, but with a tool\_calls object in its output.5  
3. **Framework Execution:** The framework parses this object, identifies the function name (get\_current\_weather) and arguments ({"location": "Boston, MA"}), and executes the actual Python function.  
4. **Observation & Final Response:** The return value from the function (the "observation") is sent back to the LLM in a new message with the role tool. The LLM then uses this new information to generate a final, user-facing natural language response.29

#### **3.2. Implementing a Heterogeneous Tool-Use Subsystem**

A significant challenge with local LLMs is the wide variance in their native capabilities. A one-size-fits-all approach to tool calling is ineffective. A sophisticated framework must therefore implement a model-aware, multi-strategy subsystem to handle tool use reliably.

Strategy 1: Native Tool Calling  
For models that have been explicitly fine-tuned for tool use (e.g., llama3.1, qwen3, mistral v0.3) 1, the framework should use the native tool-calling feature of the Ollama API. This is achieved by passing a  
tools array in the request payload. Each element in the array is a JSON schema describing a function's name, description, and parameters.5 The framework then inspects the response for a

tool\_calls field and proceeds with execution as described above.

Strategy 2: JSON Mode Emulation  
For models that lack native tool support but are good instruction followers, the framework can emulate tool calling using Ollama's constrained output feature: format: "json".18 This is accomplished through careful prompt engineering. The system prompt must instruct the model to respond  
*only* with a JSON object conforming to a specific schema, for example: {"tool\_name": "function\_to\_call", "arguments": {"arg1": "value1"}}. This approach, while requiring a more verbose prompt, effectively forces the model to produce the structured output needed for the framework to dispatch the action.33

Strategy 3: The "No-Op" Tool for Robustness  
A common failure mode, particularly with smaller local models, is that when provided with tools, they will always attempt to call one, even when a simple text answer is appropriate. This can lead to infinite loops or nonsensical function calls.34 To mitigate this, the framework must implement a crucial defensive pattern: always including a "no-operation" or "default" tool in the list of available functions. This tool could be named  
answer\_user\_directly and have a single string argument like reason\_or\_answer. The framework's tool dispatcher must be designed to recognize this specific tool name. When it is "called," the dispatcher does not execute any code; it simply takes the provided argument and returns it as the final response to the user. This gives the model a reliable "escape hatch" to exit the tool-calling loop and just answer the question, dramatically improving the agent's robustness.34

To guide developers, the following table summarizes the recommended tool-calling strategies for popular Ollama models.

**Table 2: Ollama Model Tool-Calling Capabilities**

| Model Name | Native Tool Support | Recommended Strategy | Source Reference(s) |
| :---- | :---- | :---- | :---- |
| llama3.1 | Yes | Native API (tools parameter) | 5 |
| llama3.2 | Yes | Native API (tools parameter) | 1 |
| qwen3 | Yes | Native API (tools parameter) | 1 |
| mistral:0.3 | Yes | Native API (tools parameter) | 1 |
| gemma3 | Yes | Native API (tools parameter) | 1 |
| mistral (older) | No | JSON Mode Emulation | 34 |
| llama2 | No | JSON Mode Emulation | 4 |
| tinyllama | No | JSON Mode Emulation (with caution) | 34 |

Source Data: Synthesized from.1



## **Part III: Advanced Capabilities \- The Path to Self-Improvement**

### **Chapter 5: Building Agent Memory \- The Foundation of Learning**

#### **5.1. A Multi-Layered Memory Architecture**

To move beyond solving single tasks and enable genuine learning and adaptation over time, an agent requires a memory system more sophisticated than a simple conversation history.41 Drawing inspiration from models of human cognition, our framework will implement a multi-layered memory architecture that distinguishes between transient working memory and persistent long-term storage.43

* **Short-Term Memory (STM) / Working Memory:** This is the agent's memory for the task at hand. In our architecture, the STM is represented by the conversation trajectory for the current session.44 It is managed in-memory by the FastAPI server and is ephemeral, existing only for the duration of a single task. Its size is constrained by the LLM's context window.  
* **Long-Term Memory (LTM):** This is a persistent, external storage system designed to retain information across multiple sessions and tasks.41 The industry standard for implementing LTM in LLM agents is a vector database. Information is stored as vector embeddings, allowing for efficient retrieval based on semantic similarity rather than exact keyword matches. Our LTM will be structured to hold two distinct types of memories, mirroring human declarative memory 42:  
  * **Episodic Memory:** This stores records of past experiences. Each entry is a summary of a completed task trajectory, capturing the goal, the key steps taken, and the final outcome (success or failure). This is the agent's memory of "what happened".41  
  * **Semantic Memory:** This stores distilled knowledge, facts, and concepts extracted from successful tasks. For example, after successfully finding a user's address, the agent could store the fact "User\_123's address is 123 Main St" in its semantic memory. This is the agent's memory of "what is true".43

#### **5.2. The Experience Loop: From Action to Memory**

For an agent to learn from experience, there must be a mechanism to transfer knowledge from its transient short-term memory to its persistent long-term memory. This process forms the "write" phase of the learning loop.48

We will implement this by equipping the agent with a special internal tool: commit\_experience\_to\_ltm. This tool is not for interacting with the outside world but for managing the agent's own internal state. The agent's logic will be designed such that after a task is completed, its final action is to call this function.

The commit\_experience\_to\_ltm tool will:

1. Receive the entire conversation trajectory (the STM) as input.  
2. Use the LLM one final time to summarize this trajectory, extracting the key episodic and semantic information. For example, it might generate a summary like: "Task: Book a flight for User\_123. Outcome: Success. Key steps: Used search\_flights tool, found flight BA2490, confirmed with user, used book\_flight tool. Learned fact: User\_123 prefers window seats."  
3. Generate vector embeddings for this summary.  
4. Store these embeddings and the raw summary text in the appropriate LTM stores (episodic and semantic).

This process transforms a fleeting experience into a durable, retrievable memory, forming the basis for future improvement.48

#### **5.3. Retrieval-Augmented Reasoning: Learning in Action**

The "read" phase of the learning cycle is where the agent actively uses its memories to perform better on new tasks. This is achieved through a process of retrieval-augmented reasoning.47

We will modify the agent's core prompt. The new instruction will mandate that the agent's *very first action* for any new task is to query its long-term memory. This is facilitated by another internal tool: retrieve\_from\_ltm(query: str).

The process works as follows:

1. The agent begins a new task (e.g., "Plan a vacation to Paris for me").  
2. Its first action is to call retrieve\_from\_ltm(query="User\_123 Paris vacation planning").  
3. The framework executes this tool by converting the query into a vector embedding and performing a similarity search against the LTM vector database.  
4. The result returned to the agent is a list of the most relevant memories, such as: "Episodic Memory: Previously planned a trip to Rome for User\_123, user was interested in museums and budget-friendly dining. Semantic Memory: User\_123's budget is approximately $200/day."  
5. This retrieved information is now part of the agent's short-term working memory (its context). All subsequent actions for the current task are now informed by this relevant past experience, guiding the agent toward a more personalized and effective plan.

This architectural loop of **Action → Store Experience → Retrieve Relevant Experience → Better Action** is the practical, implementable mechanism for self-improvement. The agent's performance enhances over time not because its underlying model weights are changing, but because its decisions are informed by a growing and increasingly relevant pool of its own past successes and failures.

### **Chapter 6: The Self-Correction Mechanism: Engineering Reliability**

#### **6.1. The Fallacy of Intrinsic Self-Correction**

A common misconception is that LLMs can reliably self-correct their own mistakes simply by being asked to "review" or "double-check" their work. However, a growing body of research indicates that this form of *intrinsic self-correction*, which relies solely on the model's internal capabilities without external feedback, is largely ineffective.51 LLMs often exhibit a strong "self-bias," meaning they are more likely to reinforce their initial (and potentially incorrect) reasoning than to identify the flaw.53 In some cases, asking a model to self-correct without an external signal can even degrade the quality of the response.51 The primary bottleneck is error detection; LLMs struggle to recognize their own mistakes, especially in complex reasoning tasks.53

#### **6.2. A Framework for Tool-Aided Self-Correction**

Given the limitations of intrinsic correction, a robust framework must engineer self-correction as a process grounded in external, objective feedback. The academic consensus is that self-correction is effective precisely when such reliable external feedback is available.52 Our framework will implement this using a

**Propose → Test → Reflect → Refine** cycle.54

This cycle is not a new module, but rather a specific pattern of tool use where the tools are designed for validation:

1. **Propose:** The agent generates an initial output as a standard Action in its ReAct loop. This output could be a snippet of Python code, a SQL query, a JSON object, or a paragraph of text.  
2. **Test:** The agent then uses a specialized *validator tool* to check the correctness of its proposal. This is the crucial step that provides external feedback. The framework should be extensible to support various validator tools, such as:  
   * A python\_interpreter tool that executes generated code and returns the output or any runtime errors.  
   * A unit\_test\_runner tool that runs the generated code against a predefined set of tests.  
   * A json\_schema\_validator that checks if a generated JSON object conforms to a required schema.  
   * An sql\_linter that checks a generated query for valid syntax before execution.  
3. **Reflect & Refine:** The output from the validator tool becomes the Observation. The agent is then prompted to reflect on this feedback.  
   * If the test passed, the agent can conclude that part of the task is complete and move on.  
   * If the test failed (e.g., a SyntaxError from the code interpreter), the error message becomes the critical piece of information in the Observation. The agent's next Thought will be to analyze this specific error and formulate a plan to fix it, leading to a new, refined Action (the corrected code).

This loop repeats until the validator tool confirms success. This makes self-correction an emergent property of the agent's ability to use validation tools. The agent's ability to self-correct is therefore directly proportional to the quality and availability of its validator tools, turning an abstract concept into a concrete, engineered capability. Furthermore, the agent's memory system can play a vital role, allowing it to learn which correction strategies are most effective for specific types of errors over time.

### **Conclusion: Synthesizing the Framework and Future Directions**

The architecture detailed in this guide presents a comprehensive blueprint for a Python framework capable of creating autonomous, self-improving AI agents using local LLMs via Ollama. The design is built upon a series of interconnected patterns that address the core challenges of state management, tool use, and learning.

A visualization of the complete system would show the **Model Context Protocol (MCP) Gateway** as the entry point, funneling requests to the **FastAPI State Server**. This server acts as the central nervous system, managing distinct user sessions. For each session, it maintains the **Short-Term Memory**—the active ReAct trajectory. The agent's **Control Loop** orchestrates the flow, interacting with a **Heterogeneous Tool Dispatcher** that intelligently selects between native and emulated tool-calling strategies. Crucially, this loop interfaces with a persistent **Long-Term Memory** store, implemented as a vector database. The agent's commit\_experience and retrieve\_experience tools create a learning cycle, while specialized validator tools enable a robust Propose-Test-Refine self-correction mechanism.

The key design principles that emerge are:

* **Stateful Wrapping of a Stateless API:** The framework's primary role is to create a stateful conversational layer on top of the inherently stateless Ollama REST API.  
* **Heterogeneous Tool Use:** A robust agent must accommodate the diverse capabilities of different LLMs, seamlessly switching between native tool-calling, JSON-mode emulation, and defensive "no-op" patterns.  
* **Autonomous Reasoning:** The action-observation loop provides a simple yet powerful structure for autonomous reasoning and problem decomposition.  
* **Self-Improvement as an Emergent Property:** Learning and self-correction are not magical abilities of the LLM but are engineered outcomes of the architectural loops connecting action, memory, and tool-based validation.

Looking forward, this foundational framework can be extended to explore more advanced frontiers in agentic AI. The architecture naturally supports the development of **multi-agent systems**, where specialized agents, each with their own memory and tools, collaborate to solve more complex problems.48 Further research into

**advanced memory consolidation** techniques could allow the agent to more intelligently summarize and structure its long-term memories, preventing knowledge degradation over time.47 Ultimately, this framework serves as a practical starting point for building and experimenting with the next generation of intelligent systems that learn, adapt, and improve through their interactions with the world.

#### **Works cited**

1. library \- Ollama, accessed August 4, 2025, [https://ollama.com/library](https://ollama.com/library)  
2. ollama/ollama: Get up and running with Llama 3.3, DeepSeek-R1, Phi-4, Gemma 3, Mistral Small 3.1 and other large language models. \- GitHub, accessed August 4, 2025, [https://github.com/ollama/ollama](https://github.com/ollama/ollama)  
3. Ollama, accessed August 4, 2025, [https://ollama.com/](https://ollama.com/)  
4. Using Ollama with Python: Step-by-Step Guide \- Cohorte Projects, accessed August 4, 2025, [https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide](https://www.cohorte.co/blog/using-ollama-with-python-step-by-step-guide)  
5. ChatOllama | 🦜️ LangChain, accessed August 4, 2025, [https://python.langchain.com/docs/integrations/chat/ollama/](https://python.langchain.com/docs/integrations/chat/ollama/)  
6. Ollama REST API | Documentation | Postman API Network, accessed August 4, 2025, [https://www.postman.com/postman-student-programs/ollama-api/documentation/suc47x8/ollama-rest-api](https://www.postman.com/postman-student-programs/ollama-api/documentation/suc47x8/ollama-rest-api)  
7. Ollama API Usage Examples \- GPU Mart, accessed August 4, 2025, [https://www.gpu-mart.com/blog/ollama-api-usage-examples](https://www.gpu-mart.com/blog/ollama-api-usage-examples)  
8. ollama-python \- PyPI, accessed August 4, 2025, [https://pypi.org/project/ollama-python/](https://pypi.org/project/ollama-python/)  
9. Ollama Python Library \- PyPI, accessed August 4, 2025, [https://pypi.org/project/ollama/0.1.3/](https://pypi.org/project/ollama/0.1.3/)  
10. Ollama Python library \- GitHub, accessed August 4, 2025, [https://github.com/ollama/ollama-python](https://github.com/ollama/ollama-python)  
11. Using Ollama with Python: A Simple Guide | by Jonathan Gastón Löwenstern \- Medium, accessed August 4, 2025, [https://medium.com/@jonigl/using-ollama-with-python-a-simple-guide-0752369e1e55](https://medium.com/@jonigl/using-ollama-with-python-a-simple-guide-0752369e1e55)  
12. Ollama has a Python library\! \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=JwYwPiOh72w](https://www.youtube.com/watch?v=JwYwPiOh72w)  
13. Streaming LLM Requests with Python \- Nick Herrig, accessed August 4, 2025, [https://nickherrig.com/posts/streaming-requests/](https://nickherrig.com/posts/streaming-requests/)  
14. Local LLMs using Ollama Server API with Python | Mochan.org, accessed August 4, 2025, [http://mochan.org/posts/python-ollama-server/](http://mochan.org/posts/python-ollama-server/)  
15. Ollama REST API Endpoints \- KodeKloud Notes, accessed August 4, 2025, [https://notes.kodekloud.com/docs/Running-Local-LLMs-With-Ollama/Building-AI-Applications/Ollama-REST-API-Endpoints](https://notes.kodekloud.com/docs/Running-Local-LLMs-With-Ollama/Building-AI-Applications/Ollama-REST-API-Endpoints)  
16. Stateful vs stateless applications \- Red Hat, accessed August 4, 2025, [https://www.redhat.com/en/topics/cloud-native-apps/stateful-vs-stateless](https://www.redhat.com/en/topics/cloud-native-apps/stateful-vs-stateless)  
17. Stateful vs Stateless, How about REST API? | by Tioka Chiu \- Medium, accessed August 4, 2025, [https://medium.com/@tiokachiu/stateful-vs-stateless-how-about-rest-api-7ca52344c090](https://medium.com/@tiokachiu/stateful-vs-stateless-how-about-rest-api-7ca52344c090)  
18. API Reference \- Ollama English Documentation, accessed August 4, 2025, [https://ollama.readthedocs.io/en/api/](https://ollama.readthedocs.io/en/api/)  
19. conversational state of session beans \- Stack Overflow, accessed August 4, 2025, [https://stackoverflow.com/questions/5153012/conversational-state-of-session-beans](https://stackoverflow.com/questions/5153012/conversational-state-of-session-beans)  
20. Stateful vs. Stateless Web App Design \- DreamFactory Blog, accessed August 4, 2025, [https://blog.dreamfactory.com/stateful-vs-stateless-web-app-design](https://blog.dreamfactory.com/stateful-vs-stateless-web-app-design)  
21. Conversation state \- OpenAI API, accessed August 4, 2025, [https://platform.openai.com/docs/guides/conversation-state](https://platform.openai.com/docs/guides/conversation-state)  
22. State management and separation of routes : r/FastAPI \- Reddit, accessed August 4, 2025, [https://www.reddit.com/r/FastAPI/comments/1iq7it3/state\_management\_and\_separation\_of\_routes/](https://www.reddit.com/r/FastAPI/comments/1iq7it3/state_management_and_separation_of_routes/)  
23. Building a RESTful API for Your Chatbot Service Using FastAPI | CodeSignal Learn, accessed August 4, 2025, [https://codesignal.com/learn/courses/building-a-chatbot-service-with-fastapi/lessons/building-a-restful-api-for-your-chatbot-service-using-fastapi](https://codesignal.com/learn/courses/building-a-chatbot-service-with-fastapi/lessons/building-a-restful-api-for-your-chatbot-service-using-fastapi)  
24. Building a Conversational Agent Using FastAPI and Watson Assistant: Part 1(Agent Backend) | by Aniket Mohan | Medium, accessed August 4, 2025, [https://medium.com/@aniket.mohan9/building-a-conversational-agent-using-fastapi-and-watson-assistant-part-1-agent-backend-d04b01dcf72a](https://medium.com/@aniket.mohan9/building-a-conversational-agent-using-fastapi-and-watson-assistant-part-1-agent-backend-d04b01dcf72a)  
25. Building a Conversational Agent with Memory Microservice with OpenAI and FastAPI | by Cesar Flores | TDS Archive | Medium, accessed August 4, 2025, [https://medium.com/data-science/building-a-conversational-agent-with-memory-microservice-with-openai-and-fastapi-5d0102bc8df9](https://medium.com/data-science/building-a-conversational-agent-with-memory-microservice-with-openai-and-fastapi-5d0102bc8df9)  
26. Ollama MCP server for AI agents \- Playbooks, accessed August 4, 2025, [https://playbooks.com/mcp/shadowsinger-ollama-guidance](https://playbooks.com/mcp/shadowsinger-ollama-guidance)  
27. Function calling using LLMs \- Martin Fowler, accessed August 4, 2025, [https://martinfowler.com/articles/function-call-LLM.html](https://martinfowler.com/articles/function-call-LLM.html)  
28. Function Calling with LLMs \- Prompt Engineering Guide, accessed August 4, 2025, [https://www.promptingguide.ai/applications/function\_calling](https://www.promptingguide.ai/applications/function_calling)  
29. Function calling with the Gemini API | Google AI for Developers, accessed August 4, 2025, [https://ai.google.dev/gemini-api/docs/function-calling](https://ai.google.dev/gemini-api/docs/function-calling)  
30. Understanding Function Calling in LLMs \- Zilliz blog, accessed August 4, 2025, [https://zilliz.com/blog/harnessing-function-calling-to-build-smarter-llm-apps](https://zilliz.com/blog/harnessing-function-calling-to-build-smarter-llm-apps)  
31. Function Calling with LangChain, Ollama, and Streamlit: A Game-Changer in AI-Powered Apps | by Sneharsh Belsare | Medium, accessed August 4, 2025, [https://medium.com/@snehbelsare/function-calling-with-langchain-ollama-and-streamlit-a-game-changer-in-ai-powered-apps-b3c571ba65ca](https://medium.com/@snehbelsare/function-calling-with-langchain-ollama-and-streamlit-a-game-changer-in-ai-powered-apps-b3c571ba65ca)  
32. Exploring Ollama REST API Endpoints | by Kevinnjagi \- Medium, accessed August 4, 2025, [https://medium.com/@kevinnjagi83/exploring-ollama-rest-api-endpoints-7029fae5630d](https://medium.com/@kevinnjagi83/exploring-ollama-rest-api-endpoints-7029fae5630d)  
33. Ollama Functions | 🦜️ Langchain, accessed August 4, 2025, [https://js.langchain.com/docs/integrations/chat/ollama\_functions/](https://js.langchain.com/docs/integrations/chat/ollama_functions/)  
34. How to do proper function calling on Ollama models \- Reddit, accessed August 4, 2025, [https://www.reddit.com/r/ollama/comments/1ioyxkm/how\_to\_do\_proper\_function\_calling\_on\_ollama\_models/](https://www.reddit.com/r/ollama/comments/1ioyxkm/how_to_do_proper_function_calling_on_ollama_models/)  
35. ReAct \- Prompt Engineering Guide, accessed August 4, 2025, [https://www.promptingguide.ai/techniques/react](https://www.promptingguide.ai/techniques/react)  
36. ReAct: Synergizing Reasoning and Acting in Language Models \- arXiv, accessed August 4, 2025, [https://arxiv.org/pdf/2210.03629](https://arxiv.org/pdf/2210.03629)  
37. ReAct prompting in LLM : Redefining AI with Synergized Reasoning and Acting \- Medium, accessed August 4, 2025, [https://medium.com/@sahin.samia/react-prompting-in-llm-redefining-ai-with-synergized-reasoning-and-acting-c19640fa6b73](https://medium.com/@sahin.samia/react-prompting-in-llm-redefining-ai-with-synergized-reasoning-and-acting-c19640fa6b73)  
38. Build an Agent \- ️ LangChain, accessed August 4, 2025, [https://python.langchain.com/docs/tutorials/agents/](https://python.langchain.com/docs/tutorials/agents/)  
39. Agent architectures \- GitHub Pages, accessed August 4, 2025, [https://langchain-ai.github.io/langgraph/concepts/agentic\_concepts/](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)  
40. Prompt Engineering for AI Guide | Google Cloud, accessed August 4, 2025, [https://cloud.google.com/discover/what-is-prompt-engineering](https://cloud.google.com/discover/what-is-prompt-engineering)  
41. Why Memory Matters in LLM Agents: Short-Term vs. Long-Term Memory Architectures, accessed August 4, 2025, [https://skymod.tech/why-memory-matters-in-llm-agents-short-term-vs-long-term-memory-architectures/](https://skymod.tech/why-memory-matters-in-llm-agents-short-term-vs-long-term-memory-architectures/)  
42. The Need to Improve Long-Term Memory in LLM-Agents, accessed August 4, 2025, [https://ojs.aaai.org/index.php/AAAI-SS/article/download/27688/27461/31739](https://ojs.aaai.org/index.php/AAAI-SS/article/download/27688/27461/31739)  
43. From Human Memory to AI Memory: A Survey on Memory Mechanisms in the Era of LLMs \- arXiv, accessed August 4, 2025, [https://arxiv.org/html/2504.15965v1](https://arxiv.org/html/2504.15965v1)  
44. LLM Memory: Integration of Cognitive Architectures with AI \- Cognee, accessed August 4, 2025, [https://www.cognee.ai/blog/fundamentals/llm-memory-cognitive-architectures-with-ai](https://www.cognee.ai/blog/fundamentals/llm-memory-cognitive-architectures-with-ai)  
45. Short-Term vs. Long-Term LLM Memory: When to Use Prompts vs. Long-Term Recall? – RandomTrees – Blog, accessed August 4, 2025, [https://randomtrees.com/blog/short-term-vs-long-term-llm-memory-prompts-vs-recall/](https://randomtrees.com/blog/short-term-vs-long-term-llm-memory-prompts-vs-recall/)  
46. Memory Matters: The Need to Improve Long-Term Memory in LLM-Agents | Proceedings of the AAAI Symposium Series, accessed August 4, 2025, [https://ojs.aaai.org/index.php/AAAI-SS/article/view/27688](https://ojs.aaai.org/index.php/AAAI-SS/article/view/27688)  
47. Scalable Long-Term Memory for Production AI Agents \- Mem0, accessed August 4, 2025, [https://mem0.ai/research](https://mem0.ai/research)  
48. Cross-Task Experiential Learning on LLM-based Multi-Agent Collaboration \- arXiv, accessed August 4, 2025, [https://arxiv.org/html/2505.23187v1](https://arxiv.org/html/2505.23187v1)  
49. Build Self-Improving Agents: LangMem Procedural Memory Tutorial \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=WW-v5mO2P7w](https://www.youtube.com/watch?v=WW-v5mO2P7w)  
50. Long Term Memory : The Foundation of AI Self-Evolution \- arXiv, accessed August 4, 2025, [https://arxiv.org/html/2410.15665v1](https://arxiv.org/html/2410.15665v1)  
51. Large Language Models Cannot Self-Correct Reasoning Yet \- arXiv, accessed August 4, 2025, [https://arxiv.org/html/2310.01798v2](https://arxiv.org/html/2310.01798v2)  
52. When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs | Transactions of the Association for Computational Linguistics, accessed August 4, 2025, [https://direct.mit.edu/tacl/article/doi/10.1162/tacl\_a\_00713/125177/When-Can-LLMs-Actually-Correct-Their-Own-Mistakes](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177/When-Can-LLMs-Actually-Correct-Their-Own-Mistakes)  
53. Self-Correction in Large Language Models \- Communications of the ACM, accessed August 4, 2025, [https://cacm.acm.org/news/self-correction-in-large-language-models/](https://cacm.acm.org/news/self-correction-in-large-language-models/)  
54. Self-Correcting AI Agents: How to Build AI That Learns From Its Mistakes \- DEV Community, accessed August 4, 2025, [https://dev.to/louis-sanna/self-correcting-ai-agents-how-to-build-ai-that-learns-from-its-mistakes-39f1](https://dev.to/louis-sanna/self-correcting-ai-agents-how-to-build-ai-that-learns-from-its-mistakes-39f1)  
55. A Tour of Popular Open Source Frameworks for LLM-Powered Agents \- Dataiku Blog, accessed August 4, 2025, [https://blog.dataiku.com/open-source-frameworks-for-llm-powered-agents](https://blog.dataiku.com/open-source-frameworks-for-llm-powered-agents)