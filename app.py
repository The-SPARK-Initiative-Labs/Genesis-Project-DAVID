# C:\David\app.py
# Fixed to properly handle <think> tags vs response

import chainlit as cl
import uuid
import asyncio
from src.local_agent.agent import create_agent_executor

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
            
            try:
                print("First user connected. Creating agent and preloading model into VRAM...")
                
                agent_executor, llm_instance = create_agent_executor()
                
                # Test with a simple message to preload
                test_response = await agent_executor.ainvoke(
                    {"input": "Hi"}, 
                    config={"configurable": {"session_id": "preload"}}
                )

                AGENT_EXECUTOR = agent_executor
                IS_MODEL_LOADED = True

                print("🟢 Model is now loaded and ready for all users!")
                await loading_msg.remove()
            
            except Exception as e:
                import traceback
                print(f"❌ Critical Error: Failed to load model: {str(e)}")
                traceback.print_exc()
                
                error_message = f"❌ Critical Error: Failed to load model: {str(e)}"
                await loading_msg.remove()
                await cl.Message(content=error_message).send()
                return
    
    cl.user_session.set("session_id", str(uuid.uuid4()))
    
    if IS_MODEL_LOADED:
        await cl.Message(content="🟢 David is ready! Hey Ben, what's on your mind?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming user messages - FIXED to separate thinking from response
    """
    session_id = cl.user_session.get("session_id")
    config = {"configurable": {"session_id": session_id}}

    try:
        # Collect full response first
        full_content = ""
        async for chunk in AGENT_EXECUTOR.astream(
            {"input": message.content},
            config=config
        ):
            if hasattr(chunk, 'content') and chunk.content:
                full_content += chunk.content

        # Parse thinking vs response
        if "<think>" in full_content and "</think>" in full_content:
            think_start = full_content.find("<think>")
            think_end = full_content.find("</think>") + len("</think>")
            thinking_part = full_content[think_start:think_end]
            response_part = full_content[think_end:].strip()
            
            # Show thinking first
            thinking_msg = cl.Message(content=thinking_part, author="David")
            await thinking_msg.send()
            
            # Then show response
            if response_part:
                response_msg = cl.Message(content=response_part, author="David")
                await response_msg.send()
        else:
            # No thinking tags, just send the content
            msg = cl.Message(content=full_content, author="David")
            await msg.send()
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        await cl.Message(content=error_msg, author="David").send()
        print(f"Error in on_message: {e}")
        import traceback
        traceback.print_exc()
