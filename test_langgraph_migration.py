# C:\David\test_langgraph_migration.py
# Test script to validate LangGraph implementation preserves David's behavior

import asyncio
import os
from src.local_agent.agent import create_agent_executor
from langchain_core.messages import HumanMessage

async def test_david_langgraph():
    """Test David AI's LangGraph implementation."""
    
    print("🧪 Testing David AI's LangGraph Migration...")
    
    try:
        # Create the LangGraph agent
        david_graph, llm = create_agent_executor()
        print("✅ LangGraph agent created successfully")
        
        # Test configuration
        config = {"configurable": {"thread_id": "test_session"}}
        
        # Test 1: Basic conversation
        print("\n--- Test 1: Basic Conversation ---")
        response1 = await david_graph.ainvoke(
            {"messages": [HumanMessage(content="Hi David, how are you?")]},
            config=config
        )
        
        if response1 and 'messages' in response1:
            last_msg = response1['messages'][-1]
            print(f"David: {last_msg.content}")
            
            # Check for thinking tags
            if "<think>" in last_msg.content:
                print("✅ Thinking tags present - David's behavior preserved")
            else:
                print("⚠️  No thinking tags detected")
        
        # Test 2: Tool calling
        print("\n--- Test 2: Tool Calling ---")
        response2 = await david_graph.ainvoke(
            {"messages": [HumanMessage(content="What are your settings?")]},
            config=config
        )
        
        if response2 and 'messages' in response2:
            last_msg = response2['messages'][-1]
            print(f"David: {last_msg.content}")
            
            # Check if tool was called
            has_tool_call = any(
                hasattr(msg, 'tool_calls') and msg.tool_calls 
                for msg in response2['messages'] 
                if hasattr(msg, 'tool_calls')
            )
            
            if has_tool_call:
                print("✅ Tool calling functional")
            else:
                print("⚠️  Tool calling may not be working")
        
        # Test 3: Memory persistence
        print("\n--- Test 3: Memory Persistence ---")
        response3 = await david_graph.ainvoke(
            {"messages": [HumanMessage(content="Do you remember what I asked you earlier?")]},
            config=config
        )
        
        if response3 and 'messages' in response3:
            last_msg = response3['messages'][-1]
            print(f"David: {last_msg.content}")
            print("✅ Memory persistence test completed")
        
        print("\n🎉 LangGraph migration validation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment if needed
    if not os.getenv("OLLAMA_MODEL"):
        os.environ["OLLAMA_MODEL"] = "qwen3:14b"
    
    asyncio.run(test_david_langgraph())
