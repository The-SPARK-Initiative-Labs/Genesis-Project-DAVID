# Test the fixed LangChain agent
import sys
import os
sys.path.append(os.getcwd())

try:
    from src.local_agent.agent import create_agent_executor
    print("[OK] Agent import successful")
    
    agent, llm = create_agent_executor()
    print("[OK] Agent creation successful")
    print(f"Model: {llm.model}")
    
    # Test basic functionality
    response = agent.invoke({"input": "Hello"}, config={"configurable": {"session_id": "test"}})
    print("[OK] Agent invoke successful")
    print(f"Response type: {type(response)}")
    print(f"Response content: {response}")
    
except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    traceback.print_exc()
