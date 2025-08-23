

# **A Comprehensive Research and Implementation Plan for a Multi-Tool AI Agent System**

## **Section 1: Core Agent Architecture with LangGraph and Local LLMs**

This section establishes the foundational architecture of the AI agent, focusing on how to structure a stateful graph that is robust, scalable, and compatible with the constraints of a local 14-billion-parameter Large Language Model (LLM). The architecture is designed around LangGraph for orchestration, a qwen3:14b model served via Ollama for reasoning, and a Chainlit UI for user interaction.

### **1.1 Foundational Graph Design: The StateGraph Schema**

The core of the agent's workflow is defined by a graph structure, with the application's state being the central element that is passed between computational units, or nodes.1 For a sophisticated, multi-tool agent, a well-defined state schema is paramount for managing the complex flow of information, enabling controlled tool access, maintaining historical context, and ensuring type safety.3

An enhanced state structure will be defined using Python's TypedDict to serve as the agent's comprehensive memory and operational context. This structure is more than a simple data container; it is an auditable record of the agent's execution path, which is invaluable for both automated self-correction and human-led debugging.4 By explicitly tracking tool calls, outputs, and errors, the state becomes a rich snapshot that can be inspected at any point, a key feature of LangGraph's durable execution model.5

The proposed AgentState schema is as follows:

Python

from typing import TypedDict, Annotated, Literal  
from langgraph.graph.message import add\_messages

class AgentState(TypedDict):  
    \# Conversational history, managed by LangGraph  
    messages: Annotated\[list, add\_messages\]  
      
    \# Core instructions defining the agent's personality and behavior  
    agent\_persona: str  
      
    \# A working memory for the LLM to chain thoughts and process intermediate results  
    scratchpad: str  
      
    \# Stores the LLM's requested tool invocations  
    tool\_calls: list  
      
    \# Stores the results from executed tools  
    tool\_outputs: list  
      
    \# A structured field for error handling and reflection  
    error\_state: dict  
      
    \# Contextually relevant information retrieved from long-term memory  
    long\_term\_memory: list

Each field serves a distinct purpose:

* messages: This field maintains the turn-by-turn conversation history between the user and the agent, leveraging LangGraph's add\_messages annotation to correctly append new messages.2  
* agent\_persona: Stores the core system prompt or personality instructions, ensuring this critical context can be consistently accessed and applied across different nodes in the graph.  
* scratchpad: Acts as a short-term, volatile memory for the agent's reasoning process, allowing it to "think out loud" or chain intermediate thoughts before committing to a tool call or final response.  
* tool\_calls and tool\_outputs: These fields explicitly separate the LLM's *intent* to use a tool from the *result* of that tool's execution, creating a clear, auditable trail of actions.  
* error\_state: A structured dictionary (e.g., {'error\_message': str, 'retry\_count': int, 'failed\_tool\_call': dict}) that is crucial for the self-reflection and error-handling loops detailed in Section 4\.  
* long\_term\_memory: This field will be populated with relevant facts and experiences retrieved from a persistent vector store, providing the agent with context that spans across conversations.

### **1.2 The Central Reasoning Loop and Local LLM Compatibility**

The primary reasoning engine of the agent is a central node that encapsulates the call to the local LLM. This node is responsible for interpreting the current state and deciding the next course of action.

A critical consideration for this architecture is the use of a 14-billion-parameter local model (qwen3:14b). Unlike larger, proprietary models that can infer intent from ambiguous or complex prompts, smaller models perform more reliably when given highly structured, explicit instructions. The LangGraph architecture must therefore be designed not merely as an orchestrator but as a *cognitive scaffold* that breaks down complex problems into a sequence of simpler tasks, each presentable to the LLM with a clear, focused prompt. This shifts some of the reasoning burden from the LLM to the graph's explicit structure, ensuring more predictable and reliable behavior.

The central agent node will perform the following steps:

1. **Prompt Assembly:** It constructs a detailed prompt from the AgentState. This prompt will use a structured format (e.g., XML tags) to clearly delineate different types of context: the agent's core persona, the recent conversation history from messages, relevant facts from long\_term\_memory, and any intermediate thoughts from the scratchpad.  
2. **Tool Binding:** The LLM instance is bound to the available tools using the .bind\_tools() method. This crucial step informs the model about the functions it can call and their expected JSON schemas, enabling it to generate valid tool-use requests.8  
3. **Model Invocation:** The assembled prompt is sent to the qwen3:14b model via Ollama. The model's response, which could be a natural language answer or a request to call one or more tools, is then used to update the AgentState.

The system prompt is essential for guiding the agent's behavior, especially in determining which tool is appropriate for a given query.7

### **1.3 Tool Routing and Dispatching Architecture**

Relying on a single agent node to select from a large, diverse set of tools can overwhelm a smaller LLM, leading to incorrect tool selection or hallucinated parameters.10 To mitigate this, a hierarchical, supervisor-style routing architecture will be implemented.1 This modular approach simplifies the decision-making process for the LLM at each step.

The proposed routing workflow is as follows:

1. **Initial Triage:** The central agent node makes a high-level decision, classifying the user's request into a broad category (e.g., "System Interaction," "Web Research," "Content Generation," or "Direct Answer").  
2. **Conditional Routing to Sub-graphs:** A conditional\_edge in LangGraph uses the LLM's classification to route the AgentState to a specialized sub-graph dedicated to that category. This narrows the set of available tools, providing a more focused context for the next LLM call.  
3. **Specific Tool Selection:** Within the sub-graph, another agent node can make a more fine-grained decision to select and invoke a specific tool.

This pattern will be implemented by creating separate ToolNode instances for each tool or for logical groupings of tools. This approach provides granular control over the graph's flow and is a recommended practice for managing complex tool interactions.11 A conditional routing function will inspect the tool\_calls attribute of the AI's message to determine the name of the next node to execute, effectively directing the flow of control through the graph.11

### **1.4 Preserving Agent Personality During Tool Execution**

A common failure mode in tool-using agents is "persona erosion," where the agent's established personality is lost when it returns raw, technical data from a tool (e.g., a JSON object or an unformatted text block). To ensure a cohesive and engaging user experience, the agent's persona must be consistently maintained.

The architecture will address this by introducing a dedicated "Persona Refinement" Node. This node is explicitly designed to run after a tool has been executed and its output has been added to the state.  
The workflow is as follows:

