# **The Definitive Developer's Manual for Chainlit Customization and Control**

## **Introduction**

This manual provides an exhaustive technical reference for developers working with the Chainlit framework. It is designed to serve as a complete guide to two core areas of Chainlit development: the full API of @cl. decorators and the complete spectrum of User Interface (UI) customization capabilities. This document deliberately omits introductory topics such as installation to focus exclusively on the advanced control and modification of a Chainlit application.  
The first part of this manual is a comprehensive reference for every decorator available in the chainlit Python library. Decorators are the primary mechanism for structuring a Chainlit application, providing hooks into the chat lifecycle, defining backend logic, and integrating with the frontend UI. Each entry provides a detailed explanation of the decorator's purpose, a complete list of its parameters, and validated code examples demonstrating its practical application.  
The second part is a complete instruction manual for customizing the look, feel, and behavior of the Chainlit UI. This section provides a deep dive into the config.toml file, which acts as the central control panel for UI features. It then explores the full hierarchy of visual customization, from high-level theming using theme.json to granular control with custom CSS, JavaScript, and the creation of bespoke interactive components using JSX.  
This document is intended for a developer with an existing proficiency in Python who requires a direct, unambiguous, and comprehensive resource to master the full capabilities of the Chainlit framework.

# **Part I: The Complete @cl. Decorator Reference**

This section serves as a definitive API reference for all decorators within the Chainlit framework. Decorators are the primary mechanism for defining application logic, managing the chat lifecycle, and integrating backend operations with the frontend UI. Each decorator entry follows a standardized format: Purpose, Parameters, and a detailed Usage Example.

## **1.0 Life Cycle Hook Decorators**

These decorators are fundamental to any Chainlit application, providing hooks into the key events of a user's chat session, from its creation to its termination. They are the entry points for defining the application's core conversational logic.

### **1.1 @cl.on\_chat\_start: Executing Code on Session Initialization**

**Purpose**  
The @cl.on\_chat\_start decorator registers an asynchronous function to be executed at the very beginning of a new chat session. This event fires immediately after the client establishes a WebSocket connection with the server. It is the ideal location for performing setup tasks, sending a welcome message, initializing user session variables, or preparing resources that will be needed throughout the conversation.  
**Parameters**  
This decorator does not accept any parameters itself, and the decorated function is called without any arguments.  
**Usage Example**  
The following example demonstrates a common use case: sending an initial welcome message to the user and setting a value in the user\_session for later use.  
`import chainlit as cl`

`@cl.on_chat_start`  
`async def start_chat():`  
    `# Store a user-specific value in the session`  
    `cl.user_session.set("session_start_time", "2023-01-01T12:00:00Z")`

    `# Send a welcome message to the UI`  
    `await cl.Message(`  
        `content="Welcome to the Chainlit Assistant! How can I help you today?",`  
        `author="System"`  
    `).send()`

### **1.2 @cl.on\_message: Handling User Input**

**Purpose**  
The @cl.on\_message decorator is arguably the most critical hook for building conversational logic. It registers a function that will be triggered every time a user submits a message through the UI. The decorated function receives the user's message as a cl.Message object, providing the entry point for processing the input, interacting with language models or other tools, and generating a response.  
**Parameters**  
The decorated function must accept the following parameter:

* **message**:  
  * **Type**: cl.Message  
  * **Description**: An object representing the message sent by the user. It contains attributes such as message.content (the text of the message), message.author, and any attached elements.

**Usage Example**  
This example shows a simple "echo bot" that receives a user's message and sends it back as a new message.  
`import chainlit as cl`

`@cl.on_message`  
`async def handle_message(message: cl.Message):`  
    `# The content of the user's message is accessed via the.content attribute`  
    `user_input = message.content`  
      
    `# Construct a response`  
    `response_content = f"You said: {user_input}"`  
      
    `# Send the response back to the user`  
    `await cl.Message(`  
        `content=response_content`  
    `).send()`

### **1.3 @cl.on\_chat\_end: Managing Session Disconnection**

**Purpose**  
The @cl.on\_chat\_end decorator registers a function to be executed when the user's session is terminated. This occurs when the WebSocket connection is closed, which can happen if the user closes the browser tab, refreshes the page, or navigates away. This hook is primarily used for cleanup tasks, such as saving the final state of the conversation, logging disconnection events, or releasing allocated resources.  
**Parameters**  
This decorator does not accept any parameters, and the decorated function is called without any arguments.  
**Usage Example**  
The following code demonstrates how to log a message to the console when a user's session ends, using a session ID initialized in @cl.on\_chat\_start.  
`import chainlit as cl`  
`import uuid`

`@cl.on_chat_start`  
`def start():`  
    `session_id = str(uuid.uuid4())`  
    `cl.user_session.set("id", session_id)`  
    `print(f"Chat session {session_id} started.")`

`@cl.on_chat_end`  
`def end():`  
    `session_id = cl.user_session.get("id")`  
    `print(f"Chat session {session_id} has ended.")`

### **1.4 @cl.on\_chat\_resume: Restoring Persisted Conversations**

**Purpose**  
The @cl.on\_chat\_resume decorator enables the application to restore a previously persisted chat session, allowing users to continue their conversations seamlessly. For this feature to function, both data persistence and user authentication must be enabled in the application's configuration. When a user resumes a conversation, the decorated function is called, providing a hook to re-initialize the application's state.  
While Chainlit automatically handles the restoration of the message history to the UI and any JSON-serializable data stored in cl.user\_session, it does not and cannot automatically restore complex, non-serializable Python objects. This includes instances of language models, database connections, or stateful clients from libraries like LangChain or LlamaIndex. The developer is responsible for using this hook to explicitly reconstruct these objects and re-attach them to the user session, ensuring the application's logic can continue from where it left off. Failure to do so will result in an application that displays the chat history but lacks the underlying logic to process new messages correctly.  
**Parameters**  
The decorated function must accept the following parameter:

