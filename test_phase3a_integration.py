# Test Phase 3A system tools integration
import sys
sys.path.append('C:/David/src')

from local_agent.agent import create_agent_executor
from langchain_core.messages import HumanMessage

def test_system_tools():
    """Test that David can access and use the new system tools."""
    print("Creating David's enhanced agent...")
    
    try:
        david_graph, llm = create_agent_executor()
        print("Agent created successfully")
        
        # Test configuration for thread
        config = {"configurable": {"thread_id": "test_phase3a"}}
        
        # Test tool availability
        print("Testing tool calling...")
        test_input = {"messages": [HumanMessage(content="What tools do you have available now?")]}
        
        result = david_graph.invoke(test_input, config=config)
        print("Tool query successful")
        
        # Test file operation
        print("Testing file operations...")
        file_test_input = {"messages": [HumanMessage(content="Create a test file called hello.txt with 'Hello Phase 3A' content")]}
        
        result = david_graph.invoke(file_test_input, config=config)
        print("File operation test completed")
        
        print(f"Final response: {result['messages'][-1].content}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system_tools()