1. A ToolNode executes and populates the tool\_outputs field in the AgentState.  
2. The graph transitions to the persona\_refinement\_node.  
3. This node invokes the LLM with a highly specific prompt: "You are \[agent\_persona\]. A tool has just returned the following information: \[tool\_outputs\]. Based on this, formulate a helpful and engaging response to the user's original query, which was: \[user\_query\]."  
4. The output of this node is a final, persona-aligned message that is then streamed to the user. This ensures that even the most technical tool outputs are translated into the agent's consistent voice, a key aspect of designing for human-agent collaboration.5

## **Section 2: Native System Tool Integration and Security**

This section provides a detailed implementation plan for tools that interact directly with the host operating system. The guiding principle is an uncompromising focus on security, achieved through programmatic enforcement of safety patterns rather than reliance on the LLM's discretion.

### **2.1 Filesystem Operations Module**

The agent requires the ability to read, write, and manage files and directories to perform tasks like saving generated code or summarizing local documents.

* **Library Selection:** The pathlib module will be mandated for all filesystem path manipulations. Its object-oriented interface provides a more robust, intuitive, and less error-prone approach compared to the string-based functions in the legacy os.path module.12 For high-level, recursive file operations such as copying or removing entire directory trees, the  
  shutil module will be utilized.14  
* **Tool Implementation:** A suite of fundamental filesystem tools will be defined using the @tool decorator. Each tool will be designed as a discrete, single-purpose function:  
  * read\_file(path: str) \-\> str: Reads and returns the content of a specified file.  
  * write\_file(path: str, content: str, append: bool \= False) \-\> str: Writes or appends content to a file.  
  * list\_directory(path: str) \-\> list\[str\]: Returns a list of files and subdirectories within a given path.  
  * create\_directory(path: str, exist\_ok: bool \= True) \-\> str: Creates a new directory.  
  * delete\_file(path: str) \-\> str: Deletes a specified file.  
  * delete\_directory(path: str) \-\> str: Recursively deletes a directory and its contents.

Crucially, these base functions will not be exposed directly to the agent. They will first be wrapped with the security patterns detailed in Section 2.4 to create hardened, safe versions for agent use.

### **2.2 Secure Subprocess Execution via Sandboxing**

Allowing an LLM-driven agent to execute arbitrary system commands presents the most significant security risk in the entire system. A single compromised prompt could lead to catastrophic data loss, privilege escalation, or system compromise.15 Therefore, all command execution must be performed within a strictly controlled and isolated sandbox.

* **Architectural Mandate: Docker Sandboxing:** The industry-standard solution for achieving robust process isolation is containerization. All system commands and generated code will be executed within an ephemeral Docker container.17 This approach provides several key security benefits:  
  * **Filesystem Isolation:** The container has its own isolated filesystem, preventing the agent from accessing or modifying files on the host system outside of explicitly mounted volumes.  
  * **Process Isolation:** The executed command runs in a separate process space, sandboxed from the host's processes.  
  * **Resource Constraints:** Docker allows for the enforcement of strict CPU and memory limits, preventing denial-of-service attacks from runaway processes.  
  * **Consistent Environment:** The execution environment is defined by a Dockerfile, ensuring consistency and eliminating dependency conflicts.17  
* **Implementation Plan:**  
  1. **Define a Minimal Dockerfile:** A Docker image will be created from a lightweight base (e.g., python:3.11-slim) and will include only the essential libraries needed for code execution tasks.17  
  2. **Implement the run\_command\_in\_sandbox Tool:** This tool will be the sole interface for command execution. It will use the Docker SDK for Python (docker-py) to manage the container lifecycle.20 The tool will accept a command as a list of arguments (e.g.,  
     \['ls', '-l', '/workspace'\]). It will then programmatically:  
     * Start a new container from the pre-built image.  
     * Mount a dedicated, temporary "workspace" directory into the container.  
     * Execute the command using client.containers.run().  
     * Capture stdout, stderr, and the exit code.  
     * Ensure the container is automatically removed upon completion (auto\_remove=True).  
  3. The tool will return a structured dictionary containing the execution results, which can then be processed by the agent.

### **2.3 System Monitoring and Resource Awareness**

To enable the agent to be context-aware of its operating environment, it will be equipped with tools to monitor system resources. This allows it to answer questions about system status and could form the basis for future self-regulation capabilities.

* **Library Selection:** The psutil library is the ideal choice for this task, as it provides a comprehensive, cross-platform API for retrieving information about running processes and system utilization (CPU, memory, disk, network).21  
* **Tool Implementation:** The following read-only monitoring tools will be created:  
  * get\_cpu\_usage(): Returns CPU utilization as a percentage, logical and physical core counts, and current frequency, using psutil.cpu\_percent(interval=1), psutil.cpu\_count(), and psutil.cpu\_freq().21  
  * get\_memory\_usage(): Returns system memory statistics (total, available, used) in a human-readable format using psutil.virtual\_memory().21  
  * get\_disk\_usage(path: str \= '.'): Returns disk usage statistics for the specified path using psutil.disk\_usage().21  
  * list\_running\_processes(): Provides a summary of the top running processes, sorted by CPU or memory usage, by iterating with psutil.process\_iter().23

### **2.4 Security Patterns for System Access**

Security cannot be an afterthought; it must be architected into the very design of each system-level tool. The following patterns will be strictly enforced.

* **Path Traversal Prevention:** This vulnerability is a primary threat to any tool that accepts a file path as input.24 All file paths provided by the user or generated by the LLM must be rigorously validated to ensure they do not escape a predefined, restricted "workspace" directory.  
  * **Implementation:** A security wrapper function will be created. This function will take a file path, resolve it to its absolute, canonical path using os.path.realpath(), and then verify that this resolved path is a sub-path of the designated workspace directory using startswith(). If the check fails, a PermissionError will be raised, and the operation will be aborted immediately. This reliably prevents attacks using sequences like ../.25  
* **Command Injection Prevention:** The primary defense against this is the architectural decision to use Docker sandboxing (Section 2.2). By constructing commands as a list of arguments and passing them to the Docker SDK, we avoid invoking a shell (shell=True is never used). This prevents the operating system's shell from interpreting any part of the input as a command, effectively neutralizing the command injection vector.15  
* **Principle of Least Privilege (PoLP):** The agent and its tools must operate with the absolute minimum level of permissions required to function.27  
  * **Implementation:** The main Python application hosting the agent will be run under a dedicated, non-privileged user account. The Docker containers used for sandboxing will also be configured to run their internal processes as a non-root user. Any attempts to escalate privileges, such as invoking sudo, are strictly forbidden and represent a severe security anti-pattern.29  
