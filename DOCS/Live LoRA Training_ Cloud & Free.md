

# **An Architectural Analysis of Continuous LoRA Adaptation for Agentic Workflows**

## **Executive Summary**

This report provides an exhaustive technical analysis of implementing a continuous, or "live," Low-Rank Adaptation (LoRA) training system for a qwen3:14b large language model (LLM). The proposed architecture involves serving the model via Ollama and orchestrating the learning loop with LangGraph's StateGraph. The investigation critically evaluates the feasibility of this stack on both local hardware and free-tier cloud platforms, addressing core questions of dynamic adapter management, computational overhead, and system integration.

The analysis concludes that while Ollama is an excellent tool for simplified local model deployment, its underlying architecture, which relies on llama.cpp's static merging of LoRA adapters, renders it unsuitable for a live, continuous learning workflow that requires dynamic adapter swapping without service interruption. Each update would necessitate a full model rebuild and restart, introducing significant downtime.

Consequently, this report proposes and details a superior, alternative architecture. The recommended solution utilizes a hybrid infrastructure model: a persistent, high-performance inference server for real-time agent responses, coupled with an ephemeral, free-tier cloud environment for asynchronous, periodic LoRA training. The optimal technology stack is identified as:

* **Model Serving:** **vLLM** is recommended for its high-throughput performance and, crucially, its native support for dynamic, API-driven loading and unloading of LoRA adapters at runtime.  
* **Orchestration:** **LangGraph** remains the central component, managing the agent's state, orchestrating the feedback loop, and interacting with both the vLLM server and the training pipeline.  
* **Training Pipeline:** An asynchronous training script leveraging **Unsloth** is essential for accelerating the fine-tuning process, making it feasible on consumer-grade hardware or within the constraints of free cloud platforms.  
* **Infrastructure:** For local deployment, a GPU with at least 16-24 GB of VRAM is required. For a cost-free approach, **Kaggle Notebooks** are identified as the most suitable platform for the training component due to their generous and predictable weekly GPU quotas, while the inference server would run locally.

The report provides a detailed implementation blueprint, including system diagrams, comparative analyses of technologies, hardware requirement breakdowns, and a strategic roadmap for building a robust, efficient, and continuously learning AI agent.

## **1\. Analysis of Ollama's Capabilities for Dynamic LoRA Adaptation**

The initial query centers on the viability of using Ollama as the serving layer for a system requiring live LoRA training and real-time adapter application. A thorough examination of Ollama's architecture and its dependencies reveals fundamental limitations that make it unsuitable for this specific, dynamic use case.

### **1.1. Current State of LoRA Support in Ollama**

Ollama has gained significant popularity by simplifying the process of running LLMs on local hardware.1 Its primary mechanism for model customization is the

Modelfile, a configuration file that acts as a blueprint for creating a new model instance.1 Within this system, Ollama does provide support for LoRA adapters. This is implemented via the

ADAPTER instruction in the Modelfile.4

The workflow is as follows: a user specifies a base model using the FROM instruction and then provides a path to a LoRA adapter file with the ADAPTER instruction. When the ollama create command is executed, Ollama applies the adapter to the base model, resulting in a new, self-contained model that can be run with ollama run.5 This process is effective for creating a permanently specialized model but is inherently static. The application of the adapter is a build-time operation, not a runtime one.

### **1.2. The Architectural Bottleneck: llama.cpp and Static Merging**

The root of Ollama's limitation lies in its backend dependency, llama.cpp, which serves as the inference engine for CPU and many non-NVIDIA GPU environments.1 The design philosophy of

llama.cpp regarding LoRA adapters is based on *merging*, not dynamic loading. When an adapter is applied, its weights (A and B matrices) are mathematically combined with the base model's original weight matrices (W0​) to produce a new set of weights (W′=W0​+BA). This process modifies the model's weights directly in memory.7

This architectural choice has a critical consequence: the operation is destructive to the base model's state in memory. To switch to a different LoRA adapter or revert to the base model, the entire original model must be reloaded from disk to overwrite the modified weights. The official documentation for the llama\_model\_apply\_lora\_from\_file() function in llama.cpp explicitly confirms this behavior, stating: "The model needs to be reloaded before applying a new adapter, otherwise the adapter will be applied on top of the previous one".7 This layering effect means that without a reload, subsequent adapters would be merged with an already-modified model, leading to unpredictable and incorrect behavior. This static, build-time merging is fundamentally incompatible with the concept of "hot-swapping" or live adapter switching.

### **1.3. Performance Implications of Adapter Merging in llama.cpp**

The static merging process in llama.cpp not only prevents dynamic application but also introduces a significant performance penalty during model loading. User reports and technical analysis indicate that loading a 13B parameter model with a LoRA adapter can take over 60 seconds, a stark contrast to the 2 seconds required to load the base model alone.7

This extreme latency is a direct result of the merging process necessitating the disabling of mmap (memory mapping). mmap is a crucial performance optimization that allows an operating system to map a file's contents directly into the process's virtual address space, avoiding the need to read the entire file into RAM. Model loading becomes exceptionally fast as pages are loaded from disk only when accessed. However, because the LoRA merging process modifies the model's weights, a mutable copy of the model must be created in memory, making mmap unusable. The system is forced to load the entire multi-gigabyte model file into RAM, causing the observed dramatic increase in load times.7

### **1.4. Current Development and Community Feature Requests**

The limitations of Ollama's current LoRA implementation are well-recognized within its user community. A review of open issues on Ollama's GitHub repository reveals multiple feature requests for dynamic adapter loading, hot-swapping, and per-request adapter specification.8 These requests frequently point to the fact that other serving frameworks, and even

llama.cpp itself, are evolving to support these more advanced use cases. Indeed, recent developments in llama.cpp have introduced experimental server endpoints for hot-swapping adapters, indicating a potential future path for Ollama.8

However, Ollama's adoption of these features is further complicated by the ongoing transition in adapter file formats. Ollama's current implementation relies on the older GGML/GGLA (GGUF-based LoRA Adapter) format.4 The broader ecosystem, including

llama.cpp, is standardizing on the more versatile GGUF format for both models and adapters.9 This format mismatch creates an additional layer of technical debt that must be resolved before more dynamic features can be robustly implemented and supported within Ollama.

### **1.5. Verdict: Suitability for Continuous Learning Workflows**