* **thread**:  
  * **Type**: ThreadDict  
  * **Description**: A dictionary-like object containing the persisted metadata of the conversation thread being resumed.

**Usage Example**  
This example demonstrates the critical responsibility of the developer. While a simple value user\_name is automatically restored, the LLMChain object is not. The code within @cl.on\_chat\_resume manually re-instantiates the chain and sets it back into the user session.  
`import chainlit as cl`  
`from langchain.llms import OpenAI`  
`from langchain.chains import LLMChain`  
`from langchain.prompts import PromptTemplate`

`# This function is responsible for creating the agent/chain object.`  
`def create_llm_chain():`  
    `llm = OpenAI(temperature=0)`  
    `prompt = PromptTemplate(`  
        `template="Question: {question}\nAnswer: Let's think step by step.",`  
        `input_variables=["question"]`  
    `)`  
    `return LLMChain(prompt=prompt, llm=llm)`

`@cl.on_chat_start`  
`async def start():`  
    `# This runs for a brand new chat.`  
    `# Create and store the chain in the user session.`  
    `chain = create_llm_chain()`  
    `cl.user_session.set("llm_chain", chain)`  
    `cl.user_session.set("user_name", "New User")`

`@cl.on_chat_resume`  
`async def resume_chat(thread: cl.ThreadDict):`  
    `# This runs when a user continues a past conversation.`  
    `# The 'llm_chain' object was NOT persisted. We must recreate it.`  
    `print("Resuming chat. Re-initializing the LLMChain.")`  
    `chain = create_llm_chain()`  
    `cl.user_session.set("llm_chain", chain)`  
      
    `# The 'user_name' string WAS persisted and is automatically restored.`  
    `user_name = cl.user_session.get("user_name")`  
    `await cl.Message(content=f"Welcome back, {user_name}! Let's continue.").send()`

`@cl.on_message`  
`async def message(message: cl.Message):`  
    `# Retrieve the chain from the session.`  
    `# This works for both new and resumed chats because of our setup.`  
    `chain = cl.user_session.get("llm_chain")`  
    `res = await chain.acall(message.content, callbacks=[cl.AsyncLangchainCallbackHandler()])`  
    `await cl.Message(content=res["text"]).send()`

### **1.5 @cl.on\_stop: Intercepting User-Initiated Stops**

**Purpose**  
The @cl.on\_stop decorator registers a function that is executed when the user clicks the "stop" button in the UI. This button is typically used to interrupt a long-running process, such as a streaming response from a language model. This hook provides a mechanism for the application to gracefully handle the cancellation, log the interruption, or perform any necessary cleanup.  
**Parameters**  
This decorator does not accept any parameters, and the decorated function is called without any arguments.  
**Usage Example**  
`import chainlit as cl`  
`import asyncio`

`@cl.on_message`  
`async def main(message: cl.Message):`  
    `try:`  
        `# Simulate a long-running task`  
        `await cl.Message(content="Starting a 10-second task...").send()`  
        `await asyncio.sleep(10)`  
        `await cl.Message(content="Task finished!").send()`  
    `except asyncio.CancelledError:`  
        `# This block will be executed if the task is cancelled by on_stop`  
        `pass`

`@cl.on_stop`  
`def on_stop():`  
    `# This function is called when the user clicks the stop button`  
    `print("User has stopped the current task.")`  
    `# Chainlit handles the task cancellation automatically.`  
    `# We can add custom logging or cleanup here.`

### **1.6 @cl.on\_logout: Handling User Logout Events**

**Purpose**  
The @cl.on\_logout decorator registers a function to be executed when a user logs out of the application. This hook is essential for applications with authentication enabled. It is primarily used for session management and cleanup on the server side, such as clearing security-sensitive data stored in browser cookies.  
**Parameters**  
The decorated function can accept the following parameters, providing access to the underlying web request and response objects from the FastAPI framework:

* **request**:  
  * **Type**: fastapi.Request  
  * **Description**: The incoming request object.  
* **response**:  
  * **Type**: fastapi.Response  
  * **Description**: The outgoing response object, which can be modified.

**Usage Example**  
This example demonstrates how to use the response object to delete a cookie named "session\_token" when the user logs out.  
`from fastapi import Request, Response`  
`import chainlit as cl`

`@cl.on_logout`  
`def on_logout(request: Request, response: Response):`  
    `print(f"User {request.user} is logging out.")`  
    `# Use the response object to clear a browser cookie`  
    `response.delete_cookie("session_token")`  
    `print("Session token cookie cleared.")`

### **1.7 @cl.on\_audio\_chunk & @cl.on\_audio\_end: Processing Real-time Audio Input**

**Purpose**  
These two decorators work in tandem to enable real-time voice processing capabilities.

* @cl.on\_audio\_chunk: This decorator registers a function that is called repeatedly for each small packet (or "chunk") of audio data that is streamed from the user's microphone. It is the foundation for features requiring live processing, such as real-time transcription or voice activity detection.  
* @cl.on\_audio\_end: This decorator registers a function that is called once the audio recording is complete (e.g., the user stops speaking or clicks a button). It is used to process the full audio recording after it has been captured.

**Parameters**

* For @cl.on\_audio\_chunk, the decorated function must accept:  
  * **chunk**:  
    * **Type**: cl.InputAudioChunk  
    * **Description**: An object representing a single chunk of audio data from the microphone.  
* For @cl.on\_audio\_end, the decorated function does not accept any parameters.