* **Prompt Injection Mitigation:** As detailed by OWASP, prompt injection is a critical vulnerability for LLM applications.32  
  * **Implementation:** We will employ a two-layer defense. First, strong prompt design will be used to clearly separate immutable system instructions from variable user data, often using delimiters or structured formats.34 The system prompt will explicitly instruct the LLM to treat user input as data to be operated upon, not as instructions to be followed. Second, the programmatic security wrappers (e.g., for path validation) serve as a crucial backstop, ensuring that even if a prompt injection attack successfully manipulates the LLM, the resulting malicious action (e.g., writing to a system file) will be blocked at the code level.

---

**Table 2.1: Comparison of Python Filesystem Libraries**

| Library | Key Functions/Classes | Primary Use Case | Security Considerations | Recommendation |
| :---- | :---- | :---- | :---- | :---- |
| os | os.path.join, os.listdir, os.remove | Legacy file and path operations. | Prone to errors with string-based paths; less intuitive than modern alternatives. | Avoid for new development; use pathlib instead. |
| pathlib | Path, .iterdir(), .read\_text(), .write\_text(), .resolve() | Modern, object-oriented filesystem path manipulation. | Provides a more secure and less ambiguous API, reducing the risk of path-related bugs. | **Mandatory** for all path construction and basic I/O. |
| shutil | copytree, rmtree, move | High-level file operations, including recursive directory actions. | Powerful functions that can be destructive; must be used within security wrappers. | Recommended for complex operations like copying or deleting entire directories. |

---

**Table 2.4: System Tool Security Threat Matrix**

| Tool Name | Potential Vulnerability | Threat Description | Mitigation Strategy (Code Pattern) |
| :---- | :---- | :---- | :---- |
| write\_file | Path Traversal | Attacker crafts a path like ../../etc/hosts to write outside the designated workspace. | Validate that os.path.realpath(path).startswith(BASE\_DIR) before any write operation.25 |
| read\_file | Path Traversal, Information Disclosure | Attacker reads sensitive system files like /etc/passwd or application source code. | Validate that os.path.realpath(path).startswith(BASE\_DIR) before any read operation.25 |
| run\_command | Command Injection, Privilege Escalation | Attacker injects shell commands (e.g., ls; rm \-rf /) or attempts to run commands as root. | Execute all commands in a Docker sandbox as a non-root user. Never use shell=True. Pass commands as a list of arguments.15 |
| All Tools | Prompt Injection | Attacker crafts input to trick the LLM into misusing a tool for malicious purposes. | Use strong prompt templating to separate instructions from data. Implement programmatic security wrappers on all tools as a backstop.32 |

---

## **Section 3: Autonomous Web Research Capabilities**

This section details the architecture for equipping the agent with a suite of tools for autonomous web research. The design balances the flexibility of direct web scraping with the reliability of managed search APIs, while embedding security considerations for handling untrusted external content.

### **3.1 Web Interaction Toolkit**

The foundation of the agent's web research capability is a set of tools for performing basic HTTP requests and parsing the resulting HTML content.

* **HTTP Requests:** The requests library is the de facto standard in Python for making HTTP requests and will be used for all direct web interactions.36 To ensure robustness, all tool implementations will adhere to best practices, including:  
  * **Setting Timeouts:** Every request will include a timeout parameter (e.g., timeout=10) to prevent the agent from hanging indefinitely on unresponsive servers.37  
  * **Error Handling:** The tools will check the HTTP status code of the response and handle non-200 codes gracefully, returning a clear error message to the agent instead of crashing.37  
  * **Session Management:** For tasks involving multiple requests to the same domain, a requests.Session() object will be used to leverage connection pooling and persistence of cookies, improving performance.36  
* **HTML Parsing:** Once HTML content is fetched, the BeautifulSoup library will be used for parsing and data extraction.39 It provides a powerful and intuitive API for navigating the DOM tree and extracting content based on tags, CSS classes, or IDs.39  
* **Core Tool Implementation:**  
  * fetch\_web\_page(url: str) \-\> str: This tool will take a URL, perform a GET request using the requests library, validate the response, and return the raw HTML content as a string.  
  * scrape\_url\_for\_text(url: str) \-\> str: A composite tool that first calls fetch\_web\_page and then pipes the resulting HTML into BeautifulSoup to extract and return all human-readable text, stripping away scripts and style tags.

### **3.2 Recursive Web Crawling Strategy**

For comprehensive research tasks, the agent must be able to explore a website beyond a single entry page. This requires a stateful, recursive crawling capability.

* **LangChain Component for Crawling:** Instead of building a crawler from scratch, we will leverage LangChain's RecursiveUrlLoader. This component is designed to start at a root URL and recursively follow hyperlinks up to a specified max\_depth, providing an efficient way to gather documents from a target site.42  
* **Content Extraction and Chunking:** The web is a source of untrusted input, and scraped content can contain malicious instructions designed to hijack the agent (an "indirect prompt injection").32 Therefore, all scraped text must be treated as potentially hostile. The prompt used to process this text must explicitly instruct the LLM to perform its task (e.g., summarize, extract facts) and to ignore any commands or instructions embedded within the scraped content. The hardened security wrappers on system tools (Section 2.4) serve as a final defense layer.  
  Furthermore, the context window of the qwen3:14b model is limited. Feeding it large, unstructured web pages will result in poor performance. To address this, a structure-aware chunking pipeline will be implemented:  
  1. The RecursiveUrlLoader will be configured with a custom extractor function that uses BeautifulSoup to convert raw HTML into clean text.42  
  2. The collection of resulting documents will be processed by HTMLHeaderTextSplitter. This splitter intelligently divides the documents based on semantic boundaries like \<h1\> and \<h2\> tags, preserving the document's logical structure.43  
  3. These semantically grouped chunks are then passed to a RecursiveCharacterTextSplitter to ensure each final chunk fits within a specified character limit, making them suitable for ingestion into the LLM's context window.43 This process of intelligent splitting acts as a form of pre-computation, simplifying the cognitive load on the LLM by providing it with smaller, contextually coherent pieces of information.  
* **Tool Implementation:**  
  * recursive\_crawl\_and\_summarize(url: str, query: str, depth: int \= 1): This advanced tool will orchestrate the entire crawling and RAG (Retrieval-Augmented Generation) process. It will use RecursiveUrlLoader to fetch and chunk documents, embed the chunks into a temporary in-memory vector store, perform a similarity search based on the user's query, and finally, pass the most relevant chunks to the LLM for a final summary. The agent's recursion limit must be carefully managed to prevent infinite loops, a known potential issue in graph-based agents.45