Based on this comprehensive analysis, **Ollama is architecturally unsuitable for a continuous learning workflow that requires live, real-time application of LoRA adapters.** The core design, inherited from llama.cpp, treats adapter application as a static, build-time event that creates a new, immutable model. Every "live" update would necessitate:

1. Stopping the currently running Ollama model.  
2. Modifying the Modelfile to point to the new adapter.  
3. Executing ollama create to build a new model, a process that can take over a minute.  
4. Starting the new model.

This sequence introduces significant downtime and operational friction, defeating the purpose of a "live" system. The user's goal requires a serving framework designed for dynamic, multi-tenant environments, a paradigm that is fundamentally different from Ollama's focus on simplicity and ease of local deployment. The investigation must therefore pivot from attempting to force a solution with an inappropriate tool to identifying the correct architecture and technology stack for the task.

## **2\. The LoRA Training Workflow for qwen3:14b**

The concept of "live" or "continuous" training in the context of production LLM systems does not imply online learning where model weights are updated during an inference request. Such an approach would be computationally prohibitive and would introduce unpredictable latency. Instead, a continuous learning loop is implemented as a robust, asynchronous pipeline that decouples the resource-intensive training process from the low-latency inference server.

### **2.1. Defining "Continuous Training" as an Asynchronous Pipeline**

A practical continuous learning system operates on an event-driven, asynchronous model. The workflow can be broken down into a distinct cycle:

1. **Interaction & Data Capture:** The agent, running on the inference server, interacts with a user or environment. Based on this interaction, a feedback mechanism identifies a new piece of information to be learned (e.g., a user correction, a new document, a failed task).  
2. **Training Job Trigger:** The captured data is formatted into a training example and an asynchronous training job is initiated. This is typically done via an API call to a separate training orchestrator or job queue.  
3. **Asynchronous Training:** A dedicated training process, running on separate hardware, fine-tunes a new LoRA adapter using the new data. This process runs in the background and does not impact the live inference server.10  
4. **Adapter Deployment:** Once training is complete, the newly created LoRA adapter file is saved to a shared location (e.g., a local volume, cloud storage).  
5. **Live Application:** The inference server is notified of the new adapter and loads it into memory, making it available for subsequent requests without a service restart.

This separation of concerns is paramount for system stability. It ensures that the inference server remains responsive and available while the computationally demanding training occurs independently.

### **2.2. Accelerating Training with Unsloth: A Practical Necessity**

Fine-tuning a 14-billion-parameter model, even with the efficiencies of LoRA, remains a significant computational task. Unsloth has emerged as a critical library for making such tasks feasible on accessible hardware. It provides a highly optimized training backend that can be used as a drop-in replacement for standard Hugging Face pipelines.11

Unsloth's key advantages stem from several low-level optimizations, including custom Triton kernels for attention and RoPE embeddings, intelligent memory management, and re-engineered backpropagation paths. The result is a dramatic improvement in efficiency: Unsloth can fine-tune models up to **2-3 times faster** while using up to **70% less VRAM** compared to conventional methods.12 This level of optimization is what brings the QLoRA (Quantized LoRA) fine-tuning of a model like

qwen3:14b within the reach of a single consumer-grade GPU.13

### **2.3. Dataset Preparation and Hyperparameter Tuning**

The efficacy of a LoRA adapter is directly tied to the quality of the fine-tuning data and the choice of hyperparameters. For instruction-following models like Qwen3, data is typically formatted in a conversational or chat-based structure, often using JSONL, where each line represents a dialogue turn.15

Several key hyperparameters govern the LoRA training process:

* **r (Rank):** This parameter defines the rank (and thus, the size) of the low-rank matrices A and B. It directly controls the number of trainable parameters and the adapter's capacity to learn new information. A higher rank allows for more complex adaptations but increases memory usage and training time. Common suggested values range from 8 to 128, with 16 or 32 being typical starting points.17  
* **lora\_alpha:** This is a scaling factor applied to the LoRA weights. It helps to balance the influence of the adapter against the base model. A widely adopted and effective heuristic is to set lora\_alpha to be equal to or double the rank (r).17  
* **target\_modules:** This specifies which layers of the transformer architecture will have LoRA matrices injected. While early approaches targeted only attention layers (q\_proj, v\_proj), the original QLoRA paper and subsequent research have shown that targeting all linear layers (q\_proj, k\_proj, v\_proj, o\_proj, gate\_proj, up\_proj, down\_proj) yields the best performance, more closely emulating a full fine-tune.17

### **2.4. Benchmarking LoRA Training: Time and Resource Consumption**

Providing a precise training time is dependent on dataset size, sequence length, and hardware. However, by synthesizing data from various user reports and benchmarks, we can establish realistic estimates.

For a 13B or 14B parameter model, a comprehensive fine-tuning run (e.g., 3 epochs on a dataset of \~50,000 samples) using QLoRA on a single 24 GB VRAM GPU (like an NVIDIA RTX 3090 or 4090\) typically takes approximately **9 to 12 hours**.22

For the purposes of a continuous learning loop, where each training job might only involve a few hundred or a few thousand new examples, the training time would be substantially shorter. With a smaller dataset of \~2,000 examples, training time can decrease to **2-3 hours**.24 For micro-updates involving just a few dozen new data points, a training run could potentially complete in under an hour, making a daily or even hourly update cycle feasible.

The VRAM requirements are the most critical hardware constraint. The following table illustrates the dramatic memory savings achieved by PEFT methods, making this entire endeavor possible on non-enterprise hardware.

| Fine-Tuning Method | Precision | VRAM Requirement (13B/14B Model) | Notes |
| :---- | :---- | :---- | :---- |
| Full Fine-Tuning | 16-bit | \>320 GB | Requires a multi-GPU server with 8x A100s or similar; computationally prohibitive for most users. |
| LoRA | 16-bit | \~32 GB | Feasible on a single high-end GPU like an A6000 (48GB) or potentially two 24GB GPUs. |
| QLoRA (bitsandbytes) | 8-bit | \~16 GB | Brings training into the range of a single 24GB consumer GPU. |
| QLoRA (bitsandbytes) | 4-bit | \~10 GB | Highly efficient; can run on GPUs with as little as 12GB of VRAM, albeit with smaller batch sizes. |

Data synthesized from sources.25

## **3\. Infrastructure Analysis: Local Hardware vs. Free Cloud Platforms**

The proposed hybrid architecture necessitates a clear understanding of the infrastructure required for both the persistent inference server and the ephemeral training jobs. This section details the hardware specifications for local deployment and provides a comparative analysis of free-tier cloud platforms for offloading the training workload.

