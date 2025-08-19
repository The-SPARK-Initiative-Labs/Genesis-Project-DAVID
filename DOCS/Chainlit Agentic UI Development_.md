

# **Definitive Developer's Guide to Agentic UIs with Chainlit**

## **Introduction: Architecting Advanced Conversational Interfaces**

The modern AI imperative demands more than just powerful backend models; it requires transparent, interactive, and trustworthy user experiences. As large language models (LLMs) evolve into complex, multi-step agents that can reason, use tools, and execute tasks, the "black box" approach to conversational AI is no longer sufficient. Visualizing an agent's reasoning process—its chain of thought, its tool invocations, and its intermediate findings—has become a core requirement for user trust, effective debugging, and widespread adoption.1

Bridging the gap between sophisticated backend logic and an intuitive frontend experience presents a significant engineering challenge. Chainlit emerges as the premier open-source Python framework designed to solve this exact problem.1 It abstracts away the complexities of frontend development, allowing developers to focus exclusively on their Python logic while providing a rich, out-of-the-box UI toolkit for building production-ready conversational applications.4 From visualizing multi-step reasoning to handling data persistence and integrating with corporate authentication, Chainlit provides the necessary components to build ambitious and reliable AI systems.1

This report serves as a definitive developer's guide, structured to provide both immediate solutions and a long-term strategic reference for building advanced agentic UIs with Chainlit, specifically tailored to the needs of a project like "David". Part 1 delivers a direct, tactical solution to a critical UI rendering challenge. Part 2 offers a comprehensive, deep-dive reference into the library's most essential features, empowering developers to build, troubleshoot, and scale their applications with confidence.

---

## **Part 1: The Definitive UI Pattern: Displaying Steps Before the Final Message**

### **Problem Statement**

A fundamental requirement for a transparent agentic interface is the ability to display the agent's internal steps *before* it delivers its final answer. For a single conversational turn, the UI should first render an intermediate status update (e.g., "Thinking...", "Using Tool: Search API", "Analyzing Data") and only then display the conclusive text response from the agent. This sequential rendering, prominently featured in the official Chainlit overview 5, is crucial for managing user expectations during long-running tasks and providing insight into the agent's process. The challenge lies in correctly orchestrating the asynchronous communication between the Python backend and the frontend UI to enforce this specific rendering order.

### **The Asynchronous Control Flow Solution**

The solution to this UI ordering problem is rooted in the correct application of Python's asyncio control flow within the Chainlit framework. By defining a tool or thought process as an async function decorated with @cl.step and then using await to call it from the main @cl.on\_message handler, a developer can guarantee the step is displayed and completed before any subsequent code—including the sending of the final message—is executed.

The following self-contained app.py script provides a definitive, runnable demonstration of this pattern.

### **Annotated Code (app.py)**

Python

import chainlit as cl  
import asyncio

@cl.step(type="tool")  
async def thinking\_step():  
    """  
    This function is decorated with @cl.step, marking it as a distinct  
    step in the agent's reasoning process. The 'type="tool"' parameter  
    can be used to give it a specific icon or styling in the UI.  
    """  
    \# Simulate a long-running operation, like a tool call or API request.  
    await asyncio.sleep(2.5)  
      
    \# The step automatically completes when the function returns.  
    \# The return value can be captured and used in the main function.  
    return "The thinking step has concluded."

@cl.on\_message  
async def main(message: cl.Message):  
    """  
    This function is called every time a user sends a message in the UI.  
    It orchestrates the display of an intermediate step followed by the final answer.  
      
    Args:  
        message: The user's message object.  
    """  
      
    \# Send a preliminary message to acknowledge receipt of the user's query.  
    \# This is optional but good practice for responsiveness.  
    await cl.Message(  
        content=f"Processing your message: '{message.content}'..."  
    ).send()

    \# The key to the pattern: \`await\` the decorated step function.  
    \# Chainlit's backend detects this \`await\` on a step function and  
    \# immediately renders the step in the UI in a "loading" state.  
    \# The execution of this \`main\` function is PAUSED here until  
    \# the \`thinking\_step\` function completes.  
    step\_result \= await thinking\_step()

    \# This code will only execute AFTER \`thinking\_step\` has finished.  
    \# At this point, the step in the UI has transitioned to a "completed" state.  
    \# We can now send the final message, which will appear below the completed step.  
    await cl.Message(  
        content=f"This is the final answer. The tool returned: '{step\_result}'"  
    ).send()

To run this application, save the code as app.py and execute chainlit run app.py \-w in the terminal.5

### **The Role of cl.Step as a Control Flow Construct**

The @cl.step decorator is more than a simple UI directive; it acts as an asynchronous control flow construct that integrates directly with Python's asyncio event loop to manage UI rendering. The mechanism functions as follows:

