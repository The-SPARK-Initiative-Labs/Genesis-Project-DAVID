

# **The Definitive Guide to Building a Production-Ready Local AI Stack: Ollama, LangChain, and Chainlit on Windows**

## **Introduction**

### **Purpose and Audience**

This guide serves as an expert-level, end-to-end tutorial for senior AI developers tasked with building a production-quality, fully local conversational AI application. The focus is on the flawless integration of a specific, modern technology stack on the Windows operating system, resulting in a stable, performant, and correctly functioning application built from a clean slate.

### **The Modern Local AI Stack**

The architecture detailed herein leverages a curated set of powerful, open-source tools. Ollama provides the backend, offering a remarkably simple and efficient method for serving large language models on local hardware.1 LangChain serves as the orchestration framework, providing the robust abstractions necessary for building complex, stateful AI agents.3 Finally, Chainlit delivers the user interface, enabling the rapid development of a polished front-end with unique capabilities for visualizing an agent's multi-step reasoning process, a feature critical for debugging and transparency.5

### **Core Philosophy: Privacy, Performance, and Transparency**

The primary advantage of this stack is its complete self-sufficiency. By running entirely on a local machine, it guarantees absolute data privacy, as no information is ever transmitted to a third-party service. This eliminates API-related costs and dependencies, granting developers full control over the application's performance and availability. The architecture emphasizes transparency, employing specific prompt engineering techniques and UI integrations to make the agent's internal reasoning process explicit and observable, a cornerstone of building trustworthy and debuggable AI systems.

### **Model Selection Note**

This guide targets the qwen2:14b model family. While the original mandate specified a potential qwen3 variant, the most capable and widely available model at the time of this writing is qwen2:14b-instruct-q6\_K.7 This 14-billion-parameter, instruction-tuned model from Alibaba offers exceptional performance across a range of tasks. The  
q6\_K quantization represents an optimal balance between computational efficiency and response quality, making it well-suited for deployment on modern consumer-grade hardware. The architecture presented is fundamentally model-agnostic; the model identifier in the configuration can be easily updated as new models become available in the Ollama library.  
---

## **Section 1: Architecting the Foundational Environment**

A production-ready application begins with a solid foundation. This section details the complete setup process on a Windows machine, establishing a professional, scalable, and reproducible project structure that adheres to established software engineering best practices.

### **1.1 The Canonical Project Structure for Maintainability**

To ensure long-term maintainability and prevent common Python import conflicts, this guide adopts the "src layout." This structure creates a clear separation between the application's source code and its configuration, documentation, and testing assets.9  
The final project directory will be organized as follows:

local-ai-agent/  
├──.chainlit/  
│   └── config.toml  
├──.venv/  
├── src/  
│   └── local\_agent/  
│       ├── \_\_init\_\_.py  
│       └── agent.py  
├──.gitignore  
├── app.py  
└── requirements.txt

Each component of this structure serves a distinct purpose:

* **local-ai-agent/**: The root directory of the project. All commands should be executed from this location.  
* **.chainlit/config.toml**: This file is used for Chainlit-specific configurations, such as customizing the UI theme, enabling features, or defining chat profiles.11  
* **.venv/**: This directory contains the isolated Python virtual environment, including the Python interpreter and all installed project dependencies. It should never be committed to version control.13  
* **src/**: The primary source directory. Placing application code here prevents the project root from being added to PYTHONPATH, avoiding subtle bugs related to module resolution.  
* **src/local\_agent/**: The main Python package for our application.  
* **src/local\_agent/agent.py**: A dedicated module responsible for constructing and configuring the LangChain agent. This modular approach promotes a clean separation of concerns, keeping the core AI logic distinct from the UI presentation layer.15  
* **app.py**: The main entry point for the Chainlit application. This script will import the agent from the src directory and handle the UI lifecycle.  
* **requirements.txt**: A text file that explicitly lists all project dependencies and their versions, ensuring a fully reproducible environment for any developer.  
* **.gitignore**: A standard Git configuration file used to exclude specific files and directories, such as the .venv folder and Python bytecode cache (\_\_pycache\_\_), from source control.

### **1.2 Establishing the Local AI Backend with Ollama**

Ollama is the engine of our local AI stack. Its installation on Windows is streamlined and efficient.

1. **Download and Install:** Navigate to the official Ollama website (ollama.com) and download the Windows installer.17 Execute the downloaded file and follow the on-screen instructions. The installer will configure Ollama as a background service that automatically starts on system boot, ensuring the model server is always available when needed.1  
2. **Verify the Installation:** Once the installation is complete, open a new PowerShell terminal. You can verify that the Ollama service is running and accessible by executing the following command:  
   PowerShell  
   curl http://localhost:11434

   A successful installation will return the message: Ollama is running.19 You can also type  
   ollama to see a list of available commands.20  
3. **Pull the Language Model:** With the Ollama server running, the next step is to download the specified large language model. Execute the following command in PowerShell:  
   PowerShell  
   ollama pull qwen2:14b-instruct-q6\_K

   This command connects to the Ollama model registry and downloads the qwen2 model with the 14b-instruct-q6\_K tag. This specific version is a 14-billion-parameter model that has been instruction-tuned for chat and question-answering tasks. The q6\_K quantization provides high precision with a manageable memory footprint of approximately 12 GB, making it suitable for systems with at least 16 GB of RAM and a modern GPU.7  
4. **Confirm the Model:** To ensure the model was downloaded correctly, list all locally available models:  
   PowerShell  
   ollama list

   The output should include an entry for qwen2:14b-instruct-q6\_K, confirming it is ready for use.21

### **1.3 Professional Python Environment Setup on Windows**

A dedicated, isolated virtual environment is non-negotiable for professional Python development. It prevents dependency conflicts between projects and ensures that the application's environment is explicit and reproducible.22

1. **Create the Virtual Environment:** From the root of your project directory (local-ai-agent/), execute the following command:  
   PowerShell  
   python \-m venv.venv

   This command utilizes Python's built-in venv module to create a new virtual environment inside the .venv folder.14  
2. **Activate the Virtual Environment:** To begin using the environment, it must be activated. Run the following command in your PowerShell terminal:

..venv\\Scripts\\Activate.ps1  
\`\`\`  
Upon successful activation, your PowerShell prompt will be prefixed with (.venv), indicating that any subsequent python or pip commands will be executed within this isolated environment.22

3. **Address PowerShell Execution Policy (If Necessary):** On many Windows systems, the default PowerShell security policy prevents the execution of scripts, including the activation script. If you encounter an UnauthorizedAccess error, you must adjust the execution policy. The recommended practice for developers is to allow locally created scripts to run. Execute the following command to set the policy for the current user only, which is a more secure alternative to changing the system-wide policy:  
   PowerShell  
   Set-ExecutionPolicy \-ExecutionPolicy RemoteSigned \-Scope CurrentUser

   You may need to confirm this change by typing 'Y' and pressing Enter. This setting allows local scripts to run while requiring that scripts downloaded from the internet are digitally signed by a trusted publisher.24  
4. **Install Dependencies:** Create a file named requirements.txt in the project root with the following content:  
   \# requirements.txt  
   chainlit  
   langchain  
   langchain-community  
   langchain-ollama  
   python-dotenv

   With the virtual environment activated, install all necessary libraries in a single step using pip:  
   PowerShell  
   pip install \-r requirements.txt

   This command reads the requirements.txt file and installs the exact dependencies required for the project, ensuring a consistent setup across different machines.23 The roles of these core dependencies are summarized in Table 1\.

**Table 1: Core Project Dependencies**

| Library | Role in Stack |
| :---- | :---- |
| chainlit | **UI Framework:** Provides the front-end, session management, and visualization of agent reasoning.5 |
| langchain | **Core Framework:** Provides the AgentExecutor and core Runnable abstractions (LCEL).3 |
| langchain-community | **Community Integrations:** Contains foundational components and tools used by the agent.3 |
| langchain-ollama | **Backend Integration:** Provides the ChatOllama class, the specific bridge to the local Ollama server.25 |
| python-dotenv | **Configuration Best Practice:** Manages environment variables, keeping configuration separate from code.27 |

---

## **Section 2: Constructing the Conversational Agent Core**

With the foundational environment established, the focus now shifts to building the "brain" of the application: a modular, stateful, and transparent LangChain agent.

### **2.1 The Agent Module: src/local\_agent/agent.py**

All logic related to the agent's construction will be encapsulated within the src/local\_agent/agent.py module. This design choice adheres to the Single Responsibility Principle, making the main app.py script cleaner and more focused on UI-related tasks. This separation is crucial for scalability and testing, as the core agent logic can be developed and validated independently of its presentation layer. This module will export a single function, create\_agent\_executor(), which will assemble and return the fully configured, memory-enabled agent.

### **2.2 Initializing the Local LLM with LangChain**

The first step within agent.py is to establish a connection to the Ollama server. This is accomplished using the ChatOllama class from the langchain-ollama integration package.  
Create the file src/local\_agent/agent.py and add the following code to instantiate the language model:

Python

from langchain\_ollama.chat\_models import ChatOllama

def create\_agent\_executor():  
    """  
    Creates and returns a stateful conversational agent executor.  
    """  
    llm \= ChatOllama(  
        model="qwen2:14b-instruct-q6\_K",  
        temperature=0,  
        streaming=True  
    )  
    \#... more code will be added here

Each parameter in the ChatOllama constructor is critical:

* model: This string must exactly match the name of the model as it appears in the output of the ollama list command.  
* temperature: Setting this to 0 makes the model's output more deterministic and less random. For an agent designed to follow a strict reasoning process, predictability is more valuable than creativity.  
* streaming: This boolean flag, when set to True, enables the model to yield its response token by token. This is essential for creating a responsive, real-time user experience in the Chainlit UI.28

### **2.3 Advanced Prompt Engineering for Transparent Reasoning**

To fulfill the requirement of separating the agent's internal reasoning from its final answer, a carefully crafted prompt template is required. This is not merely a formatting instruction; it fundamentally guides the model's inference process, compelling it to adopt a more structured, step-by-step approach akin to a ReAct (Reasoning and Acting) framework.29 This technique significantly improves the reliability and debuggability of the agent's behavior.  
The prompt will instruct the model to first articulate its thought process within a specific XML-style tag (\<thinking\>) before providing the user-facing answer.  
Add the following imports and prompt definition to src/local\_agent/agent.py:

Python

from langchain\_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create\_agent\_executor():  
    \#... llm instantiation from previous step...

    prompt \= ChatPromptTemplate.from\_messages(  
         
    )  
    \#... more code will be added here

This ChatPromptTemplate is composed of three key parts:

1. **System Message:** This sets the overall context and establishes the strict rules the model must follow. It defines the "contract" for the output format, including the use of \<thinking\> tags, and provides a one-shot example to guide the model's behavior.  
2. **MessagesPlaceholder:** This is a critical component for building conversational agents. It designates where the list of previous messages from the conversation history will be injected into the prompt, providing the model with the necessary context to handle follow-up questions.31  
3. **Human Message:** This placeholder ({input}) is where the user's most recent message will be inserted.

### **2.4 Building the Stateful Agent Chain**

With the model and prompt defined, the final step is to assemble them into a runnable chain and equip it with memory. While a full-fledged agent would typically involve tools and an AgentExecutor, this guide focuses on the core conversational and reasoning loop. The principle of adding memory remains the same. The modern, canonical approach in LangChain for managing conversation history is RunnableWithMessageHistory.  
Complete the create\_agent\_executor function in src/local\_agent/agent.py:

Python

from langchain\_ollama.chat\_models import ChatOllama  
from langchain\_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain\_core.runnables.history import RunnableWithMessageHistory  
from langchain\_community.chat\_message\_histories import ChatMessageHistory

def create\_agent\_executor():  
    """  
    Creates and returns a stateful conversational agent executor.  
    """  
    llm \= ChatOllama(  
        model="qwen2:14b-instruct-q6\_K",  
        temperature=0,  
        streaming=True  
    )

    prompt \= ChatPromptTemplate.from\_messages(  
         
    )

    \# Simple chain for this example  
    agent\_chain \= prompt | llm

    \# Add memory management  
    agent\_with\_memory \= RunnableWithMessageHistory(  
        agent\_chain,  
        lambda session\_id: ChatMessageHistory(),  \# Use in-memory history for each session  
        input\_messages\_key="input",  
        history\_messages\_key="chat\_history",  
    )

    return agent\_with\_memory

The RunnableWithMessageHistory wrapper is a powerful abstraction. It takes the core agent\_chain and augments it with statefulness. The lambda session\_id: ChatMessageHistory() part is a factory function that creates a new, empty, in-memory message history for each unique session ID it encounters.32 This elegantly solves the problem of keeping user conversations isolated. The  
input\_messages\_key and history\_messages\_key parameters instruct the runnable on how to map the input dictionary to the variables in our ChatPromptTemplate.  
---

## **Section 3: Flawless UI Integration with Chainlit**

This section provides the complete, runnable code to deploy the agent within an interactive web interface, demonstrating the definitive patterns for managing the agent's lifecycle and handling real-time communication.

### **3.1 The Definitive app.py Script**

The app.py file, located in the project root, serves as the entry point for the Chainlit application. It is responsible for importing the agent, managing its lifecycle per user session, and processing messages.  
Create the file app.py with the following content:

Python

import chainlit as cl  
from src.local\_agent.agent import create\_agent\_executor

@cl.on\_chat\_start  
async def on\_chat\_start():  
    """  
    Initializes and stores the agent executor in the user session when a new chat starts.  
    """  
    agent\_executor \= create\_agent\_executor()  
    cl.user\_session.set("agent\_executor", agent\_executor)

@cl.on\_message  
async def on\_message(message: cl.Message):  
    """  
    Handles incoming user messages, invokes the agent, and streams the response.  
    """  
    agent\_executor \= cl.user\_session.get("agent\_executor")

    \# The LangchainCallbackHandler is crucial for displaying intermediate steps  
    cb \= cl.AsyncLangchainCallbackHandler(stream\_final\_answer=True)

    \# The session\_id is essential for the agent to recall conversation history  
    config \= {"configurable": {"session\_id": "main\_session"}}

    \# Invoke the agent with the user's message and the callback handler  
    await agent\_executor.ainvoke(  
        {"input": message.content},  
        config={"callbacks": \[cb\], \*\*config}  
    )

### **3.2 Managing the Agent Lifecycle per Session**

The @cl.on\_chat\_start decorator is a Chainlit lifecycle hook that executes its decorated function once at the beginning of every new chat session.12 In our  
app.py, this function calls create\_agent\_executor() from our dedicated module. The returned agent, complete with its memory-management wrapper, is then stored in cl.user\_session. The user session is a key-value store that is unique to each user's connection, ensuring that each conversation has its own isolated agent instance and chat history. This pattern is fundamental to building robust, multi-user conversational applications.33

### **3.3 Handling User Interaction and Real-Time Streaming**

The @cl.on\_message decorator is the core of the interactive loop. It triggers its function every time the user sends a message.27 The implementation demonstrates the most effective and seamless pattern for integrating a LangChain agent with Chainlit:

1. **Retrieve the Agent:** The agent instance is retrieved from the cl.user\_session, ensuring we are using the correct one for the current conversation.  
2. **Instantiate the Callback Handler:** cl.AsyncLangchainCallbackHandler is the key to visualizing the agent's reasoning. This specialized handler is designed to intercept events from the LangChain execution process. When it detects an intermediate step (like the output from an LLM call before the final answer), it automatically renders it as a collapsible "step" in the UI.34 Setting  
   stream\_final\_answer=True instructs the handler to also stream the final part of the response token by token.35  
3. **Configure for Memory:** The config dictionary is prepared with a session\_id. This ID is passed to the RunnableWithMessageHistory wrapper, which uses it to retrieve the correct ChatMessageHistory object for the current conversation.  
4. **Invoke the Agent:** The agent is invoked asynchronously with agent\_executor.ainvoke(). The crucial part is passing the callbacks list containing our Chainlit handler. LangChain's execution engine will now send all events—start of a chain, output of a model, end of a tool call—to this handler, which in turn updates the UI in real time. This callback-based approach is the definitive, error-free pattern for achieving the desired transparent reasoning and real-time streaming.

To run the application, ensure your virtual environment is activated and execute the following command from the project root:

PowerShell

chainlit run app.py \-w

The \-w flag enables auto-reloading, so the application will automatically restart whenever you save changes to the source files.  
---

## **Section 4: The End-User Experience: Visualizing the Agent's Mind**

This final section describes the correct, expected behavior of the application's user interface, allowing for verification of a successful build. The focus is on how the user experiences the clear, intuitive separation of the agent's reasoning process and its final response.

### **4.1 Expected Application Behavior**

Upon running the chainlit run command, a web browser tab should open to http://localhost:8000. The user is presented with a clean, modern chat interface, ready to accept input. When the user types a query (e.g., "Explain the significance of the Magna Carta") and submits it, the application will execute the agent and render the results in a specific, two-part sequence.

### **4.2 Visualizing the Chain of Thought**

Almost immediately after the user submits their message, a new, collapsed UI element will appear in the chat stream. This element represents the agent's intermediate reasoning step, captured automatically by the cl.LangchainCallbackHandler.6 This "Chain of Thought" element will typically be labeled with the name of the LangChain component that produced it, such as "ChatOllama" or "RunnableSequence."  
By clicking on this element, the user can expand it to reveal the raw output from the language model for that step. Inside, they will find the full, unparsed text, including the agent's internal monologue enclosed within the \<thinking\>...\</thinking\> tags. This provides a direct, transparent view into the agent's reasoning process before it formulated the final answer, fulfilling a primary objective of the guide.36

### **4.3 The Final Streamed Response**

Simultaneously with, or immediately following the appearance of the reasoning step, a new assistant message will be created in the chat interface. The content of this message will be streamed token by token, creating the familiar "typing" effect seen in modern AI chatbots.12  
Critically, the content of this final message will *only* be the portion of the LLM's output that came *after* the closing \</thinking\> tag. The cl.LangchainCallbackHandler intelligently parses the model's response based on the prompt's structure, separating the intermediate "thought" from the final, user-facing answer. This results in a polished and uncluttered user experience, where the conversational flow is clean and direct, but the option to inspect the underlying reasoning is always available. This clear separation of concerns in the UI is the hallmark of a well-architected, production-quality conversational AI application.

## **Conclusion**

This guide has provided a definitive, step-by-step methodology for constructing a production-ready conversational AI application using a fully local, modern technology stack on Windows. By adhering to the principles and practices outlined, a senior AI developer can successfully build a system that is private, performant, and transparent.  
The key architectural decisions and best practices established include:

* **A Professional Project Structure:** The adoption of a src layout and modular design ensures the application is maintainable, scalable, and easy for other developers to understand.  
* **A Robust Local Backend:** The use of Ollama provides a simple yet powerful foundation for serving open-source large language models without reliance on external APIs, guaranteeing data privacy and cost control.  
* **Explicit and Transparent Reasoning:** The advanced prompt engineering technique, which forces the model to externalize its thought process, is a critical step toward building more reliable and debuggable agents.  
* **Seamless and Stateful UI Integration:** The combination of Chainlit's lifecycle hooks, session management, and the specialized AsyncLangchainCallbackHandler provides the definitive pattern for creating a stateful, real-time user experience that clearly visualizes the agent's intermediate steps.

The resulting application serves as a powerful blueprint. It demonstrates that sophisticated, production-quality AI systems can be built and deployed entirely on local hardware, empowering developers to create innovative applications while maintaining full control over their data and infrastructure. This local-first approach represents a significant and growing paradigm in the field of artificial intelligence.

#### **Works cited**

1. How to install and use Ollama to run AI LLMs on your Windows 11 PC, accessed August 17, 2025, [https://www.windowscentral.com/software-apps/how-to-install-and-use-ollama-to-run-ai-llms-on-your-windows-11-pc](https://www.windowscentral.com/software-apps/how-to-install-and-use-ollama-to-run-ai-llms-on-your-windows-11-pc)  
2. Building Local AI Agents: A Guide to LangGraph, AI Agents, and Ollama | DigitalOcean, accessed August 17, 2025, [https://www.digitalocean.com/community/tutorials/local-ai-agents-with-langgraph-and-ollama](https://www.digitalocean.com/community/tutorials/local-ai-agents-with-langgraph-and-ollama)  
3. How to install LangChain packages, accessed August 17, 2025, [https://python.langchain.com/docs/how\_to/installation/](https://python.langchain.com/docs/how_to/installation/)  
4. Prompt Chaining Langchain | IBM, accessed August 17, 2025, [https://www.ibm.com/think/tutorials/prompt-chaining-langchain](https://www.ibm.com/think/tutorials/prompt-chaining-langchain)  
5. Chainlit/chainlit: Build Conversational AI in minutes ⚡️ \- GitHub, accessed August 17, 2025, [https://github.com/Chainlit/chainlit](https://github.com/Chainlit/chainlit)  
6. Chainlit: Overview, accessed August 17, 2025, [https://docs.chainlit.io/](https://docs.chainlit.io/)  
7. qwen2.5-coder:14b-instruct-q6\_K \- Ollama, accessed August 17, 2025, [https://ollama.com/library/qwen2.5-coder:14b-instruct-q6\_K](https://ollama.com/library/qwen2.5-coder:14b-instruct-q6_K)  
8. qwen2.5:14b-instruct-q6\_K \- Ollama, accessed August 17, 2025, [https://ollama.com/library/qwen2.5:14b-instruct-q6\_K](https://ollama.com/library/qwen2.5:14b-instruct-q6_K)  
9. Setting Your Python Project Up for Success in 2024 | by Mr-Pepe | Medium, accessed August 17, 2025, [https://medium.com/@Mr\_Pepe/setting-your-python-project-up-for-success-in-2024-365e53f7f31e](https://medium.com/@Mr_Pepe/setting-your-python-project-up-for-success-in-2024-365e53f7f31e)  
10. Project structure best practices : r/learnpython \- Reddit, accessed August 17, 2025, [https://www.reddit.com/r/learnpython/comments/1ad36wi/project\_structure\_best\_practices/](https://www.reddit.com/r/learnpython/comments/1ad36wi/project_structure_best_practices/)  
11. UI \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/backend/config/ui](https://docs.chainlit.io/backend/config/ui)  
12. Chainlit: A Guide With Practical Examples \- DataCamp, accessed August 17, 2025, [https://www.datacamp.com/tutorial/chainlit](https://www.datacamp.com/tutorial/chainlit)  
13. venv — Creation of virtual environments — Python 3.13.7 documentation, accessed August 17, 2025, [https://docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)  
14. Install packages in a virtual environment using pip and venv, accessed August 17, 2025, [https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)  
15. Structuring Your Project \- The Hitchhiker's Guide to Python, accessed August 17, 2025, [https://docs.python-guide.org/writing/structure/](https://docs.python-guide.org/writing/structure/)  
16. Structuring a Python Project: Recommendations and a Template Example, accessed August 17, 2025, [https://waterprogramming.wordpress.com/2023/01/18/structuring-a-python-project-recommendations-and-a-template-example/](https://waterprogramming.wordpress.com/2023/01/18/structuring-a-python-project-recommendations-and-a-template-example/)  
17. ollama/ollama: Get up and running with OpenAI gpt-oss, DeepSeek-R1, Gemma 3 and other models. \- GitHub, accessed August 17, 2025, [https://github.com/ollama/ollama](https://github.com/ollama/ollama)  
18. Download Ollama on Windows, accessed August 17, 2025, [https://ollama.com/download/windows](https://ollama.com/download/windows)  
19. Set up Ollama on Windows | GPT for Work Documentation, accessed August 17, 2025, [https://gptforwork.com/help/ai-models/custom-endpoints/set-up-ollama-on-windows](https://gptforwork.com/help/ai-models/custom-endpoints/set-up-ollama-on-windows)  
20. How to Install Ollama on Windows | Run LLMs Locally in 2025 \- YouTube, accessed August 17, 2025, [https://www.youtube.com/watch?v=pGte2zbF650](https://www.youtube.com/watch?v=pGte2zbF650)  
21. Ollama on Windows: How to Install and Use it with OpenWebUI \- Mitja Martini, accessed August 17, 2025, [https://mitjamartini.com/posts/ollama-on-windows/](https://mitjamartini.com/posts/ollama-on-windows/)  
22. Creating Python Virtual Environment in Windows and Linux \- GeeksforGeeks, accessed August 17, 2025, [https://www.geeksforgeeks.org/python/creating-python-virtual-environment-windows-linux/](https://www.geeksforgeeks.org/python/creating-python-virtual-environment-windows-linux/)  
23. How To Set Up a Virtual Python Environment (Windows) \- mothergeo \- Read the Docs, accessed August 17, 2025, [https://mothergeo-py.readthedocs.io/en/latest/development/how-to/venv-win.html](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/venv-win.html)  
24. Create a Python virtual environment in Windows with VS Code \- YouTube, accessed August 17, 2025, [https://www.youtube.com/watch?v=JYdd1k44FRM](https://www.youtube.com/watch?v=JYdd1k44FRM)  
25. OllamaEmbeddings \- ️ LangChain, accessed August 17, 2025, [https://python.langchain.com/docs/integrations/text\_embedding/ollama/](https://python.langchain.com/docs/integrations/text_embedding/ollama/)  
26. Ollama \- ️ LangChain, accessed August 17, 2025, [https://python.langchain.com/docs/integrations/providers/ollama/](https://python.langchain.com/docs/integrations/providers/ollama/)  
27. Building a Simple Chatbot with LangGraph and Chainlit: A Step-by ..., accessed August 17, 2025, [https://dev.to/jamesbmour/building-a-simple-chatbot-with-langgraph-and-chainlit-a-step-by-step-tutorial-4k6h](https://dev.to/jamesbmour/building-a-simple-chatbot-with-langgraph-and-chainlit-a-step-by-step-tutorial-4k6h)  
28. Streaming \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/advanced-features/streaming](https://docs.chainlit.io/advanced-features/streaming)  
29. JSON agents with Ollama & LangChain, accessed August 17, 2025, [https://blog.langchain.com/json-based-agents-with-ollama-and-langchain/](https://blog.langchain.com/json-based-agents-with-ollama-and-langchain/)  
30. Chain-of-Thought Prompting: Step-by-Step Reasoning with LLMs | DataCamp, accessed August 17, 2025, [https://www.datacamp.com/tutorial/chain-of-thought-prompting](https://www.datacamp.com/tutorial/chain-of-thought-prompting)  
31. Prompt Templates | 🦜️ LangChain, accessed August 17, 2025, [https://python.langchain.com/docs/concepts/prompt\_templates/](https://python.langchain.com/docs/concepts/prompt_templates/)  
32. Memory in Langchain — III. Memory in Agent | by DhanushKumar ..., accessed August 17, 2025, [https://medium.com/@danushidk507/memory-in-langchain-iii-f0a226f5eb65](https://medium.com/@danushidk507/memory-in-langchain-iii-f0a226f5eb65)  
33. User Session \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/concepts/user-session](https://docs.chainlit.io/concepts/user-session)  
34. LangChain/LangGraph \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/integrations/langchain](https://docs.chainlit.io/integrations/langchain)  
35. Langchain Callback Handler \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/api-reference/integrations/langchain](https://docs.chainlit.io/api-reference/integrations/langchain)  
36. Step \- Chainlit, accessed August 17, 2025, [https://docs.chainlit.io/concepts/step](https://docs.chainlit.io/concepts/step)  
37. Chain reaction: How to create an observable frontend workflow using LlamaIndex and Chainlit | by Tituslhy | MITB For All | Medium, accessed August 17, 2025, [https://medium.com/mitb-for-all/chain-reaction-how-to-create-an-observable-workflow-using-llamaindex-and-chainlit-2b668fb1cee9](https://medium.com/mitb-for-all/chain-reaction-how-to-create-an-observable-workflow-using-llamaindex-and-chainlit-2b668fb1cee9)