**Usage Example**  
This example shows how audio chunks can be collected in the user session and then processed as a whole when the recording ends.  
`from io import BytesIO`  
`import chainlit as cl`

`@cl.on_chat_start`  
`async def start():`  
    `# Initialize a buffer in the session to store audio chunks`  
    `cl.user_session.set("audio_buffer", BytesIO())`  
    `await cl.Message(content="Press the microphone button and start speaking.").send()`

`@cl.on_audio_chunk`  
`async def on_audio_chunk(chunk: cl.InputAudioChunk):`  
    `# Append the incoming audio chunk to our buffer`  
    `audio_buffer = cl.user_session.get("audio_buffer")`  
    `audio_buffer.write(chunk.data)`

`@cl.on_audio_end`  
`async def on_audio_end():`  
    `# Get the full audio buffer from the session`  
    `audio_buffer = cl.user_session.get("audio_buffer")`  
    `audio_buffer.seek(0)`  
    `audio_bytes = audio_buffer.read()`  
      
    `# Here you would process the full audio_bytes,`  
    `# e.g., send to a speech-to-text API.`  
      
    `await cl.Message(`  
        `content=f"Received audio recording of {len(audio_bytes)} bytes."`  
    `).send()`  
      
    `# Reset the buffer for the next recording`  
    `cl.user_session.set("audio_buffer", BytesIO())`

## **2.0 Core Functionality Decorators**

These decorators enable key features of the Chainlit UI and interaction model, such as visualizing the agent's reasoning process, handling button clicks, and defining different chatbot personas.

### **2.1 @cl.step: Visualizing Chains of Thought**

**Purpose**  
The @cl.step decorator is a powerful tool for providing transparency into an agent's reasoning process. It wraps a function, causing it to be rendered in the UI as a distinct, collapsible "step" within the Chain of Thought (CoT) visualization. By default, the arguments passed to the decorated function are displayed as the step's "input," and the function's return value is displayed as its "output". This is fundamental for debugging and for building user trust by showing how an answer was derived. Steps can be nested by calling one decorated function from within another, creating a clear hierarchy in the UI.  
A notable and important constraint exists in the frontend rendering of steps. The UI will automatically prepend the prefixes "Using" (while the step is running) and "Used" (when the step is complete) to the step's name. This behavior is hardcoded in the frontend Step.tsx component and cannot be disabled or customized via any backend Python code or configuration. Developers who require the removal of these prefixes must either fork the Chainlit repository to modify the frontend source code or attempt to hide the prefixes using custom CSS, which can be a brittle solution.  
**Parameters**

* **name**:  
  * **Type**: str  
  * **Description**: The name of the step to be displayed in the UI. If not provided, it defaults to the name of the decorated function.  
* **type**:  
  * **Type**: str  
  * **Default**: "undefined"  
  * **Description**: A category for the step, such as "tool" or "llm". This can be used for custom styling, monitoring, or debugging purposes.  
* **language**:  
  * **Type**: str  
  * **Description**: Specifies the language for syntax highlighting of the step's output content. A list of supported languages is available.  
* **show\_input**:  
  * **Type**: Union\[bool, str\]  
  * **Default**: False  
  * **Description**: Controls the visibility of the step's input. If set to True, the input is shown as plain text. If set to a language string (e.g., "json" or "python"), the input is shown with syntax highlighting.

**Usage Example**  
This example demonstrates a parent step that calls a nested child step. It also shows how to access and modify the current step's properties using cl.context.current\_step.  
`import chainlit as cl`  
`import asyncio`

`@cl.step(name="Parent Process")`  
`async def parent_step(user_query: str):`  
    `# Access the current step to modify its properties`  
    `current_step = cl.context.current_step`  
    `current_step.input = f"Processing query: {user_query}"`  
      
    `await cl.sleep(1) # Simulate work`  
      
    `# Call a nested step`  
    `tool_result = await child_tool(param1="value1")`  
      
    `final_output = f"Parent process finished. Child tool returned: {tool_result}"`  
    `current_step.output = final_output`  
      
    `return final_output`

`@cl.step(name="Child Tool", type="tool", show_input=True)`  
`async def child_tool(param1: str):`  
    `await cl.sleep(2) # Simulate tool execution`  
    `return "This is the response from the child tool."`

`@cl.on_message`  
`async def main(message: cl.Message):`  
    `await cl.Message(content="Starting the process...").send()`  
    `final_result = await parent_step(message.content)`  
    `await cl.Message(content=f"Final Result: {final_result}").send()`

### **2.2 @cl.action\_callback: Creating Interactive Button Logic**

**Purpose**  
The @cl.action\_callback decorator defines the backend logic that is executed when a user clicks an interactive cl.Action button in the UI. The decorator must be supplied with a name that uniquely identifies the action it is responsible for handling.  
**Parameters**  
The decorator itself takes one positional argument:

* **name**:  
  * **Type**: str  
  * **Description**: The name of the action to listen for. This string must exactly match the name attribute of the cl.Action object that was sent to the UI.

The decorated function must accept the following parameter:

* **action**:  
  * **Type**: cl.Action  
  * **Description**: The Action object that was clicked. This object contains the payload that was defined when the action was created, allowing data to be passed from the frontend click event to the backend logic.

**Usage Example**  
This example creates two action buttons. The callback function inspects the payload of the clicked action to determine what message to send.  
`import chainlit as cl`

`@cl.on_chat_start`  
`async def start():`  
    `actions =`  
    `await cl.Message(`  
        `content="What would you like?",`  
        `actions=actions`  
    `).send()`