### **3.3 Integrating Managed Web Search APIs**

While direct scraping offers deep control, it can be unreliable and inefficient for general-purpose questions. Managed web search APIs provide a robust and fast alternative.

* **Tool Selection:** The TavilySearch tool will be integrated. It is specifically designed for use with LLMs, returning clean, concise summaries of search results rather than raw web page content, which is ideal for the limited context window of the local model.8  
* **Implementation:** A simple web\_search(query: str) tool will be created using TavilySearch(max\_results=3). The number of results is deliberately kept low to ensure the summarized context remains manageable for the qwen3:14b model.8  
* **Hybrid Routing Strategy:** The agent's primary reasoning loop (Section 1.3) will be responsible for choosing the appropriate web research tool. The system prompt will guide it to use web\_search for broad, open-ended questions ("What are the latest developments in AI?") and to use scrape\_url\_for\_text or recursive\_crawl\_and\_summarize when the user provides a specific URL or asks for a deep analysis of a particular website.

## **Section 4: Advanced Memory and Self-Reflection Mechanisms**

This section details the architecture for an advanced memory system that transcends simple conversational recall. It enables the agent to learn from interactions, persist knowledge across sessions, and autonomously recover from errors through a process of self-reflection.

### **4.1 Short-Term and Conversational Memory**

The ability to remember the immediate context of a conversation is a fundamental requirement for any chatbot.

* **Mechanism:** This will be implemented using LangGraph's built-in persistence layer, which is powered by **checkpointers**.6 When the graph is compiled with a checkpointer, it automatically saves a complete snapshot of the  
  AgentState after every node execution. This provides a durable record of the conversation's progression.  
* **Implementation:** For local development and ease of setup, langgraph\_checkpoint\_sqlite.SqliteSaver will be used to persist the state to a local SQLite database file. For production environments requiring higher concurrency, this can be swapped with langgraph\_checkpoint\_redis.RedisSaver.47 The checkpointer is integrated during the graph compilation step:  
  graph \= builder.compile(checkpointer=SqliteSaver.from\_conn\_string("agent\_memory.sqlite")).  
* **State and Session Management:** Each user conversation is managed as an independent **thread**. A unique thread\_id is passed in the configurable dictionary of every request, ensuring that the checkpointer saves and retrieves the state for the correct, isolated conversation.6 This mechanism is the foundation of the agent's short-term, turn-by-turn memory.

### **4.2 Long-Term Semantic and Episodic Memory**

To create a truly intelligent and personalized assistant, the agent must be able to learn and recall information across different conversations and sessions. This is achieved through a long-term memory system.

* **Conceptual Framework:** The memory system is structured around three types: semantic, episodic, and procedural.49 This plan focuses on implementing semantic and episodic memory, which store facts and experiences, respectively. The key architectural principle is that memory is not a monolith but a spectrum of context retrieval mechanisms. The agent's final prompt is a composite, assembled from multiple memory tiers to provide the richest possible context.  
* **Semantic Memory (Facts):** This memory type stores discrete pieces of knowledge, such as user preferences or key facts learned during interactions (e.g., "The user is a Python developer," "The user's favorite topic is machine learning").49  
  * **Implementation:** A VectorStore will serve as the backend for semantic memory. We will create two tools to interact with it:  
    * save\_memory(fact: str): This tool takes a factual statement, generates a vector embedding, and stores it in the vector store. Each memory entry will be namespaced with metadata like a user\_id to ensure data privacy and prevent context crossover.52  
    * search\_memory(query: str): This tool takes a query, embeds it, and performs a semantic similarity search against the vector store to retrieve the most relevant memories for the current context.53  
  * **Workflow Integration:** A dedicated load\_memories node will be added to the graph, executing at the beginning of each turn. This node uses search\_memory to retrieve relevant facts based on the latest user message and populates the long\_term\_memory field in the AgentState. The agent will also be prompted to proactively use the save\_memory tool when it identifies a new, important piece of information worth remembering.  
* **Episodic Memory (Experiences):** This memory type stores entire successful (or failed) task execution traces, which serve as few-shot examples to guide future behavior.51  
  * **Implementation:** Upon the successful completion of a complex, multi-step task, the sequence of (initial\_query, tool\_calls, final\_response) is packaged as an "episode" and stored as a document in a separate collection or vector store.  
  * **Workflow Integration:** When the agent encounters a new task, it can perform a semantic search over these stored episodes. If a highly relevant past experience is found, it is injected into the prompt as a one-shot or few-shot example, demonstrating a successful path to task completion for the LLM.

### **4.3 The Reflection Loop: Learning from Failure**

A truly robust agent should not just fail but learn from its failures. Inspired by the **Reflexion** framework, this architecture includes a cyclical, self-correcting loop for error handling.55 LangGraph's stateful nature and checkpointers are the core enabling technology for this pattern, as they allow the agent's execution to be paused, rerouted to an error-handling branch, and then resumed with new information.

* **LangGraph Implementation:**  
  1. **Error Detection and Routing:** A conditional edge placed after any ToolNode will inspect the error\_state field in the AgentState. If this field is populated (indicating a tool failure), the graph's execution is routed to a dedicated reflection\_node.  
  2. **Self-Critique Generation:** The reflection\_node is a specialized LLM call. It is prompted with the context of the failure: the original goal, the tool that was called, its input parameters, and the resulting error message or stack trace. The prompt explicitly asks the LLM to perform a self-critique: "The attempt to use tool \[tool\_name\] failed with the error \[error\_message\]. Analyze this failure and suggest a corrected tool call or an alternative approach."  
  3. **State Update and Retry:** The LLM's generated critique is added to the scratchpad in the AgentState. The error\_state's retry counter is incremented. The graph then routes execution back to the main agent node. This node now has the additional context of the self-critique in its scratchpad, allowing it to make a more informed second attempt at the task.  
  4. **Escalation:** If a predefined retry limit is exceeded, the graph can terminate the loop and escalate the failure, either by reporting the detailed failure to the user or by entering a human\_in\_the\_loop state to request assistance.  
* **Low-Level Retries:** For transient issues like network timeouts or temporary API failures, a full reflection loop is unnecessary. In these cases, the underlying LangChain Runnable that makes the network call can be wrapped with RunnableRetry. This provides an efficient, low-level mechanism for handling predictable, temporary errors with exponential backoff.58

