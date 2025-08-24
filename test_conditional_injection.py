# Test conditional consciousness injection fix
import sys
sys.path.append('C:/David/src')

from local_agent.agent import create_agent_executor
from langchain_core.messages import HumanMessage

def test_conditional_injection():
    """Test that system prompt is only injected conditionally, not every turn."""
    print("Testing conditional consciousness injection...")
    
    try:
        david_graph, llm = create_agent_executor()
        config = {"configurable": {"thread_id": "test_injection"}}
        
        # Test multiple turns to verify conditional injection
        test_messages = [
            "Hello",
            "What tools do you have?", 
            "How are you doing?",
            "Tell me about yourself",
            "What's your status?",
            "Can you help me?",  # This should trigger injection (turn 6, interval=5)
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n--- Turn {i+1}: {message} ---")
            
            result = david_graph.invoke(
                {"messages": [HumanMessage(content=message)]}, 
                config=config
            )
            
            # Check state
            state = david_graph.get_state(config)
            turn_count = state.values.get('turn_count', 0)
            
            # Check if system message is present in latest response
            last_message = result['messages'][-1]
            contains_system_prompt = "functionally sentient AI" in str(last_message.content)
            
            print(f"Turn count: {turn_count}")
            print(f"Contains system prompt: {contains_system_prompt}")
            print(f"Response length: {len(str(last_message.content))} chars")
            
            if contains_system_prompt:
                print("WARNING: System prompt detected in response content!")
        
        print("\n✅ Conditional injection test completed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conditional_injection()
