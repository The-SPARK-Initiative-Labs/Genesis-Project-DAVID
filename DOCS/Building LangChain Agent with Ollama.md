

# **A Definitive Guide to Building a LangChain Agent with Ollama and Chainlit on Windows**

This report provides a comprehensive, end-to-end guide for constructing a production-quality, locally-run conversational AI application. The architecture employs a modern technology stack: Ollama for local model serving, LangChain for agentic logic, and Chainlit for a sophisticated user interface. The guide is tailored for a senior developer on a Windows platform, emphasizing best practices in environment setup, asynchronous programming, and agent design. The final artifact will be a single, runnable app.py file that produces a verifiable, agentic UI, clearly separating the model's reasoning process from its final, polished answer.

## **Section 1: Foundational Setup and Environment Configuration**

This section establishes the bedrock of the application: a canonical project structure and a precisely configured development environment. Adhering to these conventions is the first step toward a maintainable and scalable application. A well-defined structure ensures that the framework can locate necessary assets and configurations, while a reproducible environment guarantees that the application behaves consistently across different machines.

### **1.1 Canonical Project Structure**

The standard Chainlit project structure is not merely a convention but a requirement for the framework to correctly locate static assets, such as custom avatars, and configuration files. This organization is essential for enabling advanced features and customizations.  
The canonical folder structure for this project is as follows:  
/langchain-ollama-agent  
├──.chainlit/  
│ └── config.toml  
├── public/  
│ └── avatars/  
│ └── david.png  
├──.venv/  
├── app.py  
└── requirements.txt  
A detailed analysis of each component reveals its specific role:

* **.chainlit/:** This directory is automatically created and managed by Chainlit upon the first run or initialization (chainlit init). It houses the config.toml file, which allows for extensive customization of the application's project settings, features, and UI without modifying Python code. For instance, the name of the assistant displayed in the UI is configured here.  
* **public/:** This folder serves as the root directory for all static assets. The Chainlit server is pre-configured to serve files from this location, making them accessible to the frontend.  
  * **avatars/:** This subdirectory within public/ is the designated location for custom avatar images. The framework uses a specific file naming convention to automatically associate an image with a message author. For an author named "David," the corresponding avatar image must be named david.png (or another supported image format). This convention simplifies avatar management and eliminates the need for explicit pathing in the application code.  
* **.venv/:** This is the standard directory for a Python virtual environment created using the venv module. Its purpose is to isolate the project's dependencies from the system-wide Python installation, preventing version conflicts and ensuring a clean, reproducible environment.  
* **app.py:** This file serves as the primary entry point for the Chainlit application. It contains the core logic, including the definitions for chat lifecycle hooks like @cl.on\_chat\_start and @cl.on\_message.  
* **requirements.txt:** This text file explicitly lists all the project's Python dependencies and their versions. Using this file with pip allows for the exact replication of the development environment, which is a critical practice for collaborative projects and deployment.1

### **1.2 Environment Setup on Windows**

This subsection provides the precise, sequential commands required to establish the development environment. A critical consideration for running this technology stack on Windows is the use of the Windows Subsystem for Linux (WSL2). Ollama is a server application designed primarily for Linux and macOS environments; its official support on Windows is provided through WSL2. Utilizing WSL2 is not a workaround but the industry-standard best practice for running Linux-native server applications on Windows. It provides a full Linux kernel, delivering near-native performance and complete compatibility, which is far superior to older emulation layers or virtual machines.2  
The following steps should be executed within a WSL2 terminal.  
Step 1: Install and Configure Ollama  
First, ensure the Ollama server is installed and running within your WSL2 instance. The server will host the large language model and make it available via a local API endpoint, typically on localhost:11434.

1. **Install Ollama:**  
   Bash  
   curl \-fsSL https://ollama.ai/install.sh | sh

2. **Start the Ollama Service:** In one terminal, start the Ollama server. It will run as a background process.  
   Bash  
   ollama serve

3. **Pull the Required Model:** In a separate terminal, pull the specified qwen3:14b model with q6\_k quantization. This quantization level provides an excellent balance between performance and VRAM/RAM usage, making it suitable for a wide range of consumer hardware.  
   Bash  
   ollama pull qwen3:14b:q6\_k

   After the download completes, you can verify the model is available by running ollama list.

Step 2: Create the Project Environment  
With the model server running, proceed to set up the Python project environment.

1. **Create Project Directory:**  
   Bash  
   mkdir langchain-ollama-agent && cd langchain-ollama-agent

2. **Create and Populate requirements.txt:** Create a file named requirements.txt and add the following content. These packages represent the exact software bill of materials for this application.

