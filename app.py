# C:\David\app.py
# This is the main UI file for the Chainlit application.
# Audited to be correct as per the provided research documents.

import chainlit as cl
import uuid
from src.local_agent.agent import create_agent_executor
import asyncio

# --- Global State for One-Time Model Loading ---
MODEL_LOAD_LOCK = asyncio.Lock()
IS_MODEL_LOADED = False
AGENT_EXECUTOR = None

@cl.on_chat_start
async def on_chat_start():
    """
    Initializes the agent and handles the one-time model preloading.
    """
    global IS_MODEL_LOADED, AGENT_EXECUTOR
    
    async with MODEL_LOAD_LOCK:
        if not IS_MODEL_LOADED:
            loading_msg = cl.Message(content="🔄 Loading David's consciousness... (This happens only once)")
            await loading_msg.send()
            
            try
                print("First user connected. Creating agent and preloading model into VRAM...")
                agent_executor = create_agent_executor()
                
                # Preload the model by invoking it with a simple message.
                llm = agent_executor.runnable.middle[0].middle[0] # Access the llm from the chain
                await llm.ainvoke("Preload")

                AGENT_EXECUTOR = agent_executor
                IS_MODEL_LOADED = True

                print("🟢 Model is now loaded and ready for all users!")
                await loading_msg.remove()
            
            except Exception as e:
                error_message = f"❌ Critical Error: Failed to load model: {str(e)}"
                print(error_message)
                await loading_msg.remove()
                await cl.Message(content=error_message).send()
                return
    
    cl.user_session.set("session_id", str(uuid.uuid4()))
    
    if IS_MODEL_LOADED:
        await cl.Message(content="🟢 David is ready! Hey Ben, what's on your mind?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming user messages using the definitive astream pattern.
    """
    session_id = cl.user_session.get("session_id")

    # This is the definitive, correct pattern from the research documents.
    cb = cl.AsyncLangchainCallbackHandler()
    config = {"configurable": {"session_id": session_id}}

    # Create the message for the final answer.
    msg = cl.Message(content="", author="David")
    await msg.send()

    # Stream the response.
    # The callback handler will automatically create the "Thinking Process" step.
    # The async for loop will stream the clean, parsed answer into our message.
    async for chunk in AGENT_EXECUTOR.astream(
        {"input": message.content},
        config={"callbacks": [cb], **config},
    ):
        await msg.stream_token(chunk)
    
    await msg.update()