1. A user's message triggers the @cl.on\_message coroutine, main.  
2. When the await thinking\_step() expression is encountered, the asyncio event loop is given control.  
3. The Chainlit backend, observing that the awaited coroutine is decorated with @cl.step, immediately sends a WebSocket message to the frontend, instructing it to render the "thinking\_step" UI element in an indeterminate or loading state.  
4. The main coroutine's execution is suspended at the await keyword. It cannot proceed to the final cl.Message(...).send() call.  
5. The thinking\_step coroutine runs to completion. In this example, it waits for 2.5 seconds.  
6. Once thinking\_step returns, the Chainlit backend sends another message to the frontend, updating the step's UI to a completed state, often displaying its duration.  
7. The await is now resolved, and control returns to the main coroutine, which resumes execution from the line following the await.  
8. Finally, the await cl.Message(...).send() line is executed, sending the final response to the UI, which correctly appears *after* the now-completed step.

This reveals a powerful architectural pattern: structuring an agent's internal processes (such as tool use, database queries, or complex calculations) into distinct, awaitable functions decorated with @cl.step is the fundamental method for building visually rich, step-by-step agent interactions in Chainlit.5

---

## **Part 2: Comprehensive Developer's Reference for the "David" Project**

This section provides a comprehensive reference guide to the Chainlit library, focusing on the features, classes, and patterns essential for building, troubleshooting, and scaling a sophisticated agentic application.

### **Section 2.1: Mastering the UI Toolkit: A Compendium of Chainlit Elements**

Elements are the visual building blocks for communicating rich, structured content beyond simple text messages. They can be attached to a cl.Message or a cl.Step to be displayed in the user interface.6 This section provides a reconstructed and comprehensive guide to the available UI elements.

#### **Core Elements**

* **cl.Message**  
  * **Description:** The fundamental unit of conversation, representing a single chat bubble in the UI. It can contain text, actions, and other elements.  
  * **Key Parameters:**  
    * content (str): The primary text content of the message.  
    * author (str, optional): The name of the message author, which maps to an avatar defined in config.toml.  
    * actions (List\[cl.Action\], optional): A list of interactive buttons to display with the message.  
    * elements (List\[cl.Element\], optional): A list of rich media elements to attach to the message.  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    await cl.Message(  
        content="Here is a message with an image.",  
        author="Data Analyst",  
        elements=\[cl.Image(path="./report.png", name="report", display="inline")\]  
    ).send()

* **cl.Step**  
  * **Description:** A visual component used to represent an intermediate step in an agent's reasoning or execution process. It can be used as a decorator (@cl.step) for automatic UI rendering tied to a function's execution, or instantiated directly for manual control.  
  * **Key Parameters (as decorator):**  
    * name (str, optional): The name of the step. Defaults to the function name.  
    * type (Literal\["llm", "tool", "embedding", "retrieval", "undefined"\], optional): The type of step, which can influence the icon displayed in the UI.  
  * **Code Example (Manual Instantiation):**  
    Python  
    import chainlit as cl  
    async with cl.Step(name="Manual Step", type\="tool") as step:  
        step.input \= "This is the input to the step."  
        await cl.sleep(1) \# Simulate work  
        step.output \= "This is the step's output."  
        await cl.Message(content="A message sent from within a step.").send()

* **cl.Action**  
  * **Description:** An interactive button displayed in the UI. When clicked, it triggers a corresponding backend function decorated with @cl.action\_callback.  
  * **Key Parameters:**  
    * name (str): The unique identifier for the action, used to link it to its callback.  
    * label (str): The text displayed on the button.  
    * value (str): A value associated with the action, often sent back to the server.  
    * payload (Dict, optional): A dictionary of custom data to send to the callback function.  
  * **Code Example:** See Section 2.2 for a full example with @cl.action\_callback.  
* **cl.Avatar**  
  * **Description:** Defines an avatar image for a message author. This is typically configured once in the config.toml file but can also be sent programmatically.  
  * **Key Parameters:**  
    * name (str): The name of the author this avatar belongs to.  
    * url (str) or path (str): The URL or local file path to the image.  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    @cl.on\_chat\_start  
    async def start():  
        await cl.Avatar(  
            name="Virtual Assistant",  
            url="https://example.com/avatar.png",  
        ).send()  
        await cl.Message(content="Hello\!", author="Virtual Assistant").send()

* **cl.Image**  
  * **Description:** Displays an image in the UI.  
  * **Key Parameters:**  
    * path (str) or url (str) or content (bytes): The source of the image.  
    * name (str): A name for the image, used for reference.  
    * display (Literal\["inline", "side", "page"\]): Determines how the element is displayed. "inline" shows it directly in the chat log, "side" shows a link that opens it in a sidebar, and "page" shows a link that opens it on a new page.6  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    await cl.Message(  
        content="Here is an inline image.",  
        elements=\[  
            cl.Image(path="./assets/chart.jpg", name="chart", display="inline")  
        \]  
    ).send()