`@cl.action_callback("ask_fact")`  
`async def on_action_fact(action: cl.Action):`  
    `if action.payload.get("type") == "fact":`  
        `await cl.Message(content="The Eiffel Tower can be 15 cm taller during the summer.").send()`  
      
    `# Optionally, remove the button after it's been clicked`  
    `await action.remove()`

`@cl.action_callback("ask_joke")`  
`async def on_action_joke(action: cl.Action):`  
    `if action.payload.get("type") == "joke":`  
        `await cl.Message(content="Why don't scientists trust atoms? Because they make up everything!").send()`  
      
    `await action.remove()`

### **2.3 @cl.set\_chat\_profiles: Defining Multiple Assistant Personas**

**Purpose**  
The @cl.set\_chat\_profiles decorator registers a function that defines a list of available "chat profiles." These profiles appear in a dropdown menu in the UI, allowing the user to select from different pre-configured assistants or application modes. This feature is far more than a cosmetic change; it is a powerful mechanism for implementing entirely different logic paths within a single application. By checking the selected profile in the user\_session, the application can dynamically alter system prompts, enable or disable tools, or switch between different language models.  
Furthermore, when authentication is enabled, the decorated function can accept the current\_user object as an argument. This allows the list of available profiles to be generated dynamically based on the user's role or permissions, making it a cornerstone for building multi-tenant or feature-gated conversational applications.  
**Parameters**  
The decorated function can optionally accept the following parameter if authentication is enabled:

* **current\_user**:  
  * **Type**: cl.User  
  * **Description**: An object representing the currently authenticated user.

**Usage Example**  
This example defines two chat profiles, "Helpful Assistant" and "Sarcastic Cowboy." The @cl.on\_chat\_start hook then retrieves the selected profile from the user session and sets the appropriate system prompt.  
`import chainlit as cl`

`SYSTEM_PROMPTS = {`  
    `"Helpful Assistant": "You are a kind and helpful AI assistant.",`  
    `"Sarcastic Cowboy": "You are a sarcastic cowboy AI assistant. Answer with a 'yeehaw' at the end."`  
`}`

`@cl.set_chat_profiles`  
`async def set_profiles():`  
    `return`

`@cl.on_chat_start`  
`async def start():`  
    `# Get the selected chat profile from the session`  
    `profile_name = cl.user_session.get("chat_profile")`  
      
    `# Set the system prompt based on the selected profile`  
    `system_prompt = SYSTEM_PROMPTS.get(profile_name, SYSTEM_PROMPTS["Helpful Assistant"])`  
    `cl.user_session.set("system_prompt", system_prompt)`  
      
    `await cl.Message(`  
        `content=f"Starting chat with {profile_name}. System prompt set."`  
    `).send()`

`@cl.on_message`  
`async def message(message: cl.Message):`  
    `system_prompt = cl.user_session.get("system_prompt")`  
    `# In a real app, you would use this system_prompt with your LLM call.`  
    `response = f"({system_prompt}) Echoing your message: {message.content}"`  
    `await cl.Message(content=response).send()`

## **3.0 Utility and Integration Decorators**

These decorators provide helpful utilities for common tasks like caching, as well as hooks for more advanced integrations with the UI and external services.

### **3.1 @cl.cache: Caching Expensive Operations**

**Purpose**  
The @cl.cache decorator is a simple yet powerful utility for optimizing performance. It caches the return value of the function it decorates. The first time the function is called, its code is executed, and the result is stored in an in-memory cache. On all subsequent calls, the cached result is returned instantly without re-executing the function's code. This is particularly effective for resource-intensive, deterministic operations that don't need to be run on every interaction, such as loading a large model from disk, fetching static data from a remote source, or performing a complex one-time calculation.  
**Parameters**  
The decorated function does not accept any parameters.  
**Usage Example**  
This example simulates loading a large data file, a process that takes 5 seconds. With the @cl.cache decorator, this delay only occurs the very first time a user sends a message. All subsequent messages will get the cached data instantly.  
`import chainlit as cl`  
`import time`

`@cl.cache`  
`def load_large_dataset():`  
    `print("Loading large dataset... this will take 5 seconds.")`  
    `time.sleep(5)`  
    `data = {"key": "value", "items": [span_0](start_span)[span_0](end_span)[span_1](start_span)[span_1](end_span)[span_2](start_span)[span_2](end_span)}`  
    `print("Dataset loaded and cached.")`  
    `return data`

`@cl.on_message`  
`async def main(message: cl.Message):`  
    `# The first time this is called, it will trigger load_large_dataset()`  
    `# and wait 5 seconds. Subsequent calls will be instantaneous.`  
    `dataset = load_large_dataset()`  
      
    `await cl.Message(`  
        `content=f"Successfully retrieved dataset: {str(dataset)}"`  
    `).send()`

### **3.2 @cl.author\_rename: Customizing Author Display Names**

**Purpose**  
The @cl.author\_rename decorator provides a clean and centralized way to transform backend author names into more user-friendly display names in the UI. When working with integrations like LangChain, the author of a message or step might be the name of a Python class (e.g., LLMMathChain). This decorator allows the developer to define a mapping from these technical identifiers to human-readable names (e.g., "Math Expert"), improving the overall user experience by abstracting away implementation details.  
**Parameters**  
The decorated function must accept the following parameter:

* **orig\_author**:  
  * **Type**: str  
  * **Description**: The original author string as determined by the backend.

The function should return a string, which will be the new author name displayed in the UI.  
**Usage Example**  
This example maps the author Chatbot (the default name from the config) to "Assistant" and a hypothetical CodeInterpreter tool to "Code Interpreter". Any other author name is left unchanged.  
`import chainlit as cl`

`@cl.author_rename`  
`def rename_author(orig_author: str) -> str:`  
    `author_map = {`  
        `"Chatbot": "Assistant",`  
        `"CodeInterpreter": "Code Interpreter"`  
    `}`  
    `return author_map.get(orig_author, orig_author)`