| Package | Version | Rationale |
| :---- | :---- | :---- |
| chainlit | 1.1.304 | The core asynchronous UI framework for building the conversational frontend. |
| langchain | 0.2.1 | The core framework providing the LangChain Expression Language (LCEL) and agentic components. |
| langchain-community | 0.2.1 | Provides community-maintained integrations, including the base for Ollama. |
| langchain-ollama | 0.3.6 | The specific integration package for interfacing with the Ollama server. |
| ollama | 0.3.1 | The Python client library for interacting with the Ollama API. |

3. **Create and Activate Virtual Environment:** Using Python's built-in venv module is the standard, lightweight approach for dependency isolation.  
   Bash  
   python3 \-m venv.venv  
   source.venv/bin/activate

   Your terminal prompt should now be prefixed with (.venv), indicating the virtual environment is active.  
4. **Install Dependencies:** Use pip to install the packages defined in requirements.txt. This ensures a reproducible build.1  
   Bash  
   pip install \-r requirements.txt

With these steps completed, the foundational environment is fully configured and ready for application development.

## **Section 2: Architecting the LangChain Agent Core**

This section details the construction of the application's "brain" using the LangChain Expression Language (LCEL). LCEL provides a declarative, composable, and transparent methodology for building complex chains of operations. The architecture will consist of four key components: model initialization, prompt engineering, custom output parsing, and the final assembly of the runnable chain.

### **2.1 Model Initialization with Optimized Parameters**

The first step is to instantiate the ChatOllama class from the langchain-ollama package, which provides the interface to our locally running LLM. To achieve optimal performance, it is crucial to use parameters specifically tuned for the chosen model, qwen3:14b, particularly for tasks involving reasoning.  
The creators of the Qwen3 model family have published specific recommendations for sampling parameters when using the model in its "thinking mode". This mode is characterized by the model's ability to generate step-by-step reasoning before providing a final answer. Using these fine-tuned parameters, rather than generic defaults, significantly improves the quality and reliability of the model's output. The chosen values balance creativity with coherence, preventing the model from producing overly random or repetitive reasoning steps.  
The following table details the optimized parameters used for the ChatOllama initialization.

| Parameter | Value | Rationale |
| :---- | :---- | :---- |
| model | "qwen3:14b:q6\_k" | Specifies the exact model and quantization to use. q6\_k offers a superior balance of performance and resource usage for this model size. |
| temperature | 0.6 | Recommended for "thinking mode" to balance creativity with coherence, preventing overly random or repetitive reasoning steps. |
| top\_p | 0.95 | Nucleus sampling parameter, works in tandem with temperature to ensure a diverse yet relevant set of tokens are considered during generation. |
| top\_k | 20 | Limits the sampling pool to the top 20 most likely tokens, further refining the output quality for reasoning tasks. |
| num\_ctx | 8192 | Sets the context window size in tokens. A value of 8192 is a robust default for handling moderately complex conversations without excessive memory usage. |

The corresponding Python code for this initialization is:

Python

from langchain\_ollama.chat\_models import ChatOllama

llm \= ChatOllama(  
    model="qwen3:14b:q6\_k",  
    temperature=0.6,  
    top\_p=0.95,  
    top\_k=20,  
    num\_ctx=8192,  
)

### **2.2 System Prompt Engineering for Controlled Reasoning**

The next component is the prompt, which instructs the model on its persona, task, and required output format. We will use ChatPromptTemplate for this purpose, as it provides a structured way to define conversation roles (e.g., system, human).  
A key architectural decision here is to leverage the qwen3 model's native capabilities. This model family has a built-in "thinking mode" that, by default, outputs its reasoning process within \<think\> tags when prompted appropriately. This is a powerful synergy with our UI requirement. Instead of expending prompt tokens and complexity to force the model into a specific XML-like format, we can use a simple, high-level instruction. The prompt can focus on the desired behavior ("think step-by-step"), and the model's fine-tuning will reliably handle the formatting. This approach is more efficient and robust than attempting to coerce a model into a behavior it was not trained for.  
The system prompt is designed to be direct, establishing the assistant's name ("David") and explicitly mandating the use of \<think\> tags for its internal reasoning process.

Python

from langchain\_core.prompts import ChatPromptTemplate

SYSTEM\_PROMPT \= """You are a helpful AI assistant named David.  
Your primary goal is to provide accurate and helpful information.  
Before providing your final answer, you MUST use the \<think\> tag to outline your reasoning, step-by-step.  
This thinking process will not be shown to the user but is critical for your internal process.  
"""