* **cl.Text & cl.Pdf**  
  * **Description:** Used to send file-based content, such as plain text or PDF documents. They are particularly useful for displaying the sources used in a Retrieval-Augmented Generation (RAG) system.6  
  * **Key Parameters:** Similar to cl.Image, they accept path, name, content, and display.  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    source\_doc \= cl.Pdf(path="./sources/document.pdf", name="Source Document", display="side")  
    await cl.Message(  
        content="The answer was derived from the attached source.",  
        elements=\[source\_doc\]  
    ).send()

* **cl.Audio & cl.Video**  
  * **Description:** Embeds playable audio or video files in the chat interface.  
  * **Key Parameters:** Similar to other file-based elements, they accept path, name, content, and display.  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    await cl.Message(  
        content="Here is the audio summary:",  
        elements=\[  
            cl.Audio(path="./summary.mp3", name="summary", display="inline")  
        \]  
    ).send()

* **cl.Plotly & cl.Pyplot**  
  * **Description:** Renders interactive data visualizations created with the Plotly or Matplotlib (Pyplot) libraries directly in the UI.  
  * **Key Parameters:**  
    * figure (go.Figure or plt.Figure): The figure object to be rendered.  
    * name (str): A name for the plot.  
    * display (Literal\["inline", "side", "page"\]): The display mode.  
  * **Code Example (Plotly):**  
    Python  
    import chainlit as cl  
    import plotly.graph\_objects as go

    fig \= go.Figure(data=go.Bar(y=))  
    await cl.Message(  
        content="Here is a Plotly chart.",  
        elements=\[cl.Plotly(figure=fig, name="chart", display="inline")\]  
    ).send()

* **cl.TaskList**  
  * **Description:** A specialized element for displaying a list of sub-tasks with a title and completion status. It provides a structured way to show progress on a multi-part task.  
  * **Key Parameters:**  
    * title (str): The main title for the task list.  
    * status (Literal\["running", "failed", "done"\]): The overall status of the task list.  
    * tasks (List): A list of cl.Task objects.  
  * **Code Example:**  
    Python  
    import chainlit as cl  
    task\_list \= cl.TaskList(title="Processing Pipeline")  
    await task\_list.send() \# Send the initial empty list

    task1 \= cl.Task(title="Fetching data", status=cl.TaskStatus.RUNNING)  
    task\_list.tasks.append(task1)  
    await task\_list.send() \# Update the list with the first task

    await cl.sleep(1)  
    task1.status \= cl.TaskStatus.DONE  
    await task\_list.send() \# Update the task status

#### **The CustomElement: Unleashing Full Frontend Potential**

For scenarios requiring UI components beyond the standard set, Chainlit provides the cl.CustomElement class. This powerful feature allows developers to render their own custom JSX (a syntax extension for JavaScript) components, enabling virtually unlimited UI customization.7

* **File Structure:** Custom JSX files must be placed in the public/elements/ directory at the root of the Chainlit project. The name of the file (e.g., MyComponent.jsx) is used to reference it from Python.  
* **Passing Data:** Data is passed from the Python backend to the JSX component via the props dictionary.  
* **Interactivity:** Chainlit injects a global set of APIs into the JSX environment, allowing the custom component to communicate back with the backend 7:  
  * updateElement(nextProps): Re-renders the element with new props.  
  * deleteElement(): Removes the element from the UI.  
  * callAction({name: string, payload: object}): Triggers a @cl.action\_callback on the backend.  
  * sendUserMessage(message: string): Sends a message to the chat as if the user had typed it.  
* Example (Counter Element from Docs 7):  
  * **app.py:**  
    Python  
    import chainlit as cl

    @cl.on\_message  
    async def on\_message(msg: cl.Message):  
        initial\_props \= {"count": 0}  
        counter\_element \= cl.CustomElement(name="Counter", props=initial\_props)

        await cl.Message(  
            content="Here is a custom counter element\!",  
            elements=\[counter\_element\]  
        ).send()

  * **public/elements/Counter.jsx:**  
    JavaScript  
    import { Button } from "@/components/ui/button";  
    import { X, Plus } from 'lucide-react';

    export default function Counter() {  
     return (  
     \<div id\="custom-counter" className\="mt-4 flex flex-col gap-2"\>  
     \<div\>Count: {props.count}\</div\>  
     \<Button id\="increment" onClick\={() \=\> updateElement({...props, count: props.count \+ 1 })}\>  
        \<Plus className\="mr-2 h-4 w-4" /\> Increment  
     \</Button\>  
     \<Button id\="remove" variant\="destructive" onClick\={deleteElement}\>  
        \<X className\="mr-2 h-4 w-4" /\> Remove  
     \</Button\>  
     \</div\>  
     );  
    }

#### **Table 1: Chainlit UI Element Reference**