`@cl.on_message`  
`async def main(message: cl.Message):`  
    `# This message's author is "Chatbot", which will be renamed to "Assistant"`  
    `await cl.Message(`  
        `content="This is a response from the main assistant."`  
    `).send()`

    `# This message's author is "CodeInterpreter", which will be renamed`  
    `await cl.Message(`  
        `content="This is a response from the tool.",`  
        `author="CodeInterpreter"`  
    `).send()`

### **3.3 @cl.on\_window\_message: Communicating with Embedded IFrames**

**Purpose**  
The @cl.on\_window\_message decorator is designed for advanced use cases where a Chainlit application is embedded as an \<iframe\> within a larger, parent web application. This decorator registers a function to act as a listener for messages sent from the parent window to the Chainlit iframe using the standard window.postMessage Web API. This enables two-way communication, allowing the host page to send contextual information to the Chainlit app.  
**Parameters**  
The decorated function must accept the following parameter:

* **message**:  
  * **Type**: str  
  * **Description**: The message content sent from the parent window.

**Usage Example**  
This example sets up a listener in the Chainlit app. When the parent window sends a message, the Chainlit app receives it and sends a confirmation back using the cl.send\_window\_message() function.  
**Chainlit App (app.py)**  
`import chainlit as cl`

`@cl.on_window_message`  
`async def on_window_message(message: str):`  
    `# React to a message from the parent window`  
    `if message == "GET_STATUS":`  
        `# Send a message back to the parent window`  
        `await cl.send_window_message({"status": "ready"})`

**Parent Web Page (HTML/JS)**  
`<!DOCTYPE html>`  
`<html>`  
`<head>`  
    `<title>Parent App</title>`  
`</head>`  
`<body>`  
    `<iframe id="chainlit-iframe" src="http://localhost:8000" width="600" height="800"></iframe>`  
    `<button onclick="requestStatus()">Request Status from Chainlit</button>`

    `<script>`  
        `const iframe = document.getElementById('chainlit-iframe');`

        `function requestStatus() {`  
            `// Send a message to the iframe`  
            `iframe.contentWindow.postMessage("GET_STATUS", 'http://localhost:8000');`  
        `}`

        `// Listen for messages from the iframe`  
        `window.addEventListener('message', (event) => {`  
            `if (event.origin === 'http://localhost:8000') {`  
                `console.log('Message from Chainlit:', event.data);`  
                `if (event.data.status === 'ready') {`  
                    `alert('Chainlit app is ready!');`  
                `}`  
            `}`  
        `});`  
    `</script>`  
`</body>`  
`</html>`

### **3.4 @cl.on\_mcp\_connect & @cl.on\_mcp\_disconnect: Managing Model Context Protocol Connections**

**Purpose**  
These are advanced decorators for managing the lifecycle of Model Context Protocol (MCP) connections. MCP is a feature for integrating Chainlit with external tools or services in a standardized way.

* @cl.on\_mcp\_connect: This decorator registers a function that is called when a new MCP connection is successfully established. It is required for initializing the connection.  
* @cl.on\_mcp\_disconnect: This optional but recommended decorator registers a function that is called when an MCP connection is terminated. It is used for proper cleanup of connection-related resources.

The configuration for MCP, including enabling connection types like Server-Sent Events (SSE) or standard I/O (stdio), is managed in the config.toml file under the \[features.mcp\] section.  
**Parameters**

* For @cl.on\_mcp\_connect, the decorated function accepts:  
  * **connection**: The connection object.  
  * **session**: An mcp.ClientSession object.  
* For @cl.on\_mcp\_disconnect, the decorated function accepts:  
  * **connection**: The connection object.  
  * **session**: An mcp.ClientSession object.

**Usage Example**  
`import chainlit as cl`  
`from mcp import ClientSession`

`# MCP must be enabled in config.toml for this to work.`  
`# [features.mcp.sse]`  
`# enabled = true`

`@cl.on_mcp_connect`  
`async def on_mcp_connect(connection, session: ClientSession):`  
    `"""Called when an MCP connection is established"""`  
    `print(f"MCP Connection established: {connection.name}")`  
    `# Connection initialization logic would go here.`

`@cl.on_mcp_disconnect`  
`async def on_mcp_disconnect(connection, session: ClientSession):`  
    `"""Called when an MCP connection is disconnected"""`  
    `print(f"MCP Connection disconnected: {connection.name}")`  
    `# Connection cleanup logic would go here.`

# **Part II: The Exhaustive UI Customization Manual**

This part provides a comprehensive guide to modifying every aspect of the Chainlit user interface. We will explore the full hierarchy of customization, from high-level configuration file settings to granular, code-level control with custom CSS, JavaScript, and JSX components.

## **4.0 Configuration-Driven Customization: The config.toml File**

The .chainlit/config.toml file is the primary control panel for high-level UI and feature configuration. It is created automatically when you first run chainlit run or chainlit init. This file allows developers to significantly alter the application's behavior and appearance without modifying any Python code.

### **4.1 The \[UI\] Section: Core Interface Controls**

This section of the config.toml file controls the most visible and fundamental aspects of the UI's appearance and behavior, from the application's name to the display of the reasoning chain.  
\<br\>  
**Table 1: \[UI\] Configuration Keys**

