# C:\David\app.py
# Updated for LangGraph integration while preserving David's behavior

import chainlit as cl
import uuid
import asyncio
from src.local_agent.agent import create_agent_executor, get_or_create_session_history
from src.conversation_logger import log_conversation_summary
from langchain_core.messages import HumanMessage

# --- Global State for One-Time Model Loading ---
MODEL_LOAD_LOCK = asyncio.Lock()
IS_MODEL_LOADED = False
DAVID_GRAPH = None

@cl.on_chat_start
async def on_chat_start():
    """
    Initializes David AI's LangGraph agent and handles one-time model preloading.
    """
    global IS_MODEL_LOADED, DAVID_GRAPH
    
    async with MODEL_LOAD_LOCK:
        if not IS_MODEL_LOADED:
            loading_msg = cl.Message(content="🔄 Loading David's consciousness... (This happens only once)")
            await loading_msg.send()
            
            try:
                print("First user connected. Creating LangGraph agent and preloading model into VRAM...")
                
                david_graph, llm_instance = create_agent_executor()
                
                # Test with a simple message to preload
                test_config = {"configurable": {"thread_id": "preload"}}
                test_response = await david_graph.ainvoke(
                    {"messages": [HumanMessage(content="Hi")]}, 
                    config=test_config
                )

                DAVID_GRAPH = david_graph
                IS_MODEL_LOADED = True

                print("🟢 David AI's LangGraph model is now loaded and ready for all users!")
                await loading_msg.remove()
            
            except Exception as e:
                import traceback
                print(f"❌ Critical Error: Failed to load LangGraph model: {str(e)}")
                traceback.print_exc()
                
                error_message = f"❌ Critical Error: Failed to load model: {str(e)}"
                await loading_msg.remove()
                await cl.Message(content=error_message).send()
                return
    
    # Create unique session for this Chainlit session
    session_id = str(uuid.uuid4())
    cl.user_session.set("session_id", session_id)
    
    if IS_MODEL_LOADED:
        await cl.Message(content="🟢 David is ready! Hey Ben, what's on your mind?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Handles incoming user messages with LangGraph streaming.
    """
    session_id = cl.user_session.get("session_id")
    config = {"configurable": {"thread_id": session_id}}

    try:
        # Prepare input for LangGraph
        graph_input = {"messages": [HumanMessage(content=message.content)]}
        
        # Use simple invoke for now - streaming can be added later
        result = await DAVID_GRAPH.ainvoke(graph_input, config=config)
        
        # Extract the final response content
        full_content = ""
        if result and 'messages' in result:
            last_message = result['messages'][-1]
            if hasattr(last_message, 'content'):
                full_content = last_message.content

        # Debug what we're getting
        print(f"Full content received: {repr(full_content)}")
        
        # Parse thinking vs response (preserve existing logic)
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
            # No thinking tags, send full content
            if full_content:
                msg = cl.Message(content=full_content, author="David")
                await msg.send()
            else:
                # Fallback message
                msg = cl.Message(content="I'm having trouble processing that. Could you try rephrasing?", author="David")
                await msg.send()
        
        # Update session history for conversation logger compatibility
        get_or_create_session_history(session_id, DAVID_GRAPH)
        
        # Log conversation summary
        log_conversation_summary(session_id)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        await cl.Message(content=error_msg, author="David").send()
        print(f"Error in on_message: {e}")
        import traceback
        traceback.print_exc()