### **3.1. Local Deployment: Hardware Requirements**

A local deployment requires a machine capable of handling both serving and, potentially, training. These two tasks have distinct resource profiles.

* **Training Infrastructure:** As established in Section 2, the primary requirement for training is GPU VRAM. To comfortably fine-tune a qwen3:14b model using Unsloth with QLoRA, a local machine should be equipped with an NVIDIA GPU possessing at least **16 GB of VRAM**. A GPU with **24 GB of VRAM** (e.g., NVIDIA RTX 3090, RTX 4090\) is highly recommended, as it allows for larger batch sizes and sequence lengths, leading to faster and more stable training.23  
* **Serving Infrastructure:** The inference server must hold the base model in memory. A 4-bit quantized GGUF version of a 14B model, such as the Q4\_K\_M quant, is approximately 9 GB in size.14 To run this model with good performance, it should be fully offloaded to the GPU. Therefore, the serving component requires a GPU with at least  
  **12 GB of VRAM**. Additionally, the system needs sufficient system RAM (a minimum of 16 GB, with 32 GB recommended) to handle the operating system, the serving framework (e.g., vLLM), and data processing tasks.1

A single machine with a 24 GB GPU can fulfill both roles, but not simultaneously without careful resource management. The optimal local setup involves separate machines or a robust scheduling system to ensure the training process does not disrupt the availability of the inference server.

### **3.2. Evaluating Free-Tier Cloud Options for Asynchronous Training**

For users without access to powerful local hardware, offloading the training process to free cloud notebook environments is a viable and cost-effective strategy. The key is to find a platform with a predictable and sufficiently generous GPU quota to accommodate periodic training runs.

* **Google Colab:**  
  * **Hardware:** The free tier of Google Colab offers access to NVIDIA T4 GPUs, which have **16 GB of VRAM**—sufficient for QLoRA fine-tuning.28  
  * **Limitations:** Colab's primary drawback is its highly unpredictable and opaque resource limits. Free-tier GPU sessions can be terminated after as little as 3 hours, and heavy usage can lead to users being temporarily locked out of GPU access for hours or even days.30 This lack of reliability makes Colab unsuitable for a scheduled, automated, continuous training workflow. It is best suited for interactive, ad-hoc experimentation.  
* **Kaggle Notebooks:**  
  * **Hardware:** Kaggle provides free access to NVIDIA P100 GPUs, which also come with **16 GB of VRAM**.33  
  * **Advantages:** Kaggle's key advantage is its generous and transparent quota system. Users are allocated **30 hours of GPU usage per week**, with this quota resetting every Saturday at midnight UTC.34 Individual notebook sessions can run for up to  
    **9 hours** continuously. This predictable and substantial allocation is more than sufficient to run daily or weekly LoRA training jobs, which, as estimated, may only take a few hours each. This makes Kaggle the superior choice for the asynchronous training component of the proposed architecture.  
* **Hugging Face Spaces:**  
  * **Hardware:** The standard free tier for Hugging Face Spaces provides a CPU-only environment (typically 2 vCPUs and 16 GB of RAM).36 This is completely inadequate for fine-tuning a 14B model and is even slow for serving it.  
  * **GPU Options:** While paid GPU upgrades and a "ZeroGPU" option for PRO users exist, they are designed for hosting interactive demos, not for running background training jobs, and are not part of the free offering.38

The analysis clearly indicates that a hybrid architecture is the most practical and resource-efficient solution. A persistent inference server, whether running on a local machine or a low-cost paid cloud instance, ensures 24/7 availability for the LangGraph agent. The non-time-critical, but resource-intensive, training jobs can then be offloaded to an ephemeral, free platform like Kaggle, which provides the necessary GPU power in predictable, scheduled bursts without any monetary cost.

### **Table 1: Comparison of Free Cloud GPU Platforms for LoRA Training**

| Platform | GPU Type / VRAM | Session Length Limit | Weekly Quota | Reliability & Predictability | Suitability for Continuous Workflow |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Google Colab (Free)** | NVIDIA T4 / 16 GB | Dynamic (3-6 hours) | Not specified | Low; opaque usage limits | Poor |
| **Kaggle Notebooks** | NVIDIA P100 / 16 GB | 9 hours | **30 hours** | **High; transparent quota** | **Excellent** |
| **Hugging Face (Free)** | CPU Only | N/A | N/A | N/A | Unsuitable |

## **4\. High-Performance Serving Architectures for Dynamic LoRA**

Given that Ollama's static architecture is ill-suited for the task, the focus shifts to alternative serving frameworks designed specifically for high-performance, dynamic, and multi-tenant LLM inference. The ability to manage LoRA adapters at runtime is a key differentiator for these production-grade systems.

### **4.1. Introduction to Dynamic, Per-Request Adapter Serving**

The state-of-the-art approach for serving multiple specialized models efficiently is known as multi-LoRA serving. This paradigm involves loading a single, shared base model into GPU memory one time. Then, multiple lightweight LoRA adapters can be loaded and applied dynamically on a per-request basis.39

This method offers tremendous operational and cost efficiency. Instead of deploying dozens of full-sized models, each consuming significant VRAM, a single GPU can host one base model and serve hundreds of specialized "virtual" models by swapping in the appropriate tiny LoRA adapter for each incoming request.42 This is the core technology that enables the "live" aspect of the proposed continuous learning system.

### **4.2. Deep Dive: vLLM for Real-Time LoRA Management**

vLLM is an open-source library from UC Berkeley that has become a leading solution for high-throughput LLM serving. Its primary innovation is **PagedAttention**, an algorithm that manages the memory for attention keys and values with virtual memory concepts, dramatically reducing memory waste and enabling much higher batch sizes.2

For the purposes of this report, vLLM's most critical feature is its native support for dynamic LoRA adapter management. vLLM can be launched with LoRA support enabled, and it exposes an OpenAI-compatible API server with specific endpoints for managing adapters at runtime.45

To enable this, the server must be started with the environment variable VLLM\_ALLOW\_RUNTIME\_LORA\_UPDATING set to True.45 Once running, adapters can be managed via HTTP requests:

* **Load an Adapter:** A POST request to the /v1/load\_lora\_adapter endpoint loads a new adapter into the server's memory, making it available for inference.  
  Bash  
  curl \-X POST http://localhost:8000/v1/load\_lora\_adapter \\  
  \-H "Content-Type: application/json" \\  
  \-d '{  
   "lora\_name": "newly\_trained\_adapter\_v1",  
   "lora\_path": "/path/to/adapters/adapter\_v1"  
  }'

