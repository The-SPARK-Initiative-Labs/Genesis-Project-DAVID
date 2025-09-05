# C:\David\app.py
# Simplified David with full tool system

import chainlit as cl
import uuid
import asyncio
from src.local_agent.agent import create_agent_executor, get_or_create_session_history
from src.conversation_logger import log_conversation_summary
from langchain_core.messages import HumanMessage

# Global state
MODEL_LOAD_LOCK = asyncio.Lock()
IS_MODEL_LOADED = False
DAVID_GRAPH = None

@cl.on_chat_start
async def on_chat_start():
    """Initialize simplified David."""
    global IS_MODEL_LOADED, DAVID_GRAPH
    
    async with MODEL_LOAD_LOCK:
        if not IS_MODEL_LOADED:
            loading_msg = cl.Message(content="🔄 Loading David...")
            await loading_msg.send()
            
            try:
                david_graph, llm_instance = create_agent_executor()
                
                # Test with simple message
                test_config = {"configurable": {"thread_id": "preload"}}
                test_response = await david_graph.ainvoke(
                    {"messages": [HumanMessage(content="Hi")]}, 
                    config=test_config
                )

                DAVID_GRAPH = david_graph
                IS_MODEL_LOADED = True

                print("🟢 David loaded successfully!")
                await loading_msg.remove()
            
            except Exception as e:
                print(f"❌ Error loading David: {str(e)}")
                import traceback
                traceback.print_exc()
                
                await loading_msg.remove()
                await cl.Message(content=f"❌ Error loading David: {str(e)}").send()
                return
    
    # Create session
    session_id = str(uuid.uuid4())
    cl.user_session.set("session_id", session_id)
    
    if IS_MODEL_LOADED:
        await cl.Message(content="🟢 David is ready! What can I help you with?").send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    session_id = cl.user_session.get("session_id")
    config = {"configurable": {"thread_id": session_id}}

    try:
        # Prepare input
        graph_input = {"messages": [HumanMessage(content=message.content)]}
        
        # Invoke David
        result = await DAVID_GRAPH.ainvoke(graph_input, config=config)
        
        # Extract response
        full_content = ""
        if result and 'messages' in result:
            last_message = result['messages'][-1]
            if hasattr(last_message, 'content'):
                full_content = last_message.content

        # Send response
        if full_content:
            msg = cl.Message(content=full_content, author="David")
            await msg.send()
        else:
            msg = cl.Message(content="I'm having trouble processing that.", author="David")
            await msg.send()
        
        # Log conversation
        get_or_create_session_history(session_id, DAVID_GRAPH)
        log_conversation_summary(session_id)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        await cl.Message(content=error_msg, author="David").send()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