---

**Table 4.1: Agent Memory Architecture Overview**

| Memory Type | Scope | Implementation Mechanism | LangGraph State Field | Use Case Example |
| :---- | :---- | :---- | :---- | :---- |
| **Short-Term / Conversational** | Single conversation thread | LangGraph Checkpointer (SqliteSaver, RedisSaver) | messages | Remembering the user asked "What about Paris?" after a previous question about London. |
| **Long-Term Semantic** | Across all conversations for a user | Vector Store (e.g., ChromaDB) \+ Embedding Model | long\_term\_memory | Recalling that the user prefers code examples in Python, even in a new conversation session. |
| **Long-Term Episodic** | Across all conversations | Vector Store or Document DB | Injected into prompt as few-shot examples | Retrieving a past successful workflow for "summarize and email a report" to guide a similar new request. |

---

## **Section 5: Content and Artifact Generation**

This section details the agent's capabilities for creating new content, specifically focusing on the generation of executable code and structured files from templates. The architectural design prioritizes a fundamental security principle: the strict decoupling of content *generation* from content *execution*.

### **5.1 A Framework for Custom Tool Creation**

The reliability of a tool-using agent, particularly one powered by a local LLM, is highly dependent on the quality of its tools' definitions.

* **Best Practice:** The @tool decorator from langchain\_core.tools will be the standard method for creating custom tools from Python functions. This approach is simple, declarative, and integrates seamlessly with the LangChain ecosystem.60  
* **Schema and Description:** It is mandatory for every tool function to have a detailed docstring and precise Python type hints for all arguments. The docstring serves as the tool's description, and the type hints are used by the LLM to construct the correct JSON schema for its arguments.61 A well-described tool (e.g.,  
  """Calculates the square root of a non-negative number.""") is far more likely to be used correctly by the LLM than one with a vague description (e.g., """math function""").9

### **5.2 Secure Code Generation and Execution**

To empower the agent with code generation capabilities, we will implement a multi-step workflow that emphasizes safety and iterative improvement, drawing inspiration from the AlphaCodium paper's "test and reflect" paradigm.62

This process fundamentally separates the act of writing code from the act of running it, which is the cornerstone of its security. The creative tool (generate\_python\_code) has no system privileges; it is a pure text transformer. All execution privilege is isolated within the run\_command\_in\_sandbox tool, which is heavily secured and containerized.

* **Tool and Workflow Implementation:**  
  1. **generate\_python\_code(task\_description: str) \-\> str Tool:** This tool takes a natural language description of a task (e.g., "a function that sorts a list of numbers"). It then prompts the qwen3:14b model to generate the corresponding Python code. The tool's only output is the generated code as a string. It performs no file I/O or execution.  
  2. **save\_code\_to\_file(code: str, filename: str) \-\> str Tool:** This utility tool uses the secure write\_file function defined in Section 2.1 to save the generated code string to a file within the agent's designated, sandboxed workspace.  
  3. **execute\_code\_in\_sandbox(filename: str) \-\> dict Tool:** This tool takes the filename of the saved script and uses the run\_command\_in\_sandbox tool from Section 2.2 to execute it (e.g., with the command \['python', filename\]). It securely captures and returns all output, including stdout, stderr, and the exit code.  
* **LangGraph Orchestration for Iterative Refinement:** The agent's graph will orchestrate this sequence to create a robust "generate-test-reflect-retry" loop:  
  1. The agent calls generate\_python\_code.  
  2. The graph routes to a node that calls save\_code\_to\_file.  
  3. The graph then routes to a node that calls execute\_code\_in\_sandbox.  
  4. A conditional edge checks the result. If the exit code is 0, the task is successful. If there is an error (stderr is not empty), the state is routed to the reflection\_node (from Section 4.3).  
  5. The reflection\_node analyzes the error and generates a critique, which is then fed back to the generate\_python\_code tool on the next attempt. This iterative process has been shown to substantially improve the quality and correctness of generated code.62

### **5.3 File Templating and Creation**

The agent will be equipped with a tool to generate structured text files (e.g., JSON configurations, Markdown reports, HTML pages) from predefined templates.

* **LangChain Component:** The tool will utilize LangChain's PromptTemplate.from\_file() method to load templates from a secure, read-only templates/ directory within the application's source code.63  
* **Tool Implementation:**  
  * create\_file\_from\_template(template\_name: str, output\_path: str, variables: dict) \-\> str: This tool will perform the following actions:  
    1. Securely construct the path to the template file (templates/{template\_name}) and validate that it exists.  
    2. Load the template using PromptTemplate.from\_file().  
    3. Invoke the template with the user-provided variables dictionary to render the final content.  
    4. Use the secure write\_file tool to save the rendered content to the specified output\_path within the agent's workspace.  
* **Security Considerations:** The research material contains a critical security warning regarding template formats. The jinja2 format can be vulnerable to arbitrary code execution if the template content is untrusted.63 Therefore, this implementation will  
  **mandate** the use of the default and safe f-string format for all templates. The agent will not be given the ability to create or modify template files themselves.

## **Section 6: Chainlit UI Integration and Streaming**

This section provides a practical guide for connecting the LangGraph-powered agent to a responsive and interactive user interface using Chainlit. The focus is on creating a transparent user experience by streaming the agent's internal state and thought processes in real-time.

### **6.1 Connecting LangGraph to Chainlit**

The integration point between the backend agent and the frontend UI is the Chainlit message handler.

* **Core Integration:** The compiled LangGraph app object, which is a LangChain Runnable, will be invoked within an async function decorated with @cl.on\_message. This function serves as the asynchronous entry point that is triggered every time a user sends a message through the Chainlit interface.64

### **6.2 Managing User Sessions and State**

To support concurrent users and maintain distinct conversation histories, each user session must be managed independently.

* **Session Isolation:** LangGraph's persistence mechanism is designed around the concept of a thread\_id. By assigning a unique thread\_id to each user's conversation, we ensure that the checkpointer saves and retrieves state for the correct session, preventing data leakage or context crossover between users.6  
* **Implementation:** Chainlit provides a unique session identifier through cl.context.session.thread\_id. This identifier will be passed into the RunnableConfig object during every invocation of the LangGraph application. This links the Chainlit session directly to a LangGraph persistence thread.64

Python