| Key | Type | Default Value | Description |
| :---- | :---- | :---- | :---- |
| name | str | "My Chatbot" | Sets the display name for both the application and the default chatbot author. |
| description | str | "" | Populates the \<meta name="description"\> HTML tag for SEO and browser tab descriptions. |
| cot | str | "full" | Controls the Chain of Thought (CoT) visibility. Options: "full" (show all steps), "tool\_call" (only show tool steps), "hidden" (hide the CoT panel entirely). |
| default\_collapse\_content | bool | true | If true, large message contents are automatically collapsed in the UI to maintain a concise thread view. |
| default\_expand\_messages | bool | false | If true, nested messages (sub-steps) are expanded by default. Otherwise, they are collapsed and must be clicked to be viewed. |
| github | str | "" | A URL to a GitHub repository. If provided, a GitHub icon linking to this URL will appear in the application header. |
| custom\_css | str | "" | A path to a local CSS file (e.g., "/public/style.css") or an external URL to a stylesheet for custom styling. |
| custom\_js | str | "" | A path to a local JavaScript file (e.g., "/public/script.js") or an external URL to a script to be injected into the application. |
| login\_page\_image | str | "" | Path to a local image (e.g., "/public/background.jpg") or an external URL for a custom background on the login page (requires authentication). |
| login\_page\_image\_filter | str | "" | Applies a Tailwind CSS filter class (e.g., "brightness-50") to the login page image. |
| login\_page\_image\_dark\_filter | str | "" | Applies a Tailwind CSS filter class specifically when the UI is in dark mode (e.g., "contrast-200"). |
| hide\_cot | bool | false | A legacy/deprecated setting. Use the cot key instead for modern Chainlit versions. |

### **4.2 The \[features\] Section: Toggling UI/UX Behaviors**

This section acts as a feature flag system, allowing developers to enable or disable specific functionalities, many of which have a direct impact on the user interface and experience.  
\<br\>  
**Table 2: \[features\] Configuration Keys**

| Key | Type | Default Value | Description |
| :---- | :---- | :---- | :---- |
| user\_message\_autoscroll | bool | (Varies) | Enables or disables the automatic scrolling of the chat window to the newest message. |
| edit\_message | bool | (Varies) | Enables or disables the user's ability to edit messages they have already sent. |
| data\_persistence | bool | false | (Implicitly configured) Must be enabled to use features like @cl.on\_chat\_resume and to display chat history to authenticated users. |
| mcp.sse.enabled | bool | (Varies) | Enables the Server-Sent Events (SSE) connection type for the Model Context Protocol (MCP). |
| mcp.stdio.enabled | bool | (Varies) | Enables the standard I/O (stdio) connection type for the Model Context Protocol (MCP). |
| show\_readme\_as\_default | bool | true | A legacy setting that displayed the README.md by default. This has been superseded by the "Starters" concept in modern Chainlit versions. |

## **5.0 Advanced Visual Theming**

Chainlit provides two methods for altering the application's color scheme, fonts, and overall aesthetic. The modern theme.json approach is strongly recommended for its power and flexibility.

### **5.1 Method 1: Basic Theming in config.toml (Legacy)**

This simplified method allows for overriding basic Material UI theme colors directly within the config.toml file. While functional for quick adjustments, it offers far less control than the theme.json method and should be considered a legacy option. The configuration involves adding \[UI.theme.light\] and \[UI.theme.dark\] sections with keys like background, paper, and primary.main.

### **5.2 Method 2: Granular Control with public/theme.json**

This is the modern, recommended, and most powerful method for theming a Chainlit application. It provides complete, granular control over the application's entire design system by allowing the developer to override a comprehensive set of CSS variables.  
**File Location and Format**

* The theme file must be named theme.json and placed in the /public directory of your project.  
* All color values within this file **must** be specified using the HSL (Hue, Saturation, Lightness) format, represented as a string of space-separated values (e.g., "0 0% 100%" for white). Hexadecimal color codes are not supported.  
* External fonts, such as those from Google Fonts, can be loaded by adding their CSS URLs to the custom\_fonts array at the top of the file.

**The Shadcn/ui and Tailwind CSS Foundation**  
A critical aspect of Chainlit's frontend architecture is that it is built upon the popular and well-documented Shadcn/ui component library, which in turn uses Tailwind CSS. The CSS variables defined in theme.json are not arbitrary or specific to Chainlit; they are direct mappings to the core variables that power the entire Shadcn/ui design system.  
This connection is profoundly important for any developer serious about customization. It means that mastering Chainlit theming is equivalent to understanding Shadcn's theming conventions. Any documentation, tutorial, or example related to theming Shadcn/ui is directly applicable to Chainlit. This knowledge unlocks a much deeper understanding of how to style the application and provides the context for why the variables are named as they are.  
\<br\>  
**Table 3: Key theme.json CSS Variables**  
The following table lists the most important CSS variables that can be defined in theme.json for both light and dark modes. For a complete list and visual examples, consulting the Shadcn/ui theming documentation is highly recommended.

| Variable Name | Component Area | Description of Effect |
| :---- | :---- | :---- |
| \--background | General | The primary background color of the entire application page. |
| \--foreground | General | The primary text color used for most content. |
| \--font-sans | General | The font family used for sans-serif text throughout the app. |
| \--primary | General | The main accent color, used for buttons, links, and focused elements. |
| \--primary-foreground | General | The text color used on top of elements with a \--primary background. |
| \--card | Components | The background color of card-like elements, such as messages. |
| \--card-foreground | Components | The text color used inside card-like elements. |
| \--border | Components | The color of borders and dividers between elements. |
| \--input | Components | The background color of input fields. |
| \--ring | Components | The color of the focus ring that appears around interactive elements. |
| \--sidebar-background | Sidebar | The background color of the main sidebar (if present). |
| \--sidebar-foreground | Sidebar | The text color used within the sidebar. |
| \--sidebar-primary | Sidebar | The accent color for active or highlighted items within the sidebar. |
| \--sidebar-border | Sidebar | The color of the border separating the sidebar from the main content. |