| Element Class | Description | Key Parameters | Common Use Case |
| :---- | :---- | :---- | :---- |
| cl.Message | The fundamental unit of conversation. | content, author, elements, actions | Sending any response to the user. |
| cl.Step | Visualizes an intermediate reasoning or tool use step. | name, type, input, output | Showing agent's chain of thought. |
| cl.Action | An interactive button that can trigger backend logic. | name, label, value, payload | User-driven events, choices, forms. |
| cl.Avatar | Defines a custom avatar for a message author. | name, path or url | Branding and differentiating speakers. |
| cl.Image | Displays an image. | path or url, name, display | Showing generated images, charts. |
| cl.Text | Displays plain text content, often from a file. | path or content, name, display | Displaying large text blocks or sources. |
| cl.Pdf | Embeds a PDF viewer. | path or content, name, display | Displaying source documents for RAG. |
| cl.Audio | Embeds a playable audio file. | path or content, name, display | Voice responses, transcriptions. |
| cl.Video | Embeds a playable video file. | path or content, name, display | Multimedia content, tutorials. |
| cl.Plotly | Renders an interactive Plotly chart. | figure, name, display | Data visualization, reports. |
| cl.Pyplot | Renders a static Matplotlib chart. | figure, name, display | Data visualization, scientific plots. |
| cl.TaskList | Displays a list of tasks with completion status. | title, status, tasks | Showing progress on a complex task. |
| cl.CustomElement | Renders a custom JSX component for full UI control. | name, props | Highly customized UI, interactive forms. |

### **Section 2.2: The Application Lifecycle and Event Handling**

Chainlit applications are built around an asynchronous, event-driven architecture. The core of any app is a set of functions decorated with lifecycle hooks that respond to specific user interactions or session events.4

#### **Core Lifecycle Decorators**

* **@cl.on\_chat\_start**  
  * **Trigger:** Executes once when a new user connects and a chat session begins.  
  * **Purpose:** Ideal for initialization tasks. This includes sending a welcome message, setting up API clients (e.g., for an LLM), loading models, or initializing the session state with default values.  
  * Code Example 4:  
    Python  
    import chainlit as cl

    @cl.on\_chat\_start  
    async def start\_chat():  
        await cl.Message(  
            content="Hello\! I am your personal research assistant. How can I help you today?"  
        ).send()

* **@cl.on\_message**  
  * **Trigger:** Executes every time the user sends a message.  
  * **Purpose:** This is the main workhorse of the application. The decorated function receives the user's message as an argument and is responsible for processing the input, calling the agent or LLM, and sending back one or more responses.  
  * Code Example 8:  
    Python  
    import chainlit as cl

    @cl.on\_message  
    async def handle\_message(message: cl.Message):  
        \# Main application logic goes here  
        response\_content \= f"You sent the message: '{message.content}'"  
        await cl.Message(content=response\_content).send()

* **@cl.action\_callback(name: str)**  
  * **Trigger:** Executes when a user clicks a cl.Action button whose name attribute matches the string provided in the decorator.  
  * **Purpose:** Enables interactive, non-text-based communication. It's used for handling user choices, submitting simple forms, or triggering specific, predefined functions. The decorated function receives the cl.Action object itself, which includes any payload data.  
  * Code Example 4:  
    Python  
    import chainlit as cl

    @cl.on\_chat\_start  
    async def show\_buttons():  
        actions \=  
        await cl.Message(content="Please respond.", actions=actions).send()

    @cl.action\_callback("agree")  
    async def on\_agree(action: cl.Action):  
        await cl.Message(content=f"You agreed. Value: {action.value}").send()

* **@cl.on\_stop**  
  * **Trigger:** Executes when the user clicks the "Stop" button (⏹) in the UI while an asynchronous task is running.  
  * **Purpose:** Allows for graceful cancellation of long-running operations. It can be used to clean up resources, log the interruption, or send a confirmation message to the user that the task has been stopped.  
  * Code Example 4:  
    Python  
    import chainlit as cl  
    import asyncio

    @cl.on\_message  
    async def long\_task(msg: cl.Message):  
        try:  
            await cl.Message(content="Starting a 10-second task...").send()  
            await asyncio.sleep(10)  
            await cl.Message(content="Task finished.").send()  
        except asyncio.CancelledError:  
            \# This block is not strictly necessary but is good practice  
            \# The @cl.on\_stop decorated function will be called regardless  
            print("Task was cancelled by user.")  
            raise

    @cl.on\_stop  
    async def on\_stop():  
        await cl.Message(content="Task stopped by user.").send()

* **@cl.on\_chat\_end**  
  * **Trigger:** Executes when a user's session ends, for example, by closing the browser tab or refreshing the page.  
  * **Purpose:** Useful for final cleanup, logging, or saving the session state to a persistent store.  
  * Code Example 4:  
    Python  
    import chainlit as cl

    @cl.on\_chat\_end  
    def end\_chat():  
        print("User has disconnected. Session ended.")

* **@cl.on\_chat\_resume**  
  * **Trigger:** Executes when a user reconnects to a previously established session. This hook is only active if data persistence is enabled in config.toml.  
  * **Purpose:** Allows the application to restore state and welcome the user back. It receives the cl.Thread object containing the history of the conversation.  
  * Code Example 4:  
    Python  
    import chainlit as cl

    @cl.on\_chat\_resume  
    async def resume\_chat(thread: cl.Thread):  
        await cl.Message(  
            content=f"Welcome back\! We were last discussing: '{thread.steps\[-1\].output}'"  
        ).send()

