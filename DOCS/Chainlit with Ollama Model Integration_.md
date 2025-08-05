

# **Building Conversational AI with Chainlit and Ollama: A Comprehensive Developer Guide**

## **Executive Summary**

This guide provides an exhaustive, expert-level report for developers on building sophisticated, locally-run conversational AI applications. It details the complete workflow for integrating the Chainlit frontend framework with custom Large Language Models (LLMs) served by Ollama. The report covers the entire development lifecycle, from preparing the development environment and installing the toolchain to advanced model customization, robust application integration, and production-level troubleshooting. By treating LLM behavior as configuration-as-code and addressing common architectural and environmental challenges, this manual serves as a definitive resource for creating high-performance, private, and customizable LLM applications. It empowers developers to move beyond simple API calls to external services and build powerful AI systems that run entirely on their own hardware.

## **Part 1: Foundational Setup \- Installing the Toolchain**

This section focuses on the critical first step of preparing a developer's machine. It provides detailed, platform-specific installation instructions for the necessary software, emphasizing best practices from the outset. A correct and clean setup is paramount to avoiding common frustrations, particularly those related to software dependencies.

### **1.1 Preparing Your Development Environment: Best Practices**

Before installing any project-specific software, establishing a clean and isolated development environment is essential. This practice prevents conflicts between project dependencies and system-wide packages, a frequent source of errors in the Python ecosystem.

Python Version Requirements  
The Chainlit framework requires a modern version of Python to function correctly. The development environment must have Python 3.8 or a newer version installed.1 Developers should verify their Python version using the command  
python \--version or python3 \--version in their terminal.

The Critical Role of Virtual Environments  
The single most effective practice to prevent dependency issues is the use of a virtual environment. Libraries within the AI/ML ecosystem, particularly those related to LangChain, are known to have complex and sometimes conflicting dependency requirements.3 For instance,  
chainlit and other libraries like langgraph-api may require different, incompatible versions of a shared dependency such as uvicorn.5 A virtual environment creates an isolated space for a project's packages, ensuring that the dependencies for one project do not interfere with another.

To create and activate a virtual environment using Python's built-in venv module, execute the following commands in the project directory:

* **Create the environment:**  
  Bash  
  python3 \-m venv.venv

* **Activate the environment:**  
  * On macOS and Linux:  
    Bash  
    source.venv/bin/activate

  * On Windows:

.venv\\Scripts\\activate\`\`\`

Once activated, the terminal prompt will typically change to indicate that the virtual environment is active. All subsequent pip installations will be confined to this environment.6

### **1.2 Installing and Configuring Ollama: A Multi-Platform Guide**

Ollama is a powerful framework that dramatically simplifies the process of running open-source LLMs on local hardware.8 It manages model downloads, configuration, and serving through a simple command-line interface.

Hardware and System Requirements  
Running LLMs locally is resource-intensive. Before proceeding, it is important to ensure the host machine meets the necessary hardware specifications. The amount of RAM is the primary constraint. As a general guideline, a machine should have at least 8 GB of RAM to run 7-billion-parameter models, 16 GB for 13B models, and 32 GB for 33B models.8 While a dedicated GPU is optional, it is highly recommended for acceptable performance.8  
Platform-Specific Installation Instructions  
Ollama provides tailored installation methods for all major operating systems.

* **macOS:**  
  * Requires macOS 12 Monterey or later.11  
  * The recommended method is to download the official application from the Ollama website.11  
  * Alternatively, it can be installed via a curl command in the terminal or using the Homebrew package manager.8  
    Bash  
    \# Using curl  
    curl \-fsSL https://ollama.com/install.sh | sh

    \# Using Homebrew  
    brew install ollama

* **Windows:**  
  * Requires Windows 10 or a later version.13  
  * Installation is done by downloading and running the official installer from the Ollama website.13  
  * For developers who prefer a Linux environment, Ollama can be installed within the Windows Subsystem for Linux (WSL2) by following the Linux installation instructions inside the WSL2 terminal.8  
* **Linux:**  
  * The most straightforward method is to use the provided curl script, which automates the installation process.10  
    Bash  
    curl \-fsSL https://ollama.com/install.sh | sh

* **Docker (Recommended for Reproducibility):**  
  * Using Docker is the preferred method for ensuring a consistent and isolated environment, which is ideal for team collaboration and deployment. It avoids the "it works on my machine" problem by encapsulating the application and its dependencies.  
  * To use Docker, first pull the official Ollama image from Docker Hub.10  
    Bash  
    docker pull ollama/ollama

  * Then, run the image in a container. The following command includes the essential flags for GPU acceleration and data persistence.8  
    Bash  
    docker run \-d \--gpus=all \-v ollama:/root/.ollama \-p 11434:11434 \--name ollama ollama/ollama

    * \--gpus=all: Enables the container to access all available GPUs on the host machine. This is critical for performance.  
    * \-v ollama:/root/.ollama: Mounts a Docker volume to persist the downloaded models. Without this, models would be lost every time the container is restarted.  
    * \-p 11434:11434: Maps the Ollama server port from the container to the host machine.

The choice between a native installation and Docker is a strategic one. Native installation may offer slightly better performance due to direct hardware access but can be more complex to manage. Docker provides superior isolation, consistency, and portability, making it the more robust choice for most development and production workflows.

### **1.3 Verifying the Ollama Installation and Managing Models**

After installation, it is important to verify that Ollama is running correctly and to learn the basic commands for model management.

* **Verification:** Open a new terminal window and run the ollama command. This should display a list of available commands, confirming that the installation was successful.14  
* **Running a Model:** To run a model for the first time, use the ollama run command followed by the model name. For example, to run Llama 3.1:  
  Bash  
  ollama run llama3.1

  If the model is not already present on the local machine, Ollama will automatically download it from its library before running it.10  
* **Interacting via CLI:** Once a model is running, the terminal becomes a chat interface. Messages can be sent directly to the model. To see a list of in-chat commands, type /?. To exit the chat, type /bye.16  
* **Model Management:** The two most essential commands for managing the local model library are:  
  * ollama list: Shows all models that have been downloaded to the machine.15  
  * ollama rm \<model\_name\>: Deletes a specified model to free up disk space.17

### **1.4 Installing Chainlit and Key Dependencies**

With Ollama set up and verified, the next step is to install the Chainlit framework.

* **Core Chainlit Installation:** Ensure the virtual environment created in section 1.1 is active, then install Chainlit using pip.18  
  Bash  
  pip install chainlit

* **Integration Libraries:** To facilitate the connection between Chainlit and Ollama, it is highly recommended to install the langchain-community package. This library provides a convenient abstraction layer for interacting with various LLMs, including those served by Ollama.1  
  Bash  
  pip install langchain langchain-community

* **Verifying Chainlit Installation:** To confirm that Chainlit is installed correctly, run its built-in "hello" application.19  
  Bash  
  chainlit hello

  This command should launch a new browser tab with a simple chat interface, confirming that the UI components are working.

## **Part 2: Mastering Local Model Serving with Ollama**

This section moves beyond basic installation to the practical application and customization of Ollama. The central focus is the Modelfile, a powerful tool that allows developers to define custom model behaviors and parameters without the need for complex model retraining or fine-tuning.

### **2.1 The Ollama Command Line Interface (CLI): A Comprehensive Reference**

The Ollama CLI is the primary tool for interacting with the Ollama server. A firm grasp of its commands is essential for efficient development. The following table summarizes the most frequently used commands.10

| Command | Description | Example Usage |
| :---- | :---- | :---- |
| ollama run \<model\> | Runs a model, downloading it first if necessary. Opens an interactive chat session. | ollama run llama3.1 |
| ollama create \<name\> \-f \<Modelfile\> | Creates a new custom model from a Modelfile. | ollama create my-bot \-f./Modelfile |
| ollama pull \<model\> | Downloads a model from the Ollama library without running it. | ollama pull mistral |
| ollama list | Lists all models that have been downloaded to the local machine. | ollama list |
| ollama show \<model\> | Shows detailed information about a model, including its Modelfile content. | ollama show llama3.1 \--modelfile |
| ollama cp \<source\> \<dest\> | Creates a copy of an existing model with a new name. | ollama cp llama3.1 my-llama-copy |
| ollama rm \<model\> | Removes a model and its data from the local machine. | ollama rm mistral |
| ollama serve | Starts the Ollama server manually. (Usually runs as a background service). | ollama serve |

### **2.2 Crafting Custom Model Personas with Modelfile**

The Modelfile is a revolutionary concept that treats an LLM's personality and operational parameters as configuration-as-code. It is a simple, declarative text file that acts as a blueprint for creating custom model variations.20 This approach allows a model's specific behavior—its persona, its level of creativity, its response constraints—to be version-controlled in Git, shared among team members, and deployed repeatably, just like any other piece of application code. This elevates the model from an opaque, static entity to a configurable and manageable component of the software stack.

The workflow for creating a custom model is straightforward 10:

1. **Select and Pull a Base Model:** Choose a model from the Ollama library to serve as the foundation. For example, ollama pull llama3.1.10  
2. **Create a Modelfile:** In the project directory, create a new text file named Modelfile (or any other name).  
3. **Define the Customization:** Populate the Modelfile with instructions that define the new model's behavior.  
4. **Create the Custom Model:** Use the ollama create command, providing a name for the new model and the path to the Modelfile. The \-f flag specifies the file path.10  
   Bash  
   ollama create my-custom-model \-f Modelfile

5. **Run and Test:** Interact with the newly created model using ollama run to verify that it behaves as expected.20

Example: The "Mario" Persona  
To illustrate this process, consider creating a model that always responds in the character of Mario from the Super Mario Bros. franchise. This demonstrates the power of the SYSTEM instruction to set a persistent persona.10  
Create a Modelfile with the following content:

Code snippet

FROM llama3.1

\# Set a high temperature for more creative, in-character responses  
PARAMETER temperature 1

\# Define the core persona with a system prompt  
SYSTEM """  
You are Mario from Super Mario Bros. Answer as Mario, the assistant, only. Always stay in character.  
"""

Next, create the model from this file:

Bash

ollama create mario \-f./Modelfile

Finally, run and interact with the new mario model:

Bash

ollama run mario  
\>\>\> hi  
Hello\! It's-a me, Mario\! What can I do for you today?

### **2.3 A Deep Dive into Modelfile Instructions and Parameters**

The Modelfile syntax is simple yet powerful, consisting of a series of instructions and parameters that define the model's build and runtime configuration.22

**Core Instructions**

* FROM: This is the only mandatory instruction. It specifies the base model upon which the custom model is built. The value can be a model name from the Ollama library (e.g., llama3.1) or a path to a local GGUF model file (e.g., ./vicuna-7b.Q4\_K\_M.gguf). This dual capability shows that Ollama is an open platform, allowing developers to easily customize standard models or import entirely new ones from external sources like Hugging Face.10  
* SYSTEM: Sets a system-level prompt that guides the model's overall behavior and persona. This instruction is injected into the model's context for every interaction.10  
* TEMPLATE: Provides fine-grained control over the full prompt structure sent to the model. It uses Go template syntax and allows for the precise placement of variables like {{.System }}, {{.Prompt }}, and {{.Response }}. The exact syntax is often specific to the base model being used.22  
* PARAMETER: Sets a default runtime parameter for the model. This is the primary instruction for tuning the model's generative output.21  
* ADAPTER: An advanced instruction used to apply a LoRA (Low-Rank Adaptation) adapter to the base model, which is a method for efficient fine-tuning.22

Key Modelfile Parameters  
Tuning a model's parameters is the key to shaping its output to fit a specific application's needs. The following table details the most important parameters available through the PARAMETER instruction, providing a quick-reference guide for developers.22

| Parameter | Description | Data Type | Default | Example Usage |
| :---- | :---- | :---- | :---- | :---- |
| temperature | Controls the randomness of the output. Higher values (e.g., 1.0) lead to more creative and diverse responses. Lower values (e.g., 0.2) make the output more deterministic and focused. | float | 0.8 | PARAMETER temperature 0.7 |
| num\_ctx | Sets the context window size in tokens. This determines how much of the previous conversation the model can "remember" when generating the next response. | int | 2048 | PARAMETER num\_ctx 4096 |
| top\_p | An alternative to temperature. It uses nucleus sampling, considering only the most probable tokens that make up a cumulative probability of top\_p. A lower value (e.g., 0.5) generates more conservative text. | float | 0.9 | PARAMETER top\_p 0.9 |
| repeat\_penalty | Sets the penalty for repeating tokens. A higher value (e.g., 1.5) strongly discourages repetition, while a lower value is more lenient. | float | 1.1 | PARAMETER repeat\_penalty 1.2 |
| stop | Defines one or more sequences of text that, when generated, will cause the model to stop its output. This is useful for preventing run-on sentences or forcing a specific format. Can be specified multiple times. | string | (none) | PARAMETER stop "User:" |
| seed | Sets the random seed for generation. Using the same seed with the same prompt will produce the same output, which is useful for reproducibility and testing. | int | (random) | PARAMETER seed 42 |

## **Part 3: Building Interactive UIs with Chainlit**

This section introduces the fundamental concepts of Chainlit, the open-source Python framework used to build the user interface for the conversational AI. It focuses on the core architectural patterns and UI components needed to create an interactive chat application.

### **3.1 The Anatomy of a Chainlit Application: Lifecycle and Asynchronous Decorators**

Chainlit is designed to abstract away the complexities of frontend web development, allowing developers to build rich, chat-based UIs using only Python.1 Its architecture is event-driven and asynchronous, built on Python's

asyncio library. Understanding this architecture is key to avoiding common pitfalls.

The structure of a Chainlit application does not follow a linear, top-to-bottom execution path. Instead, it is defined by a series of functions marked with special decorators. These functions, or "hooks," are triggered by events in the chat lifecycle, such as a user starting a conversation or sending a message.1

The primary lifecycle hooks are:

* @cl.on\_chat\_start: This decorator marks a function that will execute once at the very beginning of a new chat session. It is the ideal place for sending a welcome message, initializing session state, or displaying initial action buttons.1  
* @cl.on\_message: This is the most important decorator. The function it decorates is the main workhorse of the application, as it is called every time the user sends a message. This is where the application logic for processing user input and generating a response resides.1

Because Chainlit is asynchronous, all decorated functions must be defined as async def. A common mistake for developers new to this paradigm is to place a long-running, synchronous operation (like a slow, blocking API call) directly within one of these functions. This will block the server's entire event loop, making the UI unresponsive and eventually causing a "Could not reach the server" error.25 This issue and its solution will be covered in detail in the troubleshooting section.

A basic "echo bot" demonstrates these core concepts:

Python

import chainlit as cl

@cl.on\_chat\_start  
async def start():  
    await cl.Message(  
        content="Hello\! I am an echo bot. Whatever you say, I will repeat."  
    ).send()

@cl.on\_message  
async def main(message: cl.Message):  
    \# This is the main logic of the bot.  
    \# It simply sends back the content of the user's message.  
    await cl.Message(  
        content=f"You said: {message.content}"  
    ).send()

### **3.2 Core UI Components: Messages, Actions, and User Input**

Chainlit provides simple yet powerful classes for interacting with the user.

* **Sending Messages:** The cl.Message class is used to send content back to the user interface. The content is sent by calling the asynchronous .send() method.19  
* **Interactive Buttons (Actions):** Chainlit allows for the creation of clickable buttons within a message. These are called Actions and are created using the cl.Action class. A list of actions can be attached to any message via its actions parameter.1  
  Python  
  import chainlit as cl

  @cl.on\_chat\_start  
  async def start():  
      actions \= \[  
          cl.Action(name="my\_action", payload={"value": "42"}, label="Click Me\!")  
      \]  
      await cl.Message(  
          content="Please click the button.",  
          actions=actions  
      ).send()

* **Handling Button Clicks:** To make a button functional, a corresponding callback function must be defined using the @cl.action\_callback() decorator. The string passed to the decorator must match the name of the cl.Action object.1  
  Python  
  @cl.action\_callback("my\_action")  
  async def on\_action(action: cl.Action):  
      \# The action object contains the payload sent from the UI  
      await cl.Message(  
          content=f"You clicked the button\! The payload value is: {action.payload\['value'\]}"  
      ).send()

### **3.3 Running and Developing a Chainlit App**

To run a Chainlit application, navigate to the directory containing the Python script (app.py) in a terminal and use the chainlit run command.18

Bash

chainlit run app.py

During development, it is highly recommended to include the \-w (or \--watch) flag. This enables auto-reloading, which means the server will automatically restart whenever a change is saved to the source file. This creates a much faster and more efficient development feedback loop.19

Bash

chainlit run app.py \-w

This command will start the web server and open the application in a new browser tab, typically at http://localhost:8000.

## **Part 4: The Core Integration \- Connecting Chainlit to a Custom Ollama Model**

This is the central part of the guide, where the Chainlit frontend and the Ollama backend are connected to create a fully functional conversational AI. This section provides complete, runnable code examples demonstrating how to achieve this integration.

### **4.1 Architecture of the Integration: API-Driven Communication**

The integration architecture is straightforward. The Chainlit application, running as a Python backend server, communicates with the Ollama server, which runs as a separate process. When a user sends a message in the Chainlit UI, the @cl.on\_message handler in the Python script is triggered. This handler then constructs and sends an HTTP API request to the Ollama server, which is listening by default on http://localhost:11434.2 The Ollama server processes the prompt using the specified model (including any custom models created with a

Modelfile) and streams the response back to the Chainlit backend, which in turn streams it to the user's browser.

There are two primary methods for implementing this communication, each with its own trade-offs.

### **4.2 Method 1: Direct API Integration (Advanced)**

This method involves using a standard Python HTTP library like requests or httpx to interact directly with the Ollama API endpoints (/api/generate or /api/chat). This approach offers maximum control and transparency, as the developer is explicitly handling the API contract. It also avoids adding the langchain dependency, which can be beneficial for creating lightweight, production-focused applications.

To implement streaming with this method, the request payload sent to Ollama must include "stream": true. The server will then respond with a stream of JSON objects, one per line. The Python code must iterate over these lines, decode each JSON object, and extract the content chunk.2 This provides the token-by-token "live typing" effect in the UI.

### **4.3 Method 2: Simplified Integration with langchain-community (Recommended)**

This method utilizes the Ollama class from the langchain-community library, which provides a high-level abstraction over the direct API calls. This approach results in significantly cleaner and more concise code, making it the recommended path for most developers, especially during prototyping and initial development.1 It handles the complexities of API interaction and response streaming internally.

The process involves:

1. Importing the Ollama class: from langchain\_community.llms import Ollama.1  
2. Instantiating the model, pointing it to the custom model created in Part 2: llm \= Ollama(model="my-custom-model").  
3. Invoking the model within the @cl.on\_message handler using either llm.invoke() for a complete response or llm.stream() to get an iterable of response chunks.15

The choice between these two methods represents a classic engineering trade-off. The direct API method offers control and minimal dependencies at the cost of more boilerplate code. The LangChain method offers convenience and rapid development at the cost of an added abstraction layer. A good development strategy is to start with the LangChain method for speed and then, if necessary, refactor to direct API calls for performance tuning or to reduce dependencies in a final production build.

### **4.4 Implementing a Streaming Chatbot: Step-by-Step Code Walkthrough**

The following is a complete, well-commented app.py file that implements a streaming chatbot using the recommended langchain-community approach. It connects to a custom Ollama model and properly handles conversation history.

Python

import chainlit as cl  
from langchain\_community.llms import Ollama

@cl.on\_chat\_start  
async def on\_chat\_start():  
    \# Instantiate the Ollama LLM with the desired model  
    \# This model can be a custom model created with a Modelfile  
    model \= Ollama(  
        model="llama3.1", \# Replace with your custom model name, e.g., "mario"  
        base\_url="http://localhost:11434",  
        temperature=0.7  
    )

    \# Store the model instance in the user session for later use  
    cl.user\_session.set("model", model)

    await cl.Message(  
        content="The model is ready. How can I help you?"  
    ).send()

@cl.on\_message  
async def on\_message(message: cl.Message):  
    \# Retrieve the model from the user session  
    model \= cl.user\_session.get("model")

    \# Create an empty message to stream the response into  
    msg \= cl.Message(content="")  
    await msg.send()

    \# Stream the response from the model  
    \# The astream method is the async version of stream  
    response\_stream \= ""  
    async for chunk in model.astream(message.content):  
        await msg.stream\_token(chunk)  
        response\_stream \+= chunk  
      
    \# Update the message with the final, complete response  
    await msg.update()

This code demonstrates the canonical pattern for streaming in Chainlit. An empty cl.Message is created first, and then its content is progressively built by streaming tokens into it with msg.stream\_token(chunk). This is the mechanism that delivers a responsive, real-time user experience.15

### **4.5 Managing Conversation History and Context**

LLMs are stateless. To have a coherent, multi-turn conversation, the application must send the relevant parts of the conversation history back to the model with every new user message. Chainlit's user session is the perfect place to store this history.

The cl.user\_session is a dictionary-like object that persists for the duration of a single user's chat session. It can be used to store and retrieve any data needed between message turns.15

The following example extends the previous one to include conversation history management:

Python

import chainlit as cl  
from langchain\_community.llms import Ollama  
from langchain\_core.prompts import ChatPromptTemplate  
from langchain\_core.messages import HumanMessage, AIMessage

@cl.on\_chat\_start  
async def on\_chat\_start():  
    model \= Ollama(model="llama3.1", temperature=0.7)  
      
    \# Initialize an empty message history  
    cl.user\_session.set("message\_history",)  
    cl.user\_session.set("model", model)  
      
    await cl.Message(content="Model is ready. Let's chat\!").send()

@cl.on\_message  
async def on\_message(message: cl.Message):  
    model \= cl.user\_session.get("model")  
    message\_history \= cl.user\_session.get("message\_history")

    \# Add the new user message to the history  
    message\_history.append(HumanMessage(content=message.content))

    msg \= cl.Message(content="")  
    await msg.send()

    \# Create a prompt template that includes history  
    prompt \= ChatPromptTemplate.from\_messages(message\_history)  
      
    \# Create the chain  
    chain \= prompt | model

    response\_stream \= ""  
    async for chunk in chain.astream({}): \# Pass an empty dict for astream with prompt templates  
        await msg.stream\_token(chunk)  
        response\_stream \+= chunk

    \# Add the full AI response to the history  
    message\_history.append(AIMessage(content=response\_stream))  
    await msg.update()

This enhanced code ensures that with each turn, the model receives the entire conversation history, allowing it to generate contextually appropriate responses.

## **Part 5: Advanced Development and Deployment**

With the core chat functionality in place, this section explores advanced Chainlit features that enable developers to build more polished, professional, and feature-rich applications. It also covers key considerations for deploying the application to a production environment.

### **5.1 Enhancing the User Experience: UI Customization**

Chainlit's design philosophy promotes a clean separation of concerns: application logic resides in Python code, while application configuration and presentation details are managed in a dedicated configuration file. This separation is a best practice in modern software development, as it allows for changes to the UI or feature flags without modifying the core logic.

The config.toml File  
The central hub for this configuration is the .chainlit/config.toml file, located in the root of the project directory. This file allows for extensive customization of the application's appearance and behavior.1  
Theming and Styling  
The \[UI\] section of config.toml controls the visual aspects of the application. Developers can set the application's name, add a description for HTML meta tags, and customize the theme, including colors and layout.31 For more advanced styling, a path to a custom CSS file can be specified, giving full control over the application's look and feel.31  
Example config.toml for UI customization:

Ini, TOML

\[UI\]  
\# Name of the app displayed in the UI  
name \= "My Custom AI Assistant"

\# Link to a GitHub repository to display a button in the header  
github \= "https://github.com/my-user/my-repo"

\# Path to a custom CSS file for advanced styling  
\# custom\_css \= "/public/style.css"

\[UI.theme\]  
\# Override the default light theme colors  
\[UI.theme.light\]  
background \= "\#F0F2F5"  
paper \= "\#FFFFFF"  
\[UI.theme.light.primary\]  
main \= "\#1976D2"

\# Override the default dark theme colors  
\[UI.theme.dark\]  
background \= "\#121212"  
paper \= "\#1E1E1E"  
\[UI.theme.dark.primary\]  
main \= "\#64B5F6"

Custom Avatars  
To further personalize the chat experience, custom avatars can be assigned to message authors. To set a custom avatar for the assistant, place an image file (e.g., .png, .jpg) in a /public/avatars directory within the project root. The filename must match the author name of the message, with spaces replaced by underscores. For example, if the assistant's author name is "AI Assistant", the avatar file should be named ai\_assistant.png.32

### **5.2 Expanding Functionality: Multi-Modality and Data Persistence**

Chainlit supports features that go beyond simple text-based chat, enabling more complex and powerful applications.

File Uploads  
The ability for users to upload files is essential for applications that perform Retrieval-Augmented Generation (RAG), where the LLM answers questions based on the content of provided documents. This feature can be enabled in config.toml. Once enabled, users can upload files via drag-and-drop or an attach button. The uploaded files are accessible within the @cl.on\_message handler via the msg.elements list, where they can be processed.1  
Data Persistence  
For applications where users may disconnect and return later, persisting chat history is crucial. Chainlit offers a simple built-in persistence mechanism that can be enabled in config.toml. This activates the @cl.on\_chat\_resume hook, which allows the application to load the previous state when a user reconnects.1 For more robust, production-grade persistence, it is recommended to integrate a dedicated database like PostgreSQL. This provides greater control over data storage, querying, and management.6

### **5.3 Deployment Considerations**

Moving a Chainlit application from local development to a production server involves several important considerations.

* **Headless Mode:** When deploying to a server, the chainlit run command should always include the \-h (or \--headless) flag. This prevents the server from attempting to open a graphical browser window, which would fail in a headless server environment and could break the deployment.34  
  Bash  
  chainlit run app.py \-h 0.0.0.0

  The 0.0.0.0 host tells the server to listen on all available network interfaces, making it accessible from outside the server itself.  
* **Websockets and CORS:** Chainlit's real-time communication relies on websockets. The deployment environment, especially if it is behind a load balancer or reverse proxy, must be configured to support websocket connections. For auto-scaling environments, this often requires enabling "sticky sessions" (or session affinity) to ensure a client is consistently routed to the same server instance. Additionally, if the Chainlit app is embedded within another website (i.e., the UI and backend are on different origins), Cross-Origin Resource Sharing (CORS) errors will occur. This is resolved by specifying the allowed origins in the allow\_origins field of config.toml.34  
* **Deployment Platforms:** A Chainlit application can be deployed as a standalone web app on any service that supports Python. Furthermore, it is designed to be multi-platform, with integrations available to deploy the same application logic as a bot on platforms like Slack, Discord, and Microsoft Teams.18

## **Part 6: Troubleshooting and Performance Optimization**

Real-world development inevitably involves debugging errors and optimizing performance. This section addresses the most common issues encountered when working with the Chainlit and Ollama stack, providing clear solutions and strategies for performance tuning. The errors in this stack are often not simple logic bugs but rather environmental or architectural mismatches, requiring a systems-level approach to debugging.

### **6.1 Common Errors and Solutions**

The following table consolidates known issues from community forums and bug reports, providing developers with a first line of defense against common problems. It aims to diagnose the root cause behind cryptic error messages and offer verified solutions.

| Symptom / Error Message | Likely Cause | Recommended Solution(s) |
| :---- | :---- | :---- |
| **Chainlit UI shows "Could not reach the server."** | The server's asynchronous event loop is blocked by a long-running, synchronous task (e.g., a slow API call or heavy computation) in an async function. The client times out, assuming the server is dead. | Wrap the blocking synchronous call in cl.make\_async() to run it in a separate thread, or switch to an asynchronous version of the library if available (e.g., use httpx.AsyncClient instead of requests). 25 |
| **pip install fails with dependency conflicts.** | Two or more packages in the environment require incompatible versions of the same sub-dependency (e.g., chainlit requires uvicorn\<0.26.0 while langgraph-api requires uvicorn\>=0.26.0). | **1\.** Always work in a clean virtual environment (venv). **2\.** Use pip check or pipdeptree to identify the exact conflict. **3\.** Manually specify a compatible version of the conflicting package in requirements.txt or downgrade the package that has the more flexible requirement. 3 |
| **Ollama runs on CPU instead of GPU / GPU not detected.** | This is an environment configuration issue. Causes include incorrect NVIDIA/AMD drivers, misconfigured Docker runtime, or insufficient permissions for the Ollama process to access GPU devices. | **1\.** Verify drivers are installed and working with nvidia-smi (for NVIDIA) or rocminfo (for AMD). **2\.** If using Docker, ensure the docker run command includes the \--gpus all flag. **3\. (Linux)** Check that the user running Ollama is in the docker and video/render groups. **4\.** Check the Ollama server logs for specific GPU-related error codes. 36 |
| **chainlit run app.py command does nothing (no output, no error).** | This can be a subtle environment path issue, a silent crash, or a zombie process from a previous run. | **1\.** Ensure the correct virtual environment is activated and that the chainlit executable is in the system's PATH. **2\.** Check the system's process list for any lingering Python or Chainlit processes and terminate them. **3\.** Reinstall Chainlit in a fresh virtual environment. 38 |
| **Model response is slow on the first request, then fast on subsequent ones.** | Ollama unloads the model from GPU VRAM after a period of inactivity to free up resources. The first request after this period incurs the time penalty of reloading the model into memory. | In the Modelfile or via the API, set a keep\_alive parameter for the model. This tells Ollama to keep the model loaded in memory indefinitely or for a specified duration, eliminating the cold start penalty at the cost of persistently using VRAM. 39 |
| **Concurrent requests to Ollama freeze or fail.** | The default Ollama server processes requests serially. When multiple requests arrive simultaneously, a queue forms. If the queue becomes too long, incoming requests can time out and fail before they are ever processed. | This is a limitation of the basic serving architecture. For high-concurrency applications, consider more advanced serving solutions like vLLM or deploying multiple Ollama instances behind a load balancer. For development, simply be aware that concurrent requests will be slower. 39 |

### **6.2 Ollama Performance Tuning**

Beyond fixing errors, performance can be actively tuned to balance response speed and quality.

Model Quantization  
Ollama models are often available in several versions, or "tags." By default, running ollama run llama3.1 might pull a "quantized" version of the model. Quantization is a process that reduces the precision of the model's weights (e.g., from 16-bit floating-point numbers to 4-bit integers) to decrease its size and make it run faster on less powerful hardware.40  
This creates a direct trade-off:

* **Lower Quantization (e.g., Q4\_K\_M):** Smaller file size, lower RAM usage, faster inference. However, may result in a slight degradation of response quality and nuance.  
* **Higher Precision (e.g., FP16):** Larger file size, higher RAM usage, slower inference. Provides the highest possible response quality, as it is closest to the original, uncompressed model.

Developers should check the "tags" page for their chosen model on the Ollama library website. If their hardware supports it (i.e., they have sufficient VRAM), they should explicitly pull a higher-precision version to maximize the quality of their application's output.40 For example:

Bash

ollama pull llama3.1:8b-instruct-fp16

Confirming GPU Utilization  
To ensure the application is getting the full performance benefit of the available hardware, it is crucial to confirm that Ollama is using the GPU. The primary method for this is to check the Ollama server logs. Upon startup, the logs will indicate which libraries were loaded and whether a GPU was successfully detected and initialized.37 During model inference, tools like  
nvidia-smi or radeontop can be used to monitor GPU VRAM usage and utilization in real-time. If the GPU is not being used, refer to the troubleshooting table above.

## **Conclusion and Future Directions**

This guide has provided a comprehensive walkthrough of the entire process of building a custom conversational AI application using Chainlit and Ollama. It has covered the foundational setup of the development environment, the installation of the toolchain across multiple platforms, and the crucial best practice of using virtual environments to prevent dependency conflicts. The report detailed the powerful capabilities of Ollama's Modelfile for creating custom model personas through declarative configuration, treating AI behavior as version-controllable code.

The core principles of Chainlit development were explored, emphasizing its asynchronous, event-driven architecture and the use of decorators to structure application logic. A complete, streaming chatbot application was built step-by-step, demonstrating the integration between the Chainlit frontend and the Ollama backend, including the management of conversation history to maintain context. Finally, the guide addressed advanced topics in UI customization, expanded functionality, deployment strategies, and a detailed troubleshooting section to resolve common real-world errors.

By mastering the concepts and techniques presented, developers are now equipped to build, customize, and deploy powerful, private AI applications that run entirely on their own hardware. This local-first approach provides unparalleled control, privacy, and flexibility compared to relying on third-party APIs.

The journey does not end here. The skills acquired form a strong foundation for exploring more advanced architectures and applications. Future directions for developers include:

* **Building RAG Pipelines:** Leveraging Chainlit's file upload capabilities to build sophisticated Retrieval-Augmented Generation systems that allow users to chat with their own documents.9  
* **Exploring Agentic Frameworks:** Integrating the local Ollama models with agentic frameworks like LangGraph to create autonomous agents that can reason, plan, and use tools to accomplish complex tasks.5  
* **Advanced Fine-Tuning:** Moving beyond Modelfile customization to perform efficient fine-tuning of models using LoRA adapters, further tailoring them to specific domains or tasks.22

The landscape of local, open-source AI is evolving at an incredible pace. By continuing to build and experiment with powerful tools like Chainlit and Ollama, developers can remain at the forefront of this exciting field.

#### **Works cited**

1. Chainlit: A Guide With Practical Examples \- DataCamp, accessed August 4, 2025, [https://www.datacamp.com/tutorial/chainlit](https://www.datacamp.com/tutorial/chainlit)  
2. Build a Custom LLM-Powered Chat App Using Chainlit | Codecademy, accessed August 4, 2025, [https://www.codecademy.com/article/llm-powered-chatapp-using-chainlit](https://www.codecademy.com/article/llm-powered-chatapp-using-chainlit)  
3. LangChain LangChainDependencyConflictError: Dependency conflict \- Doctor Droid, accessed August 4, 2025, [https://drdroid.io/stack-diagnosis/langchain-langchaindependencyconflicterror--dependency-conflict](https://drdroid.io/stack-diagnosis/langchain-langchaindependencyconflicterror--dependency-conflict)  
4. \[RANT\] I simply cannot work with LangChain without being stuck on ..., accessed August 4, 2025, [https://www.reddit.com/r/LangChain/comments/1i4zx6y/rant\_i\_simply\_cannot\_work\_with\_langchain\_without/](https://www.reddit.com/r/LangChain/comments/1i4zx6y/rant_i_simply_cannot_work_with_langchain_without/)  
5. Dependency issue with langgraph \#1737 \- GitHub, accessed August 4, 2025, [https://github.com/Chainlit/chainlit/issues/1737](https://github.com/Chainlit/chainlit/issues/1737)  
6. sercancelenk/ai-chatbot-chainlit-ollama: AI Chatbot with ... \- GitHub, accessed August 4, 2025, [https://github.com/sercancelenk/ai-chatbot-chainlit-ollama](https://github.com/sercancelenk/ai-chatbot-chainlit-ollama)  
7. sudarshan-koirala/langchain-ollama-chainlit \- GitHub, accessed August 4, 2025, [https://github.com/sudarshan-koirala/langchain-ollama-chainlit](https://github.com/sudarshan-koirala/langchain-ollama-chainlit)  
8. A Comprehensive Guide to Ollama Local Installation \- Collabnix, accessed August 4, 2025, [https://collabnix.com/a-comprehensive-guide-to-ollama-local-installation/](https://collabnix.com/a-comprehensive-guide-to-ollama-local-installation/)  
9. RAG with Ollama and Chainlit \- Dev Genius, accessed August 4, 2025, [https://blog.devgenius.io/rag-with-ollama-and-chainlit-cbea9ac3ec55](https://blog.devgenius.io/rag-with-ollama-and-chainlit-cbea9ac3ec55)  
10. ollama/ollama: Get up and running with Llama 3.3 ... \- GitHub, accessed August 4, 2025, [https://github.com/ollama/ollama](https://github.com/ollama/ollama)  
11. Download Ollama on macOS, accessed August 4, 2025, [https://ollama.com/download/mac](https://ollama.com/download/mac)  
12. Download Ollama on Linux, accessed August 4, 2025, [https://ollama.com/download](https://ollama.com/download)  
13. Download Ollama on Windows, accessed August 4, 2025, [https://ollama.com/download/windows](https://ollama.com/download/windows)  
14. How to Customize LLMs with Ollama | by Sumuditha Lansakara | Medium, accessed August 4, 2025, [https://medium.com/@sumudithalanz/unlocking-the-power-of-large-language-models-a-guide-to-customization-with-ollama-6c0da1e756d9](https://medium.com/@sumudithalanz/unlocking-the-power-of-large-language-models-a-guide-to-customization-with-ollama-6c0da1e756d9)  
15. How to Use Ollama: Hands-On With Local LLMs and Building a ..., accessed August 4, 2025, [https://hackernoon.com/how-to-use-ollama-hands-on-with-local-llms-and-building-a-chatbot](https://hackernoon.com/how-to-use-ollama-hands-on-with-local-llms-and-building-a-chatbot)  
16. Ollama, How to Install & Run LLM's on Windows in Minutes\! \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=3W-trR0ROUY](https://www.youtube.com/watch?v=3W-trR0ROUY)  
17. AIDevBytes/Custom-Llama3-Model: Create your own CUSTOM Llama 3 model using Ollama \- GitHub, accessed August 4, 2025, [https://github.com/AIDevBytes/Custom-Llama3-Model](https://github.com/AIDevBytes/Custom-Llama3-Model)  
18. Chainlit \- Build AI applications, accessed August 4, 2025, [https://chainlit.io/](https://chainlit.io/)  
19. Chainlit-Get Started\!\! \- Medium, accessed August 4, 2025, [https://medium.com/@danushidk507/chainlit-get-started-cb25205322d8](https://medium.com/@danushidk507/chainlit-get-started-cb25205322d8)  
20. How to Customize LLM Models with Ollama's Modelfile \- GPU Mart, accessed August 4, 2025, [https://www.gpu-mart.com/blog/custom-llm-models-with-ollama-modelfile](https://www.gpu-mart.com/blog/custom-llm-models-with-ollama-modelfile)  
21. Ollama \- Building a Custom Model \- Unmesh Gundecha, accessed August 4, 2025, [https://unmesh.dev/post/ollama\_custom\_model/](https://unmesh.dev/post/ollama_custom_model/)  
22. Modelfile Reference \- Ollama English Documentation, accessed August 4, 2025, [https://ollama.readthedocs.io/en/modelfile/](https://ollama.readthedocs.io/en/modelfile/)  
23. Chainlit: Overview, accessed August 4, 2025, [https://docs.chainlit.io/](https://docs.chainlit.io/)  
24. Chainlit Setup Tutorial \- Send First Message \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=lkvuMjievbA](https://www.youtube.com/watch?v=lkvuMjievbA)  
25. Could not reach the server · Issue \#274 · Chainlit/chainlit \- GitHub, accessed August 4, 2025, [https://github.com/Chainlit/chainlit/issues/274](https://github.com/Chainlit/chainlit/issues/274)  
26. Action \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/concepts/action](https://docs.chainlit.io/concepts/action)  
27. Action \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/api-reference/action](https://docs.chainlit.io/api-reference/action)  
28. Llama Index \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/integrations/llama-index](https://docs.chainlit.io/integrations/llama-index)  
29. Ollama Remote Server Setup \+ Chainlit \- Mervin Praison, accessed August 4, 2025, [https://mer.vin/2024/05/ollama-remote-server-setup-chainlit/](https://mer.vin/2024/05/ollama-remote-server-setup-chainlit/)  
30. Building an LLM Application for Document Q\&A Using Chainlit, Qdrant and Zephyr, accessed August 4, 2025, [https://nayakpplaban.medium.com/building-an-llm-application-for-document-q-a-using-chainlit-qdrant-and-zephyr-7efca1965baa](https://nayakpplaban.medium.com/building-an-llm-application-for-document-q-a-using-chainlit-qdrant-and-zephyr-7efca1965baa)  
31. UI \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/backend/config/ui](https://docs.chainlit.io/backend/config/ui)  
32. Avatars \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/customisation/avatars](https://docs.chainlit.io/customisation/avatars)  
33. Multi-Modality \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/advanced-features/multi-modal](https://docs.chainlit.io/advanced-features/multi-modal)  
34. Overview \- Chainlit, accessed August 4, 2025, [https://docs.chainlit.io/deploy/overview](https://docs.chainlit.io/deploy/overview)  
35. How I fixed a pip-compile dependency resolution error | by Ryan Hiebert | Medium, accessed August 4, 2025, [https://medium.com/@RyanHiebert/how-i-fixed-a-pip-compile-dependency-resolution-error-c09305e107e2](https://medium.com/@RyanHiebert/how-i-fixed-a-pip-compile-dependency-resolution-error-c09305e107e2)  
36. Fix Common Issues with Ollama \- Easy Explanation \- YouTube, accessed August 4, 2025, [https://www.youtube.com/watch?v=2bTHQx5qW8s](https://www.youtube.com/watch?v=2bTHQx5qW8s)  
37. Ollama Troubleshooting Guide \- Solving Common Issues ..., accessed August 4, 2025, [https://www.llamafactory.cn/ollama-docs/en/troubleshooting.html](https://www.llamafactory.cn/ollama-docs/en/troubleshooting.html)  
38. Chainlit does not start when requested (No errors is showed) · Issue \#993 \- GitHub, accessed August 4, 2025, [https://github.com/Chainlit/chainlit/issues/993](https://github.com/Chainlit/chainlit/issues/993)  
39. Langchain \+ Chainlit integration issue \#2730 \- GitHub, accessed August 4, 2025, [https://github.com/ollama/ollama/issues/2730](https://github.com/ollama/ollama/issues/2730)  
40. Common mistakes in local LLM deployments — an Ollama example | by Sebastian Panman de Wit, accessed August 4, 2025, [https://sebastianpdw.medium.com/common-mistakes-in-local-llm-deployments-03e7d574256b](https://sebastianpdw.medium.com/common-mistakes-in-local-llm-deployments-03e7d574256b)