\# Example of configuring the graph invocation with a session-specific thread\_id  
config \= {  
    "configurable": {  
        "thread\_id": cl.context.session.thread\_id  
    }  
}  
\# The 'config' object is then passed to the app.stream() or app.invoke() call

### **6.3 Implementing Real-Time Streaming**

Streaming is not merely a cosmetic feature; it is essential for building user trust and providing transparency into the agent's complex, multi-step reasoning processes. A blank loading screen for 15 seconds can feel like a failure, whereas a stream of updates showing the agent's progress transforms the user's experience from one of frustration to one of anticipation.

* **LangGraph Streaming Capabilities:** The agent's compiled app object exposes an astream() method that will be used to stream outputs back to the client in real-time.66 LangGraph supports multiple, simultaneous streaming modes, which we will combine to create a rich, informative UI.  
* **Implementation Strategy:**  
  1. **Initialize an Empty Message:** Inside the @cl.on\_message handler, an empty cl.Message is created and sent to the UI immediately. This provides an initial placeholder that will be populated with streamed content.64  
  2. **Invoke the Stream:** The app.astream() method is called with the user's input and the session-specific config. We will request multiple stream modes: stream\_mode=\["updates", "messages"\].66  
  3. **Process the Streamed Chunks:** The application will asynchronously iterate over the chunks yielded by the stream.  
     * **Handling updates:** When a chunk from the updates stream arrives, it signifies that a node in the graph has just completed its execution. This information will be used to display status messages in the UI, such as "🔍 *Searching the web...*" or "⚙️ *Executing generated code...*". This provides the user with a clear, step-by-step view of the agent's actions.  
     * **Handling messages:** When a chunk from the messages stream arrives, it will typically be an AIMessageChunk containing a single token from the LLM's final response. This token is appended to the content of the empty message created in step 1, and await answer.update() is called to push the change to the UI. This process, repeated for each token, creates the smooth, "typing" effect that users expect from modern chatbots.64

This dual-mode streaming approach ensures the user receives both high-level updates about the agent's progress through its workflow and a real-time stream of the final generated answer, offering maximum transparency and a superior user experience.

## **Conclusion and Recommendations**

This research and implementation plan outlines a robust, secure, and feature-rich architecture for an AI agent system built on LangGraph, a local LLM, and a Chainlit UI. The proposed design addresses the core requirements of the user query by providing detailed strategies for integrating native system tools, autonomous web research capabilities, advanced memory with self-reflection, and secure content generation.

**Key Architectural Recommendations:**

1. **Adopt a Hierarchical Graph Structure:** For an agent powered by a local 14B LLM, a hierarchical routing graph that acts as a "cognitive scaffold" is essential. This approach breaks down complex tasks into simpler, more manageable steps, improving the reliability and predictability of the agent's behavior by reducing the cognitive load on the LLM.  
2. **Prioritize Security Through Isolation and Wrappers:** The principle of least privilege must be enforced programmatically. All system command and code execution must be isolated within a Docker sandbox. Furthermore, all tools that interact with the filesystem or execute commands must be wrapped in security layers that perform validation (e.g., path traversal checks) before execution. Security should not be delegated to the LLM's discretion.  
3. **Implement a Multi-Tiered Memory System:** A combination of short-term conversational memory (via LangGraph checkpointers) and long-term semantic memory (via a vector store) is necessary to create an agent that is both context-aware and personalized. This allows the agent to recall information within a single session and across multiple interactions.  
4. **Integrate a "Reflexion" Loop for Resilience:** The ability to detect, analyze, and recover from errors is a hallmark of an advanced agent. The proposed self-reflection sub-graph, enabled by LangGraph's stateful nature, transforms failures from terminal events into learning opportunities, significantly enhancing the agent's robustness.  
5. **Leverage Comprehensive Streaming for User Experience:** The integration with Chainlit should fully utilize LangGraph's multi-mode streaming capabilities. Streaming both node updates (updates) and LLM tokens (messages) provides critical transparency into the agent's reasoning process, building user trust and creating a more engaging and responsive interface.

By adhering to these architectural principles and implementation strategies, the resulting AI agent system will be well-equipped to handle complex, multi-step tasks in a secure, reliable, and transparent manner, fully leveraging the power of LangGraph's stateful orchestration while respecting the constraints and capabilities of a locally-hosted LLM.

#### **Works cited**