### **Section 2.3: State and Session Management with cl.user\_session**

Conversational AI applications are inherently stateful. To maintain context, remember previous interactions, and manage resources like API clients, a mechanism for storing data within a user's session is essential. Chainlit provides this through the cl.user\_session object.

While the specific API documentation for cl.user\_session was not directly available in the provided materials 9, its function and usage can be clearly determined from its practical application in the official integration examples.10 The

cl.user\_session object acts as a simple, dictionary-like key-value store that is scoped to a single user's chat session. Any data stored in it persists between events (like multiple @cl.on\_message calls) for that user but is isolated from other users' sessions.

#### **API Usage and Patterns**

* **cl.user\_session.set(key: str, value: Any)**  
  * **Purpose:** Stores an object in the current user's session, associating it with a given key. The value can be any Python object, from a simple string or list to a complex, instantiated class like an LLM client or a conversation buffer.  
  * **Best Practice:** Perform initialization of session variables in the @cl.on\_chat\_start function to ensure they are available from the very beginning of the conversation.  
* **cl.user\_session.get(key: str) \-\> Any**  
  * **Purpose:** Retrieves an object from the session using its key. If the key does not exist, it returns None.  
  * **Best Practice:** Use this function within @cl.on\_message or @cl.action\_callback to access state that was previously set, such as retrieving a conversation history to provide context to an LLM.  
* **cl.user\_session.remove(key: str)**  
  * **Purpose:** Deletes a key-value pair from the session. This is useful for clearing cached data or resetting parts of the session state.

#### **Code Example: Maintaining Conversation History**

This example demonstrates the canonical pattern for using cl.user\_session to store and update a conversation history list, a core requirement for most chatbots.

Python

import chainlit as cl

@cl.on\_chat\_start  
async def start\_chat():  
    \# Initialize an empty list for the conversation history in the user's session.  
    cl.user\_session.set("history",)  
    await cl.Message(content="Session started. History is now being tracked.").send()

@cl.on\_message  
async def handle\_message(message: cl.Message):  
    \# 1\. Retrieve the current history from the session.  
    history \= cl.user\_session.get("history")

    \# 2\. Append the new user message to the history.  
    history.append({"role": "user", "content": message.content})

    \# In a real application, you would now pass this history to an LLM.  
    \# For this example, we'll just simulate an agent's response.  
    agent\_response \= f"I have recorded your message. The history now has {len(history)} entries."

    \# 3\. Append the agent's response to the history.  
    history.append({"role": "assistant", "content": agent\_response})

    \# 4\. Update the history in the user's session with the new, longer list.  
    cl.user\_session.set("history", history)

    \# 5\. Send the response to the user.  
    await cl.Message(content=agent\_response).send()

### **Section 2.4: Advanced Asynchronous Patterns and Streaming**

Chainlit's foundation on Python's asyncio library is a deliberate design choice that enables it to handle many concurrent user sessions and I/O-bound operations (like network requests to LLM APIs) with high efficiency. Understanding how to work within this asynchronous paradigm is key to building responsive, high-performance applications.

#### **Streaming LLM Responses**

To create a "live" typing effect similar to ChatGPT, you should stream tokens from the LLM to the UI as they are generated. This dramatically improves the perceived performance of the application. The pattern involves creating an empty cl.Message and then populating it token-by-token using its stream\_token() method inside an async for loop.4

* **Code Example (Streaming with a Mock Generator):**  
  Python  
  import chainlit as cl  
  import asyncio

  async def mock\_llm\_stream(text):  
      \# This function simulates a streaming LLM response.  
      for token in text:  
          yield token  
          await asyncio.sleep(0.02)

  @cl.on\_message  
  async def stream\_message(message: cl.Message):  
      response\_text \= "This is a streamed response from the language model."

      \# 1\. Create an empty message object.  
      msg \= cl.Message(content="")  
      await msg.send() \# Send the empty message to create the UI element.

      \# 2\. Iterate over the async generator and stream each token.  
      async for token in mock\_llm\_stream(response\_text):  
          await msg.stream\_token(token)

      \# 3\. (Optional) Update the message once streaming is complete.  
      await msg.update()

#### **Handling Blocking Code with cl.make\_async**

A critical rule in asyncio programming is to never run long, synchronous, CPU-bound code directly, as it will block the entire event loop and freeze the UI for all users. Chainlit provides a utility, cl.make\_async, to safely run such functions in a separate thread pool, making them non-blocking and awaitable.11

* **The Problem:** A synchronous function that performs a heavy computation.  
  Python  
  import time  
  def blocking\_cpu\_task():  
      \# This function blocks for 5 seconds.  
      time.sleep(5)  
      return "CPU-intensive task complete."