## **6.0 Asset-Based Branding and Customization**

This section details how to brand the application using simple file-based conventions, which requires no code changes and is the fastest way to apply a custom identity to a Chainlit app.

### **6.1 Logos and Favicon**

To replace the default Chainlit branding with a custom logo and browser favicon, follow these steps:

1. **Create Logos**: Prepare two versions of your logo in PNG format: logo\_dark.png for use in dark mode and logo\_light.png for use in light mode.  
2. **Place Logos**: Place both logo files directly inside the /public directory at the root of your project.  
3. **Create Favicon**: Create a favicon file (e.g., favicon.png or favicon.ico) and place it in the /public directory as well.  
4. **Restart and Refresh**: Restart the Chainlit application. You may need to perform a hard refresh or clear your browser's cache to see the changes, as these assets are often aggressively cached.

### **6.2 Avatars**

To customize the avatar image displayed next to messages from different authors:

1. **Create Directory**: Create a new folder named avatars inside your /public directory. The final path should be /public/avatars/.  
2. **Name and Place Avatars**: For each message author you wish to customize, create a PNG image. The filename must be the author's name converted to snake\_case. For example, if the message author is "My Custom Assistant", the image file must be named my\_custom\_assistant.png and placed in the /public/avatars/ directory.  
3. **Default Avatar**: If a custom avatar is not found for a given author, Chainlit will default to using the application's favicon as the avatar.

### **6.3 Login Page Customization**

When user authentication is enabled, the login screen can be customized with a branded background image. This is controlled via the \[UI\] section of the config.toml file.

* login\_page\_image: Set this key to the path of an image in your /public directory (e.g., "/public/login-bg.jpg") or to an external URL.  
* login\_page\_image\_filter: Optionally apply a Tailwind CSS filter class (e.g., "grayscale brightness-75") to the image.  
* login\_page\_image\_dark\_filter: Apply a different filter specifically for dark mode.

## **7.0 Code-Driven UI Elements and Interactions**

This section covers how to use Chainlit's Python classes and functions to generate interactive UI elements and control content presentation directly from your application logic.

### **7.1 Interactive UI Widgets**

* **cl.Action**: This class is the primary method for adding interactive buttons to a message. Each Action instance requires a name that links it to a @cl.action\_callback decorator, a label for the button text, and an optional payload dictionary to pass data from the frontend click to the backend logic.  
* **cl.ChatSettings**: This class creates a settings panel that is accessible via a gear icon in the chat input bar. You can populate this panel with various input widgets, such as cl.input\_widget.Select or cl.input\_widget.Slider, allowing the user to modify application parameters on the fly.

### **7.2 Content Display and Layout**

A critical mechanism for controlling UI layout is the display parameter, which is available on all cl.Element subclasses (Image, Text, PDF, Custom, etc.). It fundamentally changes how and where the element is rendered in the UI.

* **inline**: The element is rendered directly within the message flow.  
* **side**: The element is not rendered in the message. Instead, its name appears as a clickable link. When clicked, the element's content is displayed in a sidebar next to the chat thread.  
* **page**: Similar to side, the element's name appears as a clickable link, but clicking it redirects the user to a dedicated page that displays only that element's content.

### **7.3 UI Sound and Audio**

The sole method for incorporating sound into the Chainlit UI is the cl.Audio element. It is important to note that this is for displaying an audio player for a specific sound file, not for general UI sound effects (e.g., a notification chime). The cl.Audio class can be instantiated with a local file path, a remote url, or raw content in bytes. A key parameter is auto\_play: bool, which, if set to True, will cause the audio to begin playing automatically as soon as the element is rendered in the UI.

### **7.4 UI Text and Localization**

To modify or translate the static text strings built into the Chainlit UI (e.g., button labels, headers, placeholders), you must edit the translation files.

* **Location**: These files are located in the .chainlit/translations directory, named according to their language code (e.g., en-US.json).  
* **Method**: To change a piece of text, find its corresponding key in the JSON file and modify its string value. For example, to change the "Readme" tab label to "Instructions," you would find the key components.organisms.header.readme and change its value from "Readme" to "Instructions". This is also the standard mechanism for adding support for a new language by creating a new JSON file with the appropriate language code.

## **8.0 Advanced Frontend Injection and Overrides**

This final section covers the "escape hatches" for developers who need to go beyond the standard customization options and inject their own code directly into the frontend.

### **8.1 Injecting Custom CSS**

For situations where theme.json is insufficient and arbitrary CSS overrides are needed, Chainlit provides a direct injection mechanism.

* **Method**: In config.toml, set the custom\_css key under the \[UI\] section to either a local path (e.g., "/public/stylesheet.css") or an external URL of a stylesheet.  
* **Guidance**: Chainlit does not provide a documented list of its internal CSS classes. Therefore, developers are expected to use their browser's Web Inspector (Developer Tools) to identify the class name of the element they wish to modify and then write a corresponding CSS rule in their custom stylesheet to override its properties.

### **8.2 Injecting Custom JavaScript**

To run custom client-side JavaScript—for example, to integrate third-party analytics services like Google Analytics, user behavior tracking tools like Hotjar, or other external widgets—Chainlit offers a simple injection point.

* **Method**: In config.toml, set the custom\_js key under the \[UI\] section to a local path (e.g., "/public/my\_script.js") or an external URL of a JavaScript file. The script will be loaded and executed by the client's browser.

### **8.3 The Ultimate Escape Hatch: Building Custom JSX Elements**