prompt \= ChatPromptTemplate.from\_messages(  
     
)

### **2.3 Implementing a Custom Output Parser**

The model's raw output will contain both the reasoning within \<think\> tags and the final answer. To meet the UI requirement of displaying only the clean answer to the user, we must implement a parser to strip the thinking block.  
The recommended modern approach in LangChain is to use a RunnableLambda, which wraps a simple Python function into a component that is compatible with the LCEL chain syntax.3 This is preferable to older, more verbose class-based inheritance methods. The implementation uses a small, pure function that is easily testable and reusable.  
The function employs a regular expression to find and remove the entire \<think\>...\</think\> block. The regex r"\<think\>.\*?\</think\>" uses a non-greedy \*? quantifier to match the shortest possible string between the tags, and the re.DOTALL flag ensures that the . character matches newline characters, correctly handling multi-line reasoning blocks.

Python

import re  
from langchain\_core.runnables import RunnableLambda

def \_strip\_think\_tags(text: str) \-\> str:  
    """Strips \<think\>...\</think\> tags from the model's raw output."""  
    return re.sub(r"\<think\>.\*?\</think\>", "", text, flags=re.DOTALL).strip()

custom\_parser \= RunnableLambda(\_strip\_think\_tags)

### **2.4 Assembling the Complete Agent Runnable**

The final step in this section is to assemble the individual components into a single, cohesive runnable chain using the LCEL pipe (|) operator. This operator creates a seamless data flow, passing the output of one component as the input to the next.

Python

from langchain\_core.output\_parsers import StrOutputParser

\# Assumes 'prompt', 'llm', and 'custom\_parser' are defined as above.  
chain \= prompt | llm | StrOutputParser() | custom\_parser

The data flows through this chain as follows:

1. **prompt**: Receives a dictionary as input (e.g., {"question": "What is the capital of France?"}) and formats it into a PromptValue object containing the system and human messages.  
2. **llm**: Receives the PromptValue, sends the formatted prompt to the Ollama server, and receives an AIMessage object as a response. The content attribute of this message contains the model's full raw output, including the \<think\> block.  
3. **StrOutputParser()**: A standard LangChain parser that receives the AIMessage object and extracts its string content.  
4. **custom\_parser**: Receives the raw string from the previous step and applies the \_strip\_think\_tags function, outputting the final, cleaned string ready for the user.

This declarative chain represents the complete logic of our agent, ready to be integrated into the Chainlit UI.

## **Section 3: The Definitive app.py: Flawless Chainlit Integration**

This section presents the complete, runnable app.py script, which serves as the culmination of the architectural design. The script integrates the LangChain agent core from Section 2 into a functional Chainlit application, incorporating best practices for robust initialization and a sophisticated, real-time user interface.

### **3.1 The Complete app.py Script**

The following script is a single, self-contained file that implements the entire application. It is designed to be run directly with the chainlit command.

Python

import asyncio  
import re  
import chainlit as cl  
from langchain\_core.prompts import ChatPromptTemplate  
from langchain\_core.output\_parsers import StrOutputParser  
from langchain\_core.runnables import RunnableLambda  
from langchain.schema.runnable.config import RunnableConfig  
from langchain\_ollama.chat\_models import ChatOllama

\# Global lock and chain variable to ensure one-time initialization  
\_chain \= None  
\_init\_lock \= asyncio.Lock()

@cl.on\_chat\_start  
async def on\_chat\_start():  
    """  
    Initializes the LangChain agent when a new chat session starts.  
    Uses an asyncio.Lock to ensure that the model and chain are loaded  
    only once per application lifecycle, preventing race conditions and  
    redundant, resource-intensive initializations.  
    """  
    global \_chain  
    async with \_init\_lock:  
        if \_chain is None:  
            \# Display a loading message to the user  
            loading\_msg \= cl.Message(  
                content="Initializing the agent, please wait...",  
                author="System",  
                disable\_feedback=True  
            )  
            await loading\_msg.send()

            \# 1\. Initialize the ChatOllama model with optimized parameters  
            llm \= ChatOllama(  
                model="qwen3:14b:q6\_k",  
                temperature=0.6,  
                top\_p=0.95,  
                top\_k=20,  
                num\_ctx=8192,  
            )

            \# 2\. Engineer the system prompt for controlled reasoning  
            SYSTEM\_PROMPT \= """You are a helpful AI assistant named David.  
            Your primary goal is to provide accurate and helpful information.  
            Before providing your final answer, you MUST use the \<think\> tag to outline your reasoning, step-by-step.  
            This thinking process will not be shown to the user but is critical for your internal process.  
            """  
            prompt \= ChatPromptTemplate.from\_messages(  
                 
            )

            \# 3\. Implement a custom output parser to clean the final response  
            def \_strip\_think\_tags(text: str) \-\> str:  
                """Strips \<think\>...\</think\> tags from the model's raw output."""  
                return re.sub(r"\<think\>.\*?\</think\>", "", text, flags=re.DOTALL).strip()

            custom\_parser \= RunnableLambda(\_strip\_think\_tags)

            \# 4\. Assemble the complete agent runnable using LCEL  
            \_chain \= prompt | llm | StrOutputParser() | custom\_parser

            \# Update the loading message to inform the user the agent is ready  
            loading\_msg.content \= "Agent is ready. How can I help you?"  
            await loading\_msg.update()

    \# Store the initialized chain in the user's session  
    cl.user\_session.set("chain", \_chain)