* **Unload an Adapter:** A POST request to /v1/unload\_lora\_adapter removes an adapter from memory.  
  Bash  
  curl \-X POST http://localhost:8000/v1/unload\_lora\_adapter \\  
  \-H "Content-Type: application/json" \\  
  \-d '{ "lora\_name": "old\_adapter\_to\_remove" }'

This API provides the essential mechanism for the LangGraph agent to programmatically update the serving engine with newly trained adapters without any downtime or server restarts.45

### **4.3. Deep Dive: Hugging Face Text Generation Inference (TGI)**

Text Generation Inference (TGI) is Hugging Face's own production-grade solution for serving LLMs.47 It is a highly robust and feature-rich server that also supports multi-LoRA serving.49

TGI's primary method for managing LoRA adapters is to specify them at server startup. This is done by passing a list of adapter paths or Hugging Face Hub IDs via a command-line argument (--lora-modules) or an environment variable (LORA\_ADAPTERS).41 When an inference request is made, the client can specify which of these pre-loaded adapters to use via an

adapter\_id parameter in the request payload.49

While this is highly efficient for serving a known, static set of adapters, it is less flexible than vLLM for a continuous learning workflow where new adapters are being generated frequently. Loading a new adapter with TGI would typically require a server restart to update the initial configuration.

### **4.4. Comparative Analysis and Recommendation**

When evaluated against the specific requirements of a continuous learning loop, vLLM emerges as the superior choice. While both vLLM and TGI are powerful, production-ready servers, vLLM's dedicated runtime API for adapter management is the decisive feature. This API provides the necessary programmatic control to truly "close the loop" between training and inference without manual intervention or service disruption. Furthermore, many benchmarks indicate that vLLM often has a performance edge in terms of throughput, though TGI has shown exceptional performance with very long contexts.44

### **Table 2: Feature Comparison of Model Serving Frameworks**

| Feature | Ollama | vLLM | TGI (Text Generation Inference) |
| :---- | :---- | :---- | :---- |
| **Base Technology** | llama.cpp | Custom CUDA Kernels, PagedAttention | Custom Rust/Python server, FlashAttention |
| **Dynamic Adapter Loading (API)** | **No** | **Yes** (/v1/load\_lora\_adapter) | **No** (Adapters loaded at startup) |
| **Per-Request Adapter Switching** | No (Model is pre-merged) | Yes (via model or lora\_request parameter) | Yes (via adapter\_id parameter) |
| **Performance Optimizations** | GGUF Quantization | PagedAttention, Continuous Batching, Quantization (AWQ, GPTQ) | Continuous Batching, Quantization, FlashAttention |
| **OpenAI-Compatible API** | Yes | Yes | Yes |
| **Ease of Setup** | Very Easy | Moderate (Requires Python environment) | Moderate (Typically run via Docker) |
| **Suitability for Continuous Learning** | **Unsuitable** | **Excellent** | **Limited** |

## **5\. Architecting a Continuous Learning Loop with LangGraph**

With the optimal components for serving (vLLM) and training (Unsloth) identified, LangGraph serves as the intelligent orchestrator, connecting these components and managing the entire agentic feedback and learning workflow. Its ability to define stateful, cyclical graphs makes it perfectly suited for this task.

### **5.1. Designing the Agentic Feedback Mechanism in StateGraph**

LangGraph's core abstraction is the StateGraph, which represents a workflow as a set of nodes (functions) and edges (control flow) that operate on a shared state object.51 For our continuous learning system, the state will contain not just the conversation history, but also metadata related to the learning process, such as the ID of the currently active LoRA adapter and the status of any ongoing training jobs.

A robust graph for this workflow would include the following key nodes:

1. **agent\_inference:** This is the primary interaction node. It receives user input, queries the vLLM server using the currently active LoRA adapter, and generates a response.  
2. **feedback\_detection (Conditional Edge):** This node acts as a router. It inspects the agent's output and the user's subsequent input to determine if a learning opportunity exists. This could be triggered by an explicit user command (e.g., "\!learn this fact") or by an implicit signal, such as the agent repeatedly failing to answer a question correctly. Based on its analysis, it routes the flow to either continue the conversation or initiate the training pipeline.  
3. **data\_curation:** If training is triggered, this node is responsible for extracting the relevant information from the conversation history and formatting it into a structured training example (e.g., a single-line JSON object) that the training script can consume.  
4. **trigger\_training:** This is a tool-calling node. It makes an API call to an external, simple webhook or a more robust job queue system (like Celery) to start the asynchronous LoRA training job on the designated training infrastructure (e.g., a local machine or a Kaggle Notebook). It passes the curated data as part of the request.  
5. **monitor\_training:** This node can be used to periodically poll the status of the training job, providing feedback to the user or system administrator.  
6. **deploy\_adapter:** Upon receiving confirmation that the training job has successfully completed, this node executes a tool that makes a POST request to the vLLM server's /v1/load\_lora\_adapter endpoint. This action makes the newly trained adapter available for inference, effectively closing the learning loop.

### **5.2. Integrating LangGraph with a vLLM-Powered Serving Endpoint**

LangGraph integrates seamlessly with any LLM that exposes an OpenAI-compatible API.53 The integration with vLLM is therefore straightforward. A

ChatOpenAI client from the langchain\_openai library is initialized, pointing to the local vLLM server's URL (e.g., http://localhost:8000/v1).55

A critical aspect of this integration is the ability to switch LoRA adapters on a per-request basis. When invoking the LLM, the model parameter in the API call is used to specify the ID of the desired LoRA adapter. vLLM will then dynamically apply this adapter for that specific generation request.49

Python

from langchain\_openai import ChatOpenAI  
from langgraph.graph import StateGraph, END  
from typing import TypedDict, Annotated  
import operator

\# Define the state for our graph  
class AgentState(TypedDict):  
    messages: Annotated\[list, operator.add\]  
    active\_adapter: str

\# Initialize the LLM client to point to the vLLM server  
vllm\_client \= ChatOpenAI(  
    model="base\_model\_name", \# This can be a placeholder  
    openai\_api\_key="EMPTY",  
    openai\_api\_base="http://localhost:8000/v1",  
    temperature=0.7  
)