For use cases that demand fully custom, interactive components beyond what standard elements or CSS/JS injection can provide, Chainlit offers the cl.CustomElement class. This feature fundamentally elevates Chainlit from a simple chatbot UI builder to a more general, chat-centric framework for building interactive web applications. It allows developers to write their own React components using JSX and render them as elements within the chat flow.  
The power of this feature lies in its bidirectional communication capabilities. The JSX component can call backend Python functions using callAction, and the Python backend can push updates to the component's state using element.update(). This enables the creation of complex, stateful UI widgets like interactive forms, data dashboards, or custom visualizations that live alongside and interact with the main conversation.  
**Workflow**

1. **Create the JSX File**: In your project's /public directory, create a new folder named elements. Inside this folder, create your JSX file (e.g., public/elements/MyComponent.jsx). The file must contain JSX code, not TSX.  
2. **Write the React Component**: The file must export a default React component. Component props are injected globally by Chainlit and should not be passed as function arguments. Styling is achieved using Tailwind CSS classes, which will respect the variables defined in your theme.json.  
3. **Instantiate in Python**: In your Python application, create an instance of the element: my\_element \= cl.CustomElement(name="MyComponent", props={"initial\_value": 42}). The name must match the JSX filename without the extension.  
4. **Send the Element**: Attach the custom element to a cl.Message and send it to the UI: await cl.Message(content="Check out this custom component\!", elements=\[my\_element\]).send().

**The JSX Environment: APIs and Limitations**  
Chainlit exposes a specific set of global APIs and enforces strict import limitations within the JSX environment.

* **Available APIs**:  
  * updateElement(nextProps): Updates the element's props from the frontend, triggering a re-render.  
  * deleteElement(): Removes the element from the UI.  
  * callAction({name, payload}): Calls a backend function decorated with @cl.action\_callback.  
  * sendUserMessage(message): Submits a message to the chat as if the user had typed it.  
* **Allowed Imports**: There is a strict allowlist of packages that can be imported, including react, lucide-react, and various UI components from the internal @/components/ui library (which are Shadcn components).

## **Conclusion**

This manual has provided a comprehensive and exhaustive exploration of Chainlit's decorator API and UI customization systems.  
The analysis of the decorator system reveals a well-structured set of hooks that grant developers precise control over the entire chat lifecycle. Decorators like @cl.on\_chat\_start and @cl.on\_message form the backbone of conversational logic, while more advanced hooks such as @cl.on\_chat\_resume and @cl.set\_chat\_profiles enable sophisticated features like state persistence and multi-persona applications. The @cl.step decorator, despite a minor hardcoded UI limitation, offers crucial transparency into agent reasoning.  
The investigation into UI customization demonstrates a powerful, layered approach. At the highest level, the config.toml file provides simple yet effective control over core features and branding. For deeper visual modification, the theme.json file, built upon the robust foundation of Shadcn/ui and Tailwind CSS, offers granular control over the entire design system. Finally, for ultimate flexibility, Chainlit provides a series of "escape hatches"—from custom CSS and JavaScript injection to the powerful cl.CustomElement class—that transform it from a constrained chatbot framework into a versatile platform for building rich, interactive web applications.  
By mastering these two domains—the decorator API and the customization hierarchy—developers can move beyond default configurations to build highly tailored, professional, and feature-rich conversational AI applications that meet specific branding and functional requirements.

#### **Works cited**

1\. on\_message \- Chainlit, https://docs.chainlit.io/api-reference/lifecycle-hooks/on-message 2\. on\_chat\_end \- Chainlit, https://docs.chainlit.io/api-reference/lifecycle-hooks/on-chat-end 3\. Chat History \- Chainlit, https://docs.chainlit.io/data-persistence/history 4\. on\_chat\_resume \- Chainlit, https://docs.chainlit.io/api-reference/lifecycle-hooks/on-chat-resume 5\. on\_logout \- Chainlit, https://docs.chainlit.io/api-reference/lifecycle-hooks/on-logout 6\. on\_audio\_end \- Chainlit, https://docs.chainlit.io/api-reference/lifecycle-hooks/on-audio-end 7\. Step Decorator \- Chainlit, https://docs.chainlit.io/api-reference/step-decorator 8\. Step \- Chainlit, https://docs.chainlit.io/concepts/step 9\. Action \- Chainlit, https://docs.chainlit.io/concepts/action 10\. Chat Profiles \- Chainlit, https://docs.chainlit.io/api-reference/chat-profiles 11\. cache \- Chainlit, https://docs.chainlit.io/api-reference/cache 12\. author\_rename and Message author \- Chainlit, https://docs.chainlit.io/api-reference/author-rename 13\. Web App \- Chainlit, https://docs.chainlit.io/deploy/webapp 14\. Window Messaging \- Chainlit, https://docs.chainlit.io/api-reference/window-message 15\. MCP Servers \- Chainlit, https://docs.chainlit.io/advanced-features/mcp 16\. Overview \- Chainlit, https://docs.chainlit.io/backend/config/overview 17\. UI \- Chainlit, https://docs.chainlit.io/backend/config/ui 18\. Theme \- Chainlit, https://docs.chainlit.io/customisation/theme 19\. Custom \- Chainlit, https://docs.chainlit.io/api-reference/elements/custom 20\. Logo and Favicon \- Chainlit, https://docs.chainlit.io/customisation/custom-logo-and-favicon 21\. Avatars \- Chainlit, https://docs.chainlit.io/customisation/avatars 22\. Migrate to Chainlit v1.1.300, https://docs.chainlit.io/guides/migration/1.1.300 23\. Audio \- Chainlit, https://docs.chainlit.io/api-reference/elements/audio 24\. CSS \- Chainlit, https://docs.chainlit.io/customisation/custom-css 25\. JS \- Chainlit, https://docs.chainlit.io/customisation/custom-js