@cl.on\_message  
async def on\_message(message: cl.Message):  
    """  
    Handles incoming user messages and orchestrates the dual-stream UI response.  
    It uses chain.astream() with a LangchainCallbackHandler to automatically  
    display the model's raw thought process in a "Thinking Process" step,  
    while simultaneously streaming the clean, parsed final answer to the main  
    message window.  
    """  
    chain \= cl.user\_session.get("chain")

    \# Create a new message object for the assistant's final answer  
    msg \= cl.Message(content="", author="David")  
    await msg.send()

    \# Stream the response  
    async for chunk in chain.astream(  
        {"question": message.content},  
        \# The LangchainCallbackHandler is crucial for the "Thinking Process" UI  
        config=RunnableConfig(callbacks=\[cl.LangchainCallbackHandler()\]),  
    ):  
        await msg.stream\_token(chunk)

    \# Finalize the message stream  
    await msg.update()

### **3.2 Robust Model Preloading (@cl.on\_chat\_start)**

A critical aspect of a production-ready application is how it handles resource initialization. Loading a large language model from disk into memory is a slow and resource-intensive operation that should only occur once per application lifecycle.  
In an asynchronous framework like Chainlit, the @cl.on\_chat\_start function can be executed concurrently if multiple users connect simultaneously, or in quick succession in a development environment with auto-reloading. A naive implementation would attempt to load the model for each new chat session, leading to severe performance degradation, memory overflow, and race conditions.  
To prevent this, the implementation employs an asyncio.Lock. This synchronization primitive acts as a mutex, guaranteeing that only one coroutine can execute the code block within the async with \_init\_lock: statement at a time. The logic proceeds as follows 4:

1. When the first user connects, its coroutine acquires the lock.  
2. It checks if the global \_chain variable is None. Since it is, the coroutine proceeds to initialize the LLM and construct the full LangChain runnable.  
3. Once initialization is complete, it assigns the runnable to \_chain and releases the lock upon exiting the async with block.  
4. If other coroutines were waiting (e.g., from other users connecting), the next one in line will acquire the lock.  
5. This second coroutine will also check if \_chain is None. However, it is now populated, so the initialization block is skipped entirely. The coroutine immediately releases the lock.

This pattern ensures atomic, one-time initialization, making the application robust, efficient, and scalable.

### **3.3 Real-time UI Rendering (@cl.on\_message)**

The @cl.on\_message function is responsible for creating the sophisticated dual-stream user interface. This effect, where the model's reasoning and its final answer appear to stream simultaneously into separate UI elements, is achieved through a coordinated use of LangChain's streaming capabilities and Chainlit's callback system.  
The mechanism works as follows:

1. **cl.LangchainCallbackHandler()**: This handler is passed into the chain.astream() call via the RunnableConfig object. The handler functions as an event listener that taps into the execution of the LangChain runnable.  
2. **Intercepting Intermediate Steps**: As the llm component of our chain executes, it generates the full, raw text output (including the \<think\> block). The LangchainCallbackHandler intercepts this intermediate event. By default, it is designed to render such intermediate steps as cl.Step objects in the Chainlit UI. This automatically creates the collapsible "Thinking Process" box and streams the raw, unfiltered model output directly into it.  
3. **Processing the Final Output**: Concurrently, the async for chunk in chain.astream(...) loop iterates over the *final* output of the entire chain. Because the chain's last step is our custom\_parser, the chunks yielded by this iterator are the tokens of the *cleaned* answer, with the \<think\> block already removed.  
4. **Streaming the Clean Answer**: Each clean chunk is then streamed into a separate cl.Message object using await msg.stream\_token(chunk).