\# A node in the LangGraph  
def agent\_inference(state: AgentState):  
    \# Dynamically specify the LoRA adapter for this specific call  
    adapter\_id \= state.get("active\_adapter", "base\_model\_name")  
    response \= vllm\_client.invoke(  
        state\["messages"\],  
        model=adapter\_id \# This tells vLLM which adapter to use  
    )  
    return {"messages": \[response\]}

\#... graph definition would follow...

### **5.3. State Management and Human-in-the-Loop**

LangGraph's built-in persistence capabilities are essential for a long-running agent. By configuring a checkpointer (e.g., MemorySaver), the state of the graph can be automatically saved after each step. This allows the workflow to be paused and resumed, which is critical for incorporating human oversight.58

A crucial design pattern for this system is to add a human-in-the-loop checkpoint. Before the trigger\_training node is executed, the graph can be configured to pause using an interrupt. This allows a human operator to review the curated training data and either approve or reject the training job, preventing the agent from learning from incorrect or malicious feedback.60

### **5.4. Architectural Blueprint: A Complete End-to-End System Diagram**

The complete system architecture integrates these components into a cohesive, continuous learning loop. The workflow is visualized as follows:

1. **User Interface:** A user interacts with the application front-end.  
2. **LangGraph Orchestrator:** This is the central application logic. It manages the agent's state and orchestrates the entire workflow.  
3. **Inference Flow (Real-time):**  
   * The LangGraph agent sends an inference request to the vLLM Server. The request specifies which LoRA adapter to use.  
   * The vLLM Server, running on a persistent local or cloud GPU, processes the request using the base qwen3:14b model and the specified adapter.  
   * The response is returned to the LangGraph agent and then to the user.  
4. **Learning Flow (Asynchronous):**  
   * The LangGraph agent's feedback\_detection node identifies a learning opportunity.  
   * The data\_curation node prepares a training sample.  
   * (Optional) The graph pauses for human-in-the-loop approval.  
   * The trigger\_training node sends an API request to a Training Orchestrator (e.g., a simple FastAPI server).  
   * The Training Orchestrator launches a training job on the Training Infrastructure (e.g., a Kaggle Notebook via its API, or a local script).  
   * The training script uses Unsloth to fine-tune a new LoRA adapter.  
   * The completed adapter file is saved to a Shared Storage volume accessible by the vLLM server.  
5. **Deployment Flow (Live Update):**  
   * The training script, upon completion, notifies the Training Orchestrator.  
   * The Training Orchestrator sends a POST request to the vLLM Server's /v1/load\_lora\_adapter endpoint, providing the name and path of the new adapter.  
   * The vLLM server loads the adapter into memory, making it immediately available for future inference requests without any downtime.

## **6\. Strategic Recommendations and Implementation Roadmap**

This final section synthesizes the report's findings into a set of actionable recommendations and provides a clear path for implementing the proposed continuous learning system.

### **6.1. Final Recommendation on the Optimal Technology Stack**

Based on the detailed analysis, the following technology stack is recommended to achieve the user's goal of a live, continuously learning agentic system:

* **Model Serving:** **vLLM**. Its high-performance inference engine and, most critically, its runtime API for dynamic LoRA adapter management make it the only suitable choice among the evaluated options for a truly live system.  
* **Model:** **qwen3:14b**. As requested by the user, this model provides a strong balance of performance and size. A GGUF-quantized version should be used for the base model to optimize memory usage.  
* **Training Framework:** **Unsloth \+ Hugging Face trl**. Unsloth's optimizations are essential for making the fine-tuning process fast and resource-efficient enough to be practical on accessible hardware.  
* **Training Infrastructure:**  
  * **Local Option:** A dedicated machine with an NVIDIA GPU containing at least 24 GB of VRAM.  
  * **Free Cloud Option:** **Kaggle Notebooks**, leveraged via its API to run scheduled, asynchronous training jobs, taking advantage of the predictable 30-hour weekly GPU quota.  
* **Orchestration:** **LangGraph StateGraph**. Its powerful state management, control flow capabilities, and human-in-the-loop features make it the ideal framework for orchestrating the complex, cyclical workflow of the learning loop.

### **6.2. Step-by-Step Implementation Guide**

A high-level roadmap for building the system is as follows:

1. **Setup the Serving Environment:** Install vLLM and its dependencies. Start the vLLM OpenAI-compatible server, loading the base qwen3:14b model and ensuring LoRA support is enabled (--enable-lora) and the dynamic update environment variable is set.  
2. **Develop the Training Pipeline:** Create a Python script that uses the Unsloth library and Hugging Face's trl.SFTTrainer to perform QLoRA fine-tuning. This script should be parameterized to accept a dataset path and an output path for the trained adapter.  
3. **Build a Training Trigger API:** Implement a simple API endpoint (e.g., using FastAPI) that can receive a request with training data. This endpoint will be responsible for saving the data and invoking the training script developed in step 2\.  
4. **Design the LangGraph Agent:** Implement the StateGraph as detailed in Section 5\. Define the nodes for inference, feedback detection, data curation, and triggering/deploying adapters.  
5. **Integrate the Components:**  
   * Configure the LangGraph agent's LLM client to point to the vLLM server.  
   * Implement the trigger\_training node as a tool that calls the API from step 3\.  
   * Implement the deploy\_adapter node as a tool that calls the vLLM /v1/load\_lora\_adapter API endpoint.

### **6.3. Considerations for Production Deployment and Scalability**

While the proposed architecture is robust, moving to a full production environment would benefit from several enhancements:

* **Job Queuing:** Replace the simple training trigger API with a dedicated task queue system like Celery with a Redis or RabbitMQ broker. This provides better reliability, retry logic, and scalability for managing training jobs.  
* **Adapter Management:** Implement a more sophisticated system for versioning and managing LoRA adapters. This could involve a database that tracks adapters, their training data, and performance metrics, allowing the LangGraph agent to intelligently select or even A/B test different adapter versions.  
* **Mitigating Catastrophic Forgetting:** Continuous fine-tuning, even with LoRA, can lead to the model "forgetting" previously learned information. This is a known challenge in continual learning. Advanced techniques should be explored as the system matures, such as periodically merging successful adapters back into the base model or using synthetic replay, where the model generates data from previous tasks to include in new training runs, helping to retain knowledge.63

### **6.4. Future Outlook: The Evolution of Live Adaptation in LLMs**

The field of dynamic model adaptation is evolving rapidly. The architecture described in this report represents the current state-of-the-art for practical implementation. However, emerging research and technologies are set to make these systems even more efficient. Techniques like **LoRA-Switch** propose token-wise routing mechanisms that could further reduce the latency of applying dynamic adapters.65 It is likely that leading serving frameworks like vLLM will continue to integrate these advanced capabilities, further blurring the line between static inference and dynamic, continuous learning, and making the creation of truly adaptive AI agents more accessible than ever.