* **The Solution:** Wrap the blocking function with cl.make\_async.  
  Python  
  import chainlit as cl

  \#... (blocking\_cpu\_task definition)...

  @cl.on\_message  
  async def handle\_blocking\_code(message: cl.Message):  
      await cl.Message(content="Starting a blocking task...").send()

      \# Create an awaitable version of the sync function.  
      non\_blocking\_task \= cl.make\_async(blocking\_cpu\_task)

      \# Await the task without blocking the event loop.  
      result \= await non\_blocking\_task()

      await cl.Message(content=result).send()

#### **Calling Async from Sync with cl.run\_sync**

Occasionally, it may be necessary to call an async Chainlit function from within a synchronous context (e.g., inside a library callback that is not async). For this purpose, Chainlit provides cl.run\_sync, which safely runs an awaitable from a synchronous function.11

* **The Problem:** A synchronous function needs to send a Chainlit message.  
* **The Solution:** Use cl.run\_sync to call the async .send() method.  
  Python  
  import chainlit as cl

  def my\_synchronous\_library\_function():  
      \# This function is not async, but needs to send a message.  
      message\_to\_send \= cl.Message(content="Message from a sync function.")

      \# Use run\_sync to execute the async send() method.  
      cl.run\_sync(message\_to\_send.send())

      return "Sync function finished."

### **Section 2.5: Configuring and Customizing the Chainlit Environment**

The config.toml file, located in the .chainlit directory of a project, provides a powerful mechanism for separating application logic from operational and UI configuration. This separation is a best practice for creating maintainable and deployable applications. The file is automatically created by running chainlit init.12

The configuration is organized into three main sections: \[project\], \[features\], and \[UI\].13

#### **Breakdown of Configuration Sections**