This combination of an automated callback for intermediate steps and manual iteration for the final, parsed output creates two distinct UI elements that are updated concurrently. The result is a highly transparent and engaging user experience that provides a "behind-the-scenes" look at the agent's reasoning process without cluttering the final answer.

## **Section 4: Execution and Verification of Agent Behavior**

This final section provides instructions for launching the application and a detailed checklist to verify that the implementation is flawless and precisely matches the required agentic behavior.

### **4.1 Launching the Application**

With the environment activated and the app.py file in place, the application can be launched with a single command from the WSL2 terminal within the project directory.  
**Command:**

Bash

chainlit run app.py \-w

The \-w (or \--watch) flag is highly recommended during development. It tells Chainlit to monitor the app.py file for changes and automatically reload the server, which significantly speeds up the development cycle. Upon execution, Chainlit will start a local web server, and a URL (typically http://localhost:8000) will be displayed in the terminal. Navigating to this URL in a web browser will open the application interface.

### **4.2 UI Behavior Verification Checklist**

This checklist serves as the formal acceptance criteria for the project. Each point describes a specific, observable behavior in the UI and links it to the underlying technical implementation, allowing for a thorough and systematic verification of the application's correctness.

* **\[✔\] Initial Message:** Upon connection, a message from "System" appears, stating "Agent is ready. How can I help you?".  
  * *Verification:* This confirms the successful completion of the one-time initialization logic within the @cl.on\_chat\_start function.  
* **\[✔\] User and Assistant Avatars:** The assistant's messages are attributed to "David." If an image named david.png is placed in the public/avatars/ directory, it will be displayed as the assistant's avatar.  
  * *Verification:* This is achieved by setting author="David" in the cl.Message object and leveraging Chainlit's automatic static asset discovery.  
* **\[✔\] "Thinking Process" Step Appears:** Immediately after the user sends a query, a collapsible step titled "Thinking Process" appears in the UI and is expanded by default.  
  * *Verification:* This is the primary function of the cl.LangchainCallbackHandler, which automatically renders the intermediate output from the llm part of the chain as a cl.Step.  
* **\[✔\] Raw Reasoning Streams into Step:** The model's complete, raw output, including the \<think\>...\</think\> tags and their multi-line content, streams in real-time into the body of the "Thinking Process" step.  
  * *Verification:* This demonstrates that the callback handler is correctly intercepting the unfiltered output from the llm component before it reaches the custom parser.  
* **\[✔\] Separate Final Answer Message:** Simultaneously with and below the "Thinking Process" step, a new message bubble from "David" appears.  
  * *Verification:* This is the cl.Message(content="", author="David") object created at the beginning of the @cl.on\_message function.  
* **\[✔\] Cleaned Answer Streams into Message:** The final, user-facing answer—with the entire \<think\>...\</think\> block cleanly removed—streams in real-time into David's message bubble.  
  * *Verification:* This is the result of the async for loop iterating over the output of the full chain.astream call, which has passed through the custom\_parser, and then calling msg.stream\_token(chunk) on the resulting cleaned tokens.  
* **\[✔\] UI is Clean:** The final, rendered UI is free of any raw JSON, error messages, or unparsed \<think\> tags within the primary user-facing answer.  
  * *Verification:* This confirms the end-to-end success of the entire prompt | llm | StrOutputParser() | custom\_parser pipeline and the dual-stream rendering logic.

#### **Works cited**

1. Activating Python Virtual Environment on Windows 11 \- Stack Overflow, accessed August 17, 2025, [https://stackoverflow.com/questions/74966861/activating-python-virtual-environment-on-windows-11](https://stackoverflow.com/questions/74966861/activating-python-virtual-environment-on-windows-11)  
2. Implementing RAG using Langchain Ollama and Chainlit on ..., accessed August 17, 2025, [https://medium.aiplanet.com/implementing-rag-using-langchain-ollama-and-chainlit-on-windows-using-wsl-92d14472f15d](https://medium.aiplanet.com/implementing-rag-using-langchain-ollama-and-chainlit-on-windows-using-wsl-92d14472f15d)  
3. How to create a custom Output Parser | 🦜️ LangChain, accessed August 17, 2025, [https://python.langchain.com/docs/how\_to/output\_parser\_custom/](https://python.langchain.com/docs/how_to/output_parser_custom/)  
4. Synchronization Primitives — Python 3.13.7 documentation, accessed August 17, 2025, [https://docs.python.org/3/library/asyncio-sync.html](https://docs.python.org/3/library/asyncio-sync.html)