#### **Works cited**

1. How to Use Ollama (Complete Ollama Cheatsheet) \- Apidog, accessed August 23, 2025, [https://apidog.com/blog/how-to-use-ollama/](https://apidog.com/blog/how-to-use-ollama/)  
2. Ten ways to Serve Large Language Models: A Comprehensive Guide | by Gautam Chutani, accessed August 23, 2025, [https://gautam75.medium.com/ten-ways-to-serve-large-language-models-a-comprehensive-guide-292250b02c11](https://gautam75.medium.com/ten-ways-to-serve-large-language-models-a-comprehensive-guide-292250b02c11)  
3. A Comprehensive Guide to Fine-tuning Ollama Models \- Arsturn, accessed August 23, 2025, [https://www.arsturn.com/blog/how-to-fine-tune-ollama-models](https://www.arsturn.com/blog/how-to-fine-tune-ollama-models)  
4. Lora models / Lora training · Issue \#4432 · ollama/ollama \- GitHub, accessed August 23, 2025, [https://github.com/ollama/ollama/issues/4432](https://github.com/ollama/ollama/issues/4432)  
5. Use Unsloth LoRA Adapter with Ollama in 3 Steps | by Sarin Suriyakoon \- Medium, accessed August 23, 2025, [https://sarinsuriyakoon.medium.com/unsloth-lora-with-ollama-lightweight-solution-to-full-cycle-llm-development-edadb6d9e0f0](https://sarinsuriyakoon.medium.com/unsloth-lora-with-ollama-lightweight-solution-to-full-cycle-llm-development-edadb6d9e0f0)  
6. Training a model with my own data : r/LocalLLaMA \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/18mxuq0/training\_a\_model\_with\_my\_own\_data/](https://www.reddit.com/r/LocalLLaMA/comments/18mxuq0/training_a_model_with_my_own_data/)  
7. Is it possible to dynamically switch multiple LoRA adapters? · Issue \#6377 · ggml-org/llama.cpp \- GitHub, accessed August 23, 2025, [https://github.com/ggerganov/llama.cpp/issues/6377](https://github.com/ggerganov/llama.cpp/issues/6377)  
8. Support hot-swapping for LoRA adapters · Issue \#9548 \- GitHub, accessed August 23, 2025, [https://github.com/ollama/ollama/issues/9548](https://github.com/ollama/ollama/issues/9548)  
9. Support LoRA GGUF Adapters · Issue \#5788 \- GitHub, accessed August 23, 2025, [https://github.com/ollama/ollama/issues/5788](https://github.com/ollama/ollama/issues/5788)  
10. Training Models \- Getting Started, accessed August 23, 2025, [https://docs.scenario.com/docs/training-models](https://docs.scenario.com/docs/training-models)  
11. A Step-by-Step Coding Guide to Efficiently Fine-Tune Qwen3-14B Using Unsloth AI on Google Colab with Mixed Datasets and LoRA Optimization \[NOTEBOOK Included\] : r/machinelearningnews \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/machinelearningnews/comments/1kqyv05/a\_stepbystep\_coding\_guide\_to\_efficiently\_finetune/](https://www.reddit.com/r/machinelearningnews/comments/1kqyv05/a_stepbystep_coding_guide_to_efficiently_finetune/)  
12. Run & Fine-tune Qwen3 \- Unsloth AI, accessed August 23, 2025, [https://unsloth.ai/blog/qwen3](https://unsloth.ai/blog/qwen3)  
13. Qwen3: How to Run & Fine-tune | Unsloth Documentation, accessed August 23, 2025, [https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune](https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune)  
14. unsloth/Qwen3-14B-GGUF \- Hugging Face, accessed August 23, 2025, [https://huggingface.co/unsloth/Qwen3-14B-GGUF](https://huggingface.co/unsloth/Qwen3-14B-GGUF)  
15. A Step-by-Step Coding Guide to Efficiently Fine-Tune Qwen3-14B Using Unsloth AI on Google Colab with Mixed Datasets and LoRA Optimization \- MarkTechPost, accessed August 23, 2025, [https://www.marktechpost.com/2025/05/20/a-step-by-step-coding-guide-to-efficiently-fine-tune-qwen3-14b-using-unsloth-ai-on-google-colab-with-mixed-datasets-and-lora-optimization/](https://www.marktechpost.com/2025/05/20/a-step-by-step-coding-guide-to-efficiently-fine-tune-qwen3-14b-using-unsloth-ai-on-google-colab-with-mixed-datasets-and-lora-optimization/)  
16. Fine-Tuning Models with Ollama: A Comprehensive Guide \- Arsturn, accessed August 23, 2025, [https://www.arsturn.com/blog/deep-dive-fine-tuning-models-ollama](https://www.arsturn.com/blog/deep-dive-fine-tuning-models-ollama)  
17. Tutorial: How to Finetune Llama-3 and Use In Ollama | Unsloth Documentation, accessed August 23, 2025, [https://docs.unsloth.ai/basics/tutorials-how-to-fine-tune-and-run-llms/tutorial-how-to-finetune-llama-3-and-use-in-ollama](https://docs.unsloth.ai/basics/tutorials-how-to-fine-tune-and-run-llms/tutorial-how-to-finetune-llama-3-and-use-in-ollama)  
18. Fine-Tuning Qwen-2.5-Coder-14B LLM (SFT, PEFT) \- Kaggle, accessed August 23, 2025, [https://www.kaggle.com/code/ksmooi/fine-tuning-qwen-2-5-coder-14b-llm-sft-peft](https://www.kaggle.com/code/ksmooi/fine-tuning-qwen-2-5-coder-14b-llm-sft-peft)  
19. Fine-Tuning LLMs: LoRA or Full-Parameter? An in-depth Analysis with Llama 2 \- Anyscale, accessed August 23, 2025, [https://www.anyscale.com/blog/fine-tuning-llms-lora-or-full-parameter-an-in-depth-analysis-with-llama-2](https://www.anyscale.com/blog/fine-tuning-llms-lora-or-full-parameter-an-in-depth-analysis-with-llama-2)  
20. LoRA vs Full Fine-tuning: An Illusion of Equivalence \- arXiv, accessed August 23, 2025, [https://arxiv.org/html/2410.21228v2](https://arxiv.org/html/2410.21228v2)  
21. How to optimize fine-tuning of Llama-2 13B? : r/LocalLLaMA \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/18p48fc/how\_to\_optimize\_finetuning\_of\_llama2\_13b/](https://www.reddit.com/r/LocalLLaMA/comments/18p48fc/how_to_optimize_finetuning_of_llama2_13b/)  
22. LoRA fine-tuning is getting too long nowadays\! : r/LocalLLaMA \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1dn1d4b/lora\_finetuning\_is\_getting\_too\_long\_nowadays/](https://www.reddit.com/r/LocalLLaMA/comments/1dn1d4b/lora_finetuning_is_getting_too_long_nowadays/)  
23. Anyone try fine-tuning 13B model? \#28 \- tloen/alpaca-lora \- GitHub, accessed August 23, 2025, [https://github.com/tloen/alpaca-lora/issues/28](https://github.com/tloen/alpaca-lora/issues/28)  
24. How long does fine-tuning take, and how much VRAM does it use? (At different model sizes and context lengths, using the latest methods) : r/LocalLLaMA \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/15hiid1/how\_long\_does\_finetuning\_take\_and\_how\_much\_vram/](https://www.reddit.com/r/LocalLLaMA/comments/15hiid1/how_long_does_finetuning_take_and_how_much_vram/)  
25. The Complete Guide to GPU Requirements for LLM Fine-Tuning | Runpod Blog, accessed August 23, 2025, [https://www.runpod.io/blog/llm-fine-tuning-gpu-guide](https://www.runpod.io/blog/llm-fine-tuning-gpu-guide)  
26. Helpful VRAM requirement table for qlora, lora, and full finetuning. : r/LocalLLaMA \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/18o5u0k/helpful\_vram\_requirement\_table\_for\_qlora\_lora\_and/](https://www.reddit.com/r/LocalLLaMA/comments/18o5u0k/helpful_vram_requirement_table_for_qlora_lora_and/)  
27. How can I fine-tune large language models on a budget using LoRA and QLoRA on cloud GPUs? \- Runpod, accessed August 23, 2025, [https://www.runpod.io/articles/guides/how-to-fine-tune-large-language-models-on-a-budget](https://www.runpod.io/articles/guides/how-to-fine-tune-large-language-models-on-a-budget)  
28. Fine-tuning Falcon-7b-instruct using PEFT- LoRA on Free GPU | by Srishti Nagu \- Medium, accessed August 23, 2025, [https://medium.com/@srishtinagu19/fine-tuning-falcon-7b-instruct-using-peft-lora-on-free-gpu-6fa1b0fcbcb](https://medium.com/@srishtinagu19/fine-tuning-falcon-7b-instruct-using-peft-lora-on-free-gpu-6fa1b0fcbcb)  
29. Making the Most of your Colab Subscription \- Colab, accessed August 23, 2025, [https://colab.research.google.com/notebooks/pro.ipynb](https://colab.research.google.com/notebooks/pro.ipynb)  
30. Free tier GPU runtime reduced from 6 hours to 3 : r/GoogleColab \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/GoogleColab/comments/1ammpw2/free\_tier\_gpu\_runtime\_reduced\_from\_6\_hours\_to\_3/](https://www.reddit.com/r/GoogleColab/comments/1ammpw2/free_tier_gpu_runtime_reduced_from_6_hours_to_3/)  
31. Google Colab, RAM, VRAM and GPU usage limits – I – no clear conditions over multiple sessions | Linux-Blog, accessed August 23, 2025, [https://linux-blog.anracom.com/2023/05/04/google-colab-ram-vram-and-gpu-usage-limits-i-no-clear-conditions-over-multiple-sessions/](https://linux-blog.anracom.com/2023/05/04/google-colab-ram-vram-and-gpu-usage-limits-i-no-clear-conditions-over-multiple-sessions/)  
32. How long does Colab's Usage limits for GPUs lasts? : r/GoogleColab \- Reddit, accessed August 23, 2025, [https://www.reddit.com/r/GoogleColab/comments/h85qpn/how\_long\_does\_colabs\_usage\_limits\_for\_gpus\_lasts/](https://www.reddit.com/r/GoogleColab/comments/h85qpn/how_long_does_colabs_usage_limits_for_gpus_lasts/)  
33. blog.paperspace.com, accessed August 23, 2025, [https://blog.paperspace.com/gradient-kaggle-notebook-comparison/](https://blog.paperspace.com/gradient-kaggle-notebook-comparison/)  
34. Efficient GPU Usage Tips and Tricks | Kaggle, accessed August 23, 2025, [https://www.kaggle.com/page/GPU-tips-and-tricks](https://www.kaggle.com/page/GPU-tips-and-tricks)  
35. kaggle gpu usage limit 30hours per week/ when does it reset?, accessed August 23, 2025, [https://www.kaggle.com/general/135810](https://www.kaggle.com/general/135810)  
36. Using GPU Spaces \- Hugging Face, accessed August 23, 2025, [https://huggingface.co/docs/hub/spaces-gpus](https://huggingface.co/docs/hub/spaces-gpus)  
37. LLama3 generation on Huggingface CPU Basic Space Free Tier Hardware \- DevQuasar, accessed August 23, 2025, [https://devquasar.com/hardware/llama3-generation-on-huggingface-cpu-basic-space-free-tier-hardware/](https://devquasar.com/hardware/llama3-generation-on-huggingface-cpu-basic-space-free-tier-hardware/)  
38. Spaces ZeroGPU: Dynamic GPU Allocation for Spaces \- Hugging Face, accessed August 23, 2025, [https://huggingface.co/docs/hub/spaces-zerogpu](https://huggingface.co/docs/hub/spaces-zerogpu)  
39. Efficient and cost-effective multi-tenant LoRA serving with Amazon SageMaker \- AWS, accessed August 23, 2025, [https://aws.amazon.com/blogs/machine-learning/efficient-and-cost-effective-multi-tenant-lora-serving-with-amazon-sagemaker/](https://aws.amazon.com/blogs/machine-learning/efficient-and-cost-effective-multi-tenant-lora-serving-with-amazon-sagemaker/)  
40. Deploy Once, Serve Many: The Ultimate Guide to TGI Multi-LoRA for Efficient AI Model Management \- Medium, accessed August 23, 2025, [https://medium.com/mr-plan-publication/deploy-once-serve-many-the-ultimate-guide-to-tgi-multi-lora-for-efficient-ai-model-management-f9ad8ad0c141](https://medium.com/mr-plan-publication/deploy-once-serve-many-the-ultimate-guide-to-tgi-multi-lora-for-efficient-ai-model-management-f9ad8ad0c141)  
41. TGI Multi-LoRA: Deploy Once, Serve 30 Models \- Hugging Face, accessed August 23, 2025, [https://huggingface.co/blog/multi-lora-serving](https://huggingface.co/blog/multi-lora-serving)  
42. Efficiently Serving Multiple Machine Learning Models with Lorax and vLLM on Vast.ai, accessed August 23, 2025, [https://vast.ai/article/efficiently-serving-multiple-ml-models-with-lorax-vllm-vast-ai](https://vast.ai/article/efficiently-serving-multiple-ml-models-with-lorax-vllm-vast-ai)  
43. LoRAX: Multi-LoRA Inference Server — SkyPilot documentation, accessed August 23, 2025, [https://docs.skypilot.co/en/v0.9.2/examples/serving/lorax.html](https://docs.skypilot.co/en/v0.9.2/examples/serving/lorax.html)  
44. The AI Acceleration Showdown: vLLM vs. TGI in the Race for Efficient LLM Deployment, accessed August 23, 2025, [https://runaker.medium.com/the-ai-acceleration-showdown-vllm-vs-tgi-in-the-race-for-efficient-llm-deployment-13fe90c635be](https://runaker.medium.com/the-ai-acceleration-showdown-vllm-vs-tgi-in-the-race-for-efficient-llm-deployment-13fe90c635be)  
45. Using LoRA adapters — vLLM, accessed August 23, 2025, [https://docs.vllm.ai/en/v0.6.1/models/lora.html](https://docs.vllm.ai/en/v0.6.1/models/lora.html)  
46. LORA Loading — production-stack \- vLLM, accessed August 23, 2025, [https://docs.vllm.ai/projects/production-stack/en/latest/tutorials/lora\_load.html](https://docs.vllm.ai/projects/production-stack/en/latest/tutorials/lora_load.html)  
47. Your Guide to Text Generation Inference (TGI) \- Sandgarden, accessed August 23, 2025, [https://www.sandgarden.com/learn/text-generation-inference-tgi](https://www.sandgarden.com/learn/text-generation-inference-tgi)  
48. Large Language Model Text Generation Inference \- GitHub, accessed August 23, 2025, [https://github.com/huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference)  
49. Efficiently Deploying LoRA Adapters: Optimizing LLM Fine-Tuning for Multi-Task AI, accessed August 23, 2025, [https://www.inferless.com/learn/how-to-serve-multi-lora-adapters](https://www.inferless.com/learn/how-to-serve-multi-lora-adapters)  
50. TGI v3 overview \- Hugging Face, accessed August 23, 2025, [https://huggingface.co/docs/text-generation-inference/conceptual/chunking](https://huggingface.co/docs/text-generation-inference/conceptual/chunking)  
51. LangGraph Tutorial: Building LLM Agents with LangChain's Agent Framework \- Zep, accessed August 23, 2025, [https://www.getzep.com/ai-agents/langgraph-tutorial/](https://www.getzep.com/ai-agents/langgraph-tutorial/)  
52. LangGraph Tutorial: What Is LangGraph and How to Use It? \- DataCamp, accessed August 23, 2025, [https://www.datacamp.com/tutorial/langgraph-tutorial](https://www.datacamp.com/tutorial/langgraph-tutorial)  
53. Deploying A LangGraph Agent Application with An Open-Source Model \- BentoML, accessed August 23, 2025, [https://www.bentoml.com/blog/deploying-a-langgraph-agent-application-with-an-open-source-model](https://www.bentoml.com/blog/deploying-a-langgraph-agent-application-with-an-open-source-model)  
54. How to use LangChain and LangGraph for Agentic AI \- Pluralsight, accessed August 23, 2025, [https://www.pluralsight.com/resources/blog/ai-and-data/langchain-langgraph-agentic-ai-guide](https://www.pluralsight.com/resources/blog/ai-and-data/langchain-langgraph-agentic-ai-guide)  
55. Using LangChain with vLLM: Complete Tutorial \- Lunary \- AI, accessed August 23, 2025, [https://lunary.ai/blog/vllm-langchain-tutorial](https://lunary.ai/blog/vllm-langchain-tutorial)  
56. LangChain \- vLLM, accessed August 23, 2025, [https://docs.vllm.ai/en/v0.9.1/serving/integrations/langchain.html](https://docs.vllm.ai/en/v0.9.1/serving/integrations/langchain.html)  
57. Using LoRA adapters \- vLLM, accessed August 23, 2025, [https://docs.vllm.ai/en/v0.5.4/models/lora.html](https://docs.vllm.ai/en/v0.5.4/models/lora.html)  
58. LangGraph \- GitHub Pages, accessed August 23, 2025, [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)  
59. LangGraph Tutorial: A Comprehensive Guide for Beginners, accessed August 23, 2025, [https://blog.futuresmart.ai/langgraph-tutorial-for-beginners](https://blog.futuresmart.ai/langgraph-tutorial-for-beginners)  
60. LangGraph's human-in-the-loop \- Overview, accessed August 23, 2025, [https://langchain-ai.github.io/langgraph/concepts/human\_in\_the\_loop/](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)  
61. LangGraph Agents \- Human-In-The-Loop \- User Feedback \- YouTube, accessed August 23, 2025, [https://www.youtube.com/watch?v=YmAaKKlDy7k](https://www.youtube.com/watch?v=YmAaKKlDy7k)  
62. Use a LangGraph agent | Generative AI on Vertex AI \- Google Cloud, accessed August 23, 2025, [https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/langgraph](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/langgraph)  
63. Continual Learning in Vision-Language Models via Aligned Model Merging \- arXiv, accessed August 23, 2025, [https://arxiv.org/html/2506.03189v1](https://arxiv.org/html/2506.03189v1)  
64. LoRA-Loop: Closing the Synthetic Replay Cycle for Continual VLM Learning \- arXiv, accessed August 23, 2025, [https://www.arxiv.org/abs/2507.13568](https://www.arxiv.org/abs/2507.13568)  
65. LoRA-Switch: Boosting the Efficiency of Dynamic LLM Adapters via System-Algorithm Co-design \- arXiv, accessed August 23, 2025, [https://arxiv.org/html/2405.17741v1](https://arxiv.org/html/2405.17741v1)