1. LangGraph Tutorial for Beginners \- Analytics Vidhya, accessed August 21, 2025, [https://www.analyticsvidhya.com/blog/2025/05/langgraph-tutorial-for-beginners/](https://www.analyticsvidhya.com/blog/2025/05/langgraph-tutorial-for-beginners/)  
2. Understanding State in LangGraph: A Beginners Guide | by Rick Garcia | Medium, accessed August 21, 2025, [https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997](https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997)  
3. LangGraph Tutorial: Enhanced State Management for Multi-Tool Agents \- Unit 2.2 Exercise 1 \- AI Product Engineer, accessed August 21, 2025, [https://aiproduct.engineer/tutorials/langgraph-tutorial-enhanced-state-management-for-multi-tool-agents-unit-22-exercise-1](https://aiproduct.engineer/tutorials/langgraph-tutorial-enhanced-state-management-for-multi-tool-agents-unit-22-exercise-1)  
4. LangGraph \- GitHub Pages, accessed August 21, 2025, [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)  
5. LangGraph \- LangChain, accessed August 21, 2025, [https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)  
6. Persistence \- Overview, accessed August 21, 2025, [https://langchain-ai.github.io/langgraph/concepts/persistence/](https://langchain-ai.github.io/langgraph/concepts/persistence/)  
7. LangGraph Agents with Multiple Tools — Prebuilt & Custom Approaches \- Medium, accessed August 21, 2025, [https://medium.com/@dharamai2024/langgraph-agents-with-multiple-tools-prebuilt-custom-approaches-b6208c5beb0f](https://medium.com/@dharamai2024/langgraph-agents-with-multiple-tools-prebuilt-custom-approaches-b6208c5beb0f)  
8. 2\. Add tools \- GitHub Pages, accessed August 21, 2025, [https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/](https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/)  
9. Tool calling | 🦜️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/concepts/tool\_calling/](https://python.langchain.com/docs/concepts/tool_calling/)  
10. About using tools in langgraph : r/LangChain \- Reddit, accessed August 21, 2025, [https://www.reddit.com/r/LangChain/comments/1fsx8at/about\_using\_tools\_in\_langgraph/](https://www.reddit.com/r/LangChain/comments/1fsx8at/about_using_tools_in_langgraph/)  
11. Route each tool from the ToolNode to a different graph chain ..., accessed August 21, 2025, [https://github.com/langchain-ai/langgraph/discussions/3004](https://github.com/langchain-ai/langgraph/discussions/3004)  
12. Working With Files in Python – Real Python, accessed August 21, 2025, [https://realpython.com/working-with-files-in-python/](https://realpython.com/working-with-files-in-python/)  
13. pathlib — Object-oriented filesystem paths — Python 3.13.7 documentation, accessed August 21, 2025, [https://docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html)  
14. The Python Standard Library — Python 3.13.7 documentation, accessed August 21, 2025, [https://docs.python.org/3/library/index.html](https://docs.python.org/3/library/index.html)  
15. A Guide to Python Subprocess \- Stackify, accessed August 21, 2025, [https://stackify.com/a-guide-to-python-subprocess/](https://stackify.com/a-guide-to-python-subprocess/)  
16. Command injection in Python: examples and prevention \- Snyk, accessed August 21, 2025, [https://snyk.io/blog/command-injection-python-prevention-examples/](https://snyk.io/blog/command-injection-python-prevention-examples/)  
17. Building a Sandboxed Environment for AI generated Code ..., accessed August 21, 2025, [https://anukriti-ranjan.medium.com/building-a-sandboxed-environment-for-ai-generated-code-execution-e1351301268a](https://anukriti-ranjan.medium.com/building-a-sandboxed-environment-for-ai-generated-code-execution-e1351301268a)  
18. Python Sandbox: Secure Python Code Execution for LLMs \- MCP Market, accessed August 21, 2025, [https://mcpmarket.com/server/python-sandbox](https://mcpmarket.com/server/python-sandbox)  
19. Making our own code interpreter: making of a sandbox | by Shrish \- Medium, accessed August 21, 2025, [https://medium.com/@Shrishml/making-our-own-code-interpreter-part-1-making-of-a-sandbox-382da3339eaa](https://medium.com/@Shrishml/making-our-own-code-interpreter-part-1-making-of-a-sandbox-382da3339eaa)  
20. Docker SDK for Python \- Read the Docs, accessed August 21, 2025, [https://docker-py.readthedocs.io/](https://docker-py.readthedocs.io/)  
21. Psutil module in Python \- GeeksforGeeks, accessed August 21, 2025, [https://www.geeksforgeeks.org/python/psutil-module-in-python/](https://www.geeksforgeeks.org/python/psutil-module-in-python/)  
22. Using the Psutil Module for System Monitoring \- DZone, accessed August 21, 2025, [https://dzone.com/articles/using-the-psutil-module-for-system-monitoring-bonu](https://dzone.com/articles/using-the-psutil-module-for-system-monitoring-bonu)  
23. System Monitoring Made Easy with Python's Psutil Library | by Ravi Tiwari | Medium, accessed August 21, 2025, [https://umeey.medium.com/system-monitoring-made-easy-with-pythons-psutil-library-4b9add95a443](https://umeey.medium.com/system-monitoring-made-easy-with-pythons-psutil-library-4b9add95a443)  
24. Path Traversal | OWASP Foundation, accessed August 21, 2025, [https://owasp.org/www-community/attacks/Path\_Traversal](https://owasp.org/www-community/attacks/Path_Traversal)  
25. Path Traversal and remediation in Python | by Ajay Monga \- OSINT Team, accessed August 21, 2025, [https://osintteam.blog/path-traversal-and-remediation-in-python-0b6e126b4746](https://osintteam.blog/path-traversal-and-remediation-in-python-0b6e126b4746)  
26. Subprocess management — Python 3.13.7 documentation, accessed August 21, 2025, [https://docs.python.org/3/library/subprocess.html](https://docs.python.org/3/library/subprocess.html)  
27. What Is Least Privilege & Why Do You Need It? \- BeyondTrust, accessed August 21, 2025, [https://www.beyondtrust.com/blog/entry/what-is-least-privilege](https://www.beyondtrust.com/blog/entry/what-is-least-privilege)  
28. How to manage system commands safely | LabEx, accessed August 21, 2025, [https://labex.io/tutorials/python-how-to-manage-system-commands-safely-437718](https://labex.io/tutorials/python-how-to-manage-system-commands-safely-437718)  
29. python \- GTFOBins, accessed August 21, 2025, [https://gtfobins.github.io/gtfobins/python/](https://gtfobins.github.io/gtfobins/python/)  
30. Python \- escalate privileges while running \- Stack Overflow, accessed August 21, 2025, [https://stackoverflow.com/questions/20969320/python-escalate-privileges-while-running](https://stackoverflow.com/questions/20969320/python-escalate-privileges-while-running)  
31. CWE-250: Execution with Unnecessary Privileges (4.17) \- MITRE Corporation, accessed August 21, 2025, [https://cwe.mitre.org/data/definitions/250.html](https://cwe.mitre.org/data/definitions/250.html)  
32. Prompt Injection | OWASP Foundation, accessed August 21, 2025, [https://owasp.org/www-community/attacks/PromptInjection](https://owasp.org/www-community/attacks/PromptInjection)  
33. LLM01:2023 \- Prompt Injections, accessed August 21, 2025, [https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0\_1\_vulns/Prompt\_Injection.html](https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Prompt_Injection.html)  
34. Mitigating Indirect Prompt Injection Attacks on LLMs | Solo.io, accessed August 21, 2025, [https://www.solo.io/blog/mitigating-indirect-prompt-injection-attacks-on-llms](https://www.solo.io/blog/mitigating-indirect-prompt-injection-attacks-on-llms)  
35. LLM Prompt Injection Prevention \- OWASP Cheat Sheet Series, accessed August 21, 2025, [https://cheatsheetseries.owasp.org/cheatsheets/LLM\_Prompt\_Injection\_Prevention\_Cheat\_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)  
36. Requests: HTTP for Humans™ — Requests 2.32.5 documentation, accessed August 21, 2025, [https://requests.readthedocs.io/](https://requests.readthedocs.io/)  
37. Python's Requests Library (Guide) – Real Python, accessed August 21, 2025, [https://realpython.com/python-requests/](https://realpython.com/python-requests/)  
38. Python Requests \- GeeksforGeeks, accessed August 21, 2025, [https://www.geeksforgeeks.org/python/python-requests-tutorial/](https://www.geeksforgeeks.org/python/python-requests-tutorial/)  
39. BeautifulSoup Web Scraping: Step-By-Step Tutorial \- Bright Data, accessed August 21, 2025, [https://brightdata.com/blog/how-tos/beautiful-soup-web-scraping](https://brightdata.com/blog/how-tos/beautiful-soup-web-scraping)  
40. Beautiful Soup: Web Scraping with Python \- SerpApi, accessed August 21, 2025, [https://serpapi.com/blog/beautiful-soup-build-a-web-scraper-with-python/](https://serpapi.com/blog/beautiful-soup-build-a-web-scraper-with-python/)  
41. Implementing Web Scraping in Python with BeautifulSoup \- GeeksforGeeks, accessed August 21, 2025, [https://www.geeksforgeeks.org/python/implementing-web-scraping-python-beautiful-soup/](https://www.geeksforgeeks.org/python/implementing-web-scraping-python-beautiful-soup/)  
42. Recursive URL \- ️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/integrations/document\_loaders/recursive\_url/](https://python.langchain.com/docs/integrations/document_loaders/recursive_url/)  
43. How to split HTML | 🦜️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/how\_to/split\_html/](https://python.langchain.com/docs/how_to/split_html/)  
44. Is there any need of splitting Recursive Loader \#27248 \- GitHub, accessed August 21, 2025, [https://github.com/langchain-ai/langchain/discussions/27248](https://github.com/langchain-ai/langchain/discussions/27248)  
45. Recursion Limit in LangGraph agent : Recursion limit of 25 reached without hitting a stop condition \- Stack Overflow, accessed August 21, 2025, [https://stackoverflow.com/questions/79515242/recursion-limit-in-langgraph-agent-recursion-limit-of-25-reached-without-hitti](https://stackoverflow.com/questions/79515242/recursion-limit-in-langgraph-agent-recursion-limit-of-25-reached-without-hitti)  
46. Build an Agent \- ️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/tutorials/agents/](https://python.langchain.com/docs/tutorials/agents/)  
47. LangGraph & Redis: Build smarter AI agents with memory & persistence, accessed August 21, 2025, [https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)  
48. langgraph-checkpoint \- PyPI, accessed August 21, 2025, [https://pypi.org/project/langgraph-checkpoint/](https://pypi.org/project/langgraph-checkpoint/)  
49. Memory for agents \- LangChain Blog, accessed August 21, 2025, [https://blog.langchain.com/memory-for-agents/](https://blog.langchain.com/memory-for-agents/)  
50. New course with LangChain\! Long-Term Agentic Memory with LangGraph \- YouTube, accessed August 21, 2025, [https://www.youtube.com/watch?v=9E1e3ZW3-pw](https://www.youtube.com/watch?v=9E1e3ZW3-pw)  
51. Long-Term Agentic Memory with LangGraph \- DeepLearning.AI, accessed August 21, 2025, [https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/](https://www.deeplearning.ai/short-courses/long-term-agentic-memory-with-langgraph/)  
52. LangMem SDK for agent long-term memory \- LangChain Blog, accessed August 21, 2025, [https://blog.langchain.com/langmem-sdk-launch/](https://blog.langchain.com/langmem-sdk-launch/)  
53. A Long-Term Memory Agent | 🦜️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/versions/migrating\_memory/long\_term\_memory\_agent/](https://python.langchain.com/docs/versions/migrating_memory/long_term_memory_agent/)  
54. Long-term Memory in LLM Applications, accessed August 21, 2025, [https://langchain-ai.github.io/langmem/concepts/conceptual\_guide/](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)  
55. Reflexion | Prompt Engineering Guide, accessed August 21, 2025, [https://www.promptingguide.ai/techniques/reflexion](https://www.promptingguide.ai/techniques/reflexion)  
56. \#12: How Do Agents Learn from Their Own Mistakes? The Role of Reflection in AI, accessed August 21, 2025, [https://huggingface.co/blog/Kseniase/reflection](https://huggingface.co/blog/Kseniase/reflection)  
57. LangChain/LangGraph: Build Reflection Enabled Agentic | by TeeTracker \- Medium, accessed August 21, 2025, [https://teetracker.medium.com/build-reflection-enabled-agent-9186a35c6581](https://teetracker.medium.com/build-reflection-enabled-agent-9186a35c6581)  
58. RunnableRetry — LangChain documentation, accessed August 21, 2025, [https://python.langchain.com/api\_reference/core/runnables/langchain\_core.runnables.retry.RunnableRetry.html](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.retry.RunnableRetry.html)  
59. langchain\_core.runnables.retry.RunnableRetry — LangChain 0.2.17, accessed August 21, 2025, [https://api.python.langchain.com/en/latest/runnables/langchain\_core.runnables.retry.RunnableRetry.html](https://api.python.langchain.com/en/latest/runnables/langchain_core.runnables.retry.RunnableRetry.html)  
60. How to create tools | 🦜️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/how\_to/custom\_tools/](https://python.langchain.com/docs/how_to/custom_tools/)  
61. Tools | 🦜️ LangChain, accessed August 21, 2025, [https://python.langchain.com/docs/concepts/tools/](https://python.langchain.com/docs/concepts/tools/)  
62. LangGraph for Code Generation \- LangChain Blog, accessed August 21, 2025, [https://blog.langchain.com/code-execution-with-langgraph/](https://blog.langchain.com/code-execution-with-langgraph/)  
63. PromptTemplate — LangChain documentation, accessed August 21, 2025, [https://python.langchain.com/api\_reference/core/prompts/langchain\_core.prompts.prompt.PromptTemplate.html](https://python.langchain.com/api_reference/core/prompts/langchain_core.prompts.prompt.PromptTemplate.html)  
64. Building a Simple Chatbot with LangGraph and Chainlit: A Step-by ..., accessed August 21, 2025, [https://dev.to/jamesbmour/building-a-simple-chatbot-with-langgraph-and-chainlit-a-step-by-step-tutorial-4k6h](https://dev.to/jamesbmour/building-a-simple-chatbot-with-langgraph-and-chainlit-a-step-by-step-tutorial-4k6h)  
65. LangChain/LangGraph \- Chainlit, accessed August 21, 2025, [https://docs.chainlit.io/integrations/langchain](https://docs.chainlit.io/integrations/langchain)  
66. What's possible with LangGraph streaming \- Overview, accessed August 21, 2025, [https://langchain-ai.github.io/langgraph/concepts/streaming/](https://langchain-ai.github.io/langgraph/concepts/streaming/)