* **\[project\]:** Contains settings related to the project's operation and data persistence.  
  * public (bool): If true, the app is accessible to anonymous users. If false, authentication is required.14  
  * database (str): Configures chat history persistence. Options are "local" (creates a local database), "cloud" (uses Chainlit's cloud service), or "custom".14  
  * user\_env (List\[str\]): A list of environment variable names that the user will be prompted to provide in the UI before they can use the app (e.g., \`\`).14  
  * session\_timeout (int): Duration in seconds to save a session when a user disconnects, enabling chat resumption.14  
  * allow\_origins (List\[str\]): A list of allowed origins for Cross-Origin Resource Sharing (CORS). Essential for embedding the chatbot on an external website.15  
* **\[features\]:** Enables or disables specific application features.  
  * \[features.file\_uploads\]:  
    * allow\_file\_types (List\[str\]): A list of MIME types or extensions for allowed file uploads (e.g., \["text/plain", ".pdf"\]).4  
    * max\_size\_mb (int): The maximum size for an uploaded file in megabytes.  
* **\[UI\]:** Controls the appearance and behavior of the user interface.  
  * name (str): The name of the application and chatbot displayed in the UI header.14  
  * description (str): The meta description for the application's HTML page.  
  * github (str): A URL to a GitHub repository, which adds a GitHub icon link to the header.16  
  * cot (Literal\['hidden', 'tool\_call', 'full'\]): Controls the visibility of the Chain of Thought (step) elements. "hidden" hides all steps, "tool\_call" shows only tool steps, and "full" shows all steps.16  
  * default\_expand\_messages (bool): If true, nested messages (steps) are expanded by default.16  
  * \[UI.theme\]:\*\* Provides granular control over the light and dark theme colors, allowing for full branding customization. You can override properties like background, paper, and primary.main for both themes.14

#### **Deployment-Critical Configurations**

When moving an application to production, certain command-line flags and config.toml settings are crucial:

* chainlit run Flags 12:  
  * \-h or \--headless: Prevents the app from automatically opening a browser window, which is essential for server-side deployments.  
  * \--host 0.0.0.0: Binds the server to all network interfaces, which is typically required for Docker containers and cloud deployments.  
  * \--port \<number\>: Specifies the port for the server to listen on.  
  * \--root-path /\<subpath\>: Deploys the application on a specific URL subpath (e.g., https://example.com/my-chatbot).  
* Websocket Configuration 15:  
  * In config.toml, setting transports \= \["websocket"\] can improve reliability in environments with load balancers that struggle with sticky sessions.

#### **Table 2: Key config.toml Options**

| Section | Setting | Description | Possible Values/Type | Example |
| :---- | :---- | :---- | :---- | :---- |
| \[project\] | database | Enables chat persistence. | "local", "cloud", "custom" | database \= "local" |
| \[project\] | user\_env | Prompts user for environment variables. | List of strings | user\_env \= |
| \[project\] | allow\_origins | Sets CORS allowed origins for embedding. | List of strings (URLs) | allow\_origins \= \["https://my-website.com"\] |
| \[features.file\_uploads\] | allow\_file\_types | Whitelists file types for upload. | List of strings (MIME types) | allow\_file\_types \= \["application/pdf"\] |
| \[UI\] | name | Sets the name of the chatbot in the UI. | String | name \= "David Agent" |
| \[UI\] | cot | Controls Chain of Thought visibility. | "hidden", "tool\_call", "full" | cot \= "full" |
| \[UI\] | github | Adds a link to a GitHub repository. | String (URL) | github \= "https://github.com/user/repo" |
| \[UI.theme.light.primary\] | main | Sets the primary color for the light theme. | String (Hex code) | main \= "\#007AFF" |
| \[UI.theme.dark.primary\] | main | Sets the primary color for the dark theme. | String (Hex code) | main \= "\#007AFF" |

### **Section 2.6: Visualizing Agentic Workflows and Tool Integration**

The defining characteristic of an advanced agent is its ability to use tools to interact with the outside world. For such an agent to be useful and trustworthy, its actions must be transparent to the user. Chainlit's tight integration with the LangChain ecosystem provides a powerful, out-of-the-box solution for visualizing these agentic workflows.

#### **The cl.LangchainCallbackHandler: Automatic Visualization**

The single most impactful feature for building agentic UIs in Chainlit is the cl.LangchainCallbackHandler. This class acts as a bridge, or an adapter, that listens to the stream of events emitted by a LangChain agent or graph during its execution. It automatically translates these events—such as tool calls, LLM invocations, and data retrieval—into a sequence of cl.Step elements rendered live in the UI.10

This provides an incredibly rich, detailed view of the agent's reasoning process with minimal developer effort. Rather than manually creating and updating each step, the developer simply needs to add the callback handler to the agent's execution configuration. This tight integration makes LangChain, and particularly its sub-library LangGraph, the recommended framework for building agentic logic intended for a Chainlit frontend. The synergy between the two libraries is a "killer feature" that directly addresses the core challenge of agentic UI development.

#### **Practical Implementation with LangGraph**

LangGraph is a library for building stateful, multi-actor applications with LLMs, making it exceptionally well-suited for defining complex agents that can loop, branch, and use multiple tools. When combined with the LangchainCallbackHandler, Chainlit will automatically render the entire graph execution, showing which nodes are running and what data is passing between them.

The following is an annotated walkthrough of the LangGraph tool-use example from the official documentation, highlighting the key components for Chainlit integration.10

* **app.py with LangGraph and Chainlit:**  
  Python  
  import chainlit as cl  
  from typing import Literal  
  from langchain\_core.tools import tool  
  from langchain\_openai import ChatOpenAI  
  from langgraph.prebuilt import ToolNode  
  from langgraph.graph import StateGraph, START, END  
  from langgraph.graph.message import MessagesState  
  from langchain\_core.messages import HumanMessage  
  from langchain.schema.runnable.config import RunnableConfig

  \# 1\. Define a tool the agent can use.  
  @tool  
  def get\_weather(city: Literal\["nyc", "sf"\]):  
      """Use this to get weather information."""  
      if city \== "nyc":  
          return "It might be cloudy in nyc"  
      return "It's always sunny in sf"

  \# 2\. Set up the LLM and bind the tool to it.  
  tools \= \[get\_weather\]  
  model \= ChatOpenAI(model\_name="gpt-4o", temperature=0).bind\_tools(tools)

  \# 3\. Define the LangGraph graph structure.  
  \# The graph's state is a list of messages.  
  builder \= StateGraph(MessagesState)

  \# Define the nodes of the graph.  
  def call\_model(state: MessagesState):  
      """The primary agent node that calls the LLM."""  
      messages \= state\["messages"\]  
      response \= model.invoke(messages)  
      return {"messages": \[response\]}

  builder.add\_node("agent", call\_model)  
  builder.add\_node("tools", ToolNode(tools)) \# A pre-built node for executing tools.

  \# Define the edges (the control flow).  
  builder.add\_edge(START, "agent")

  def should\_continue(state: MessagesState) \-\> Literal\["tools", "final\_answer"\]:  
      """Conditional edge to decide the next step."""  
      if state\["messages"\]\[-1\].tool\_calls:  
          return "tools" \# If the LLM called a tool, go to the tools node.  
      return "final\_answer" \# Otherwise, we are done.

  builder.add\_conditional\_edges("agent", should\_continue, {"tools": "tools", "final\_answer": END})  
  builder.add\_edge("tools", "agent") \# After using a tool, go back to the agent.

  \# Compile the graph into a runnable object.  
  graph \= builder.compile()

  @cl.on\_message  
  async def on\_message(msg: cl.Message):  
      \# 4\. The critical integration step.  
      \# Instantiate the callback handler and pass it to the graph's config.  
      \# This handler will automatically create the step-by-step UI.  
      cb \= cl.LangchainCallbackHandler()

      config \= RunnableConfig(callbacks=\[cb\])

      final\_answer\_msg \= cl.Message(content="")

      \# 5\. Stream the graph's execution.  
      \# The callback handler will intercept all events and update the UI.  
      async for chunk in graph.astream(  
          {"messages": \[HumanMessage(content=msg.content)\]},  
          config=config,  
      ):  
          \# We only stream the final answer to the main message.  
          \# The intermediate steps are handled automatically by the callback.  
          if final\_answer := chunk.get("agent", {}).get("messages",)\[-1\].content:  
              if final\_answer and isinstance(final\_answer, str):  
                  await final\_answer\_msg.stream\_token(final\_answer)

      await final\_answer\_msg.send()

When a user asks, "What's the weather in nyc?", Chainlit will render a UI that shows:

1. An "agent" step, containing the LLM call.  
2. A "tools" step, showing the get\_weather tool being called with the argument city='nyc'.  
3. Another "agent" step, where the LLM processes the tool's output to formulate the final answer.  
4. The final cl.Message containing the text response.

This automatic, detailed visualization is the most effective pattern for building the transparent and sophisticated agentic UI required for the "David" project.

---

## **Conclusion: Synthesis and Architectural Recommendations for "David"**

The Chainlit framework provides a powerful and comprehensive toolkit for building the user-facing layer of modern AI applications. The analysis and reference material compiled in this report lead to a set of clear architectural recommendations for the successful development of the "David" project.

The key patterns for building a robust, transparent, and user-friendly agentic application with Chainlit are as follows:

1. **Structure Agentic Processes with @cl.step:** For any internal agent logic that is not part of a larger framework like LangChain, the primary pattern for visualizing work is to encapsulate processes into async functions decorated with @cl.step. Awaiting these functions from the main message handler provides a simple yet effective way to control UI rendering order and communicate the agent's progress to the user.  
2. **Manage State with cl.user\_session:** The cl.user\_session key-value store is the standard mechanism for maintaining state across conversational turns. It should be used to store conversation history, API clients, and any other user-specific data, typically initialized in @cl.on\_chat\_start and accessed in subsequent event handlers.  
3. **Decouple Configuration with config.toml:** All operational concerns—such as UI branding, feature flags, data persistence settings, and deployment parameters—should be managed within the .chainlit/config.toml file. This decouples the core application logic from its environment, improving maintainability and simplifying deployment.  
4. **Embrace LangChain for Automatic Visualization:** For the core agentic logic, the most powerful and efficient path is to build the agent using the LangChain or LangGraph frameworks. The seamless integration provided by the cl.LangchainCallbackHandler offers rich, automatic, and live-updating visualization of the agent's reasoning and tool use with minimal code. This approach is strongly recommended as it directly fulfills the need for a transparent and debuggable agentic UI, which is a central goal of the "David" project.

By combining these patterns, developers can leverage Chainlit to its full potential, creating sophisticated conversational AI applications that are not only powerful in their logic but also clear, interactive, and trustworthy in their presentation.

#### **Works cited**

1. Chainlit: Overview, accessed August 4, 2025, [https://docs.chainlit.io/](https://docs.chainlit.io/)  
2. Chainlit: Build LLM Apps in MINUTES\! \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=rcXPq3UcxIY](https://www.youtube.com/watch?v=rcXPq3UcxIY)  
3. Chainlit \- Build AI applications, accessed August 4, 2025, [https://chainlit.io/](https://chainlit.io/)  
4. Chainlit: A Guide With Practical Examples | DataCamp, accessed August 4, 2025, [https://www.datacamp.com/tutorial/chainlit](https://www.datacamp.com/tutorial/chainlit)  
5. Chainlit/chainlit: Build Conversational AI in minutes ⚡️ \- GitHub, accessed August 4, 2025, [https://github.com/Chainlit/chainlit](https://github.com/Chainlit/chainlit)  
6. Element \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/concepts/element](https://docs.chainlit.io/concepts/element)  
7. Custom \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/api-reference/elements](https://docs.chainlit.io/api-reference/elements)  
8. Chainlit-Get Started\!\! \- Medium, accessed August 4, 2025, [https://medium.com/@danushidk507/chainlit-get-started-cb25205322d8](https://medium.com/@danushidk507/chainlit-get-started-cb25205322d8)  
9. docs.chainlit.io, accessed August 4, 2025, [https://docs.chainlit.io/api-reference/user-session](https://docs.chainlit.io/api-reference/user-session)  
10. LangChain/LangGraph \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/integrations/langchain](https://docs.chainlit.io/integrations/langchain)  
11. Async / Sync \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/guides/sync-async](https://docs.chainlit.io/guides/sync-async)  
12. Command Line Options \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/backend/command-line](https://docs.chainlit.io/backend/command-line)  
13. Overview \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/backend/config/overview](https://docs.chainlit.io/backend/config/overview)  
14. .chainlit/config.toml · XThomasBU/chainlit-example at ..., accessed August 4, 2025, [https://huggingface.co/spaces/XThomasBU/chainlit-example/blob/e3d711be161f1b78d5132370e071b903dd566151/.chainlit/config.toml](https://huggingface.co/spaces/XThomasBU/chainlit-example/blob/e3d711be161f1b78d5132370e071b903dd566151/.chainlit/config.toml)  
15. Overview \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/deploy/overview](https://docs.chainlit.io/deploy/overview)  
16. UI \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/backend/config/ui](https://docs.chainlit.io/backend/config/ui)