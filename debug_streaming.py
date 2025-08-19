# Debug the LangChain streaming issue
import sys
import os
sys.path.append(os.getcwd())

from src.local_agent.agent import create_agent_executor

async def test_langchain_streaming():
    """Test if LangChain streaming actually works"""
    print("Creating agent...")
    agent, llm = create_agent_executor()
    
    print("Testing streaming...")
    config = {"configurable": {"session_id": "debug"}}
    
    full_response = ""
    chunk_count = 0
    
    async for chunk in agent.astream({"input": "Hello"}, config=config):
        chunk_count += 1
        print(f"Chunk {chunk_count}: {type(chunk)} = {chunk}")
        if hasattr(chunk, 'content'):
            full_response += chunk.content
    
    print(f"\nTotal chunks: {chunk_count}")
    print(f"Full response: {full_response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_langchain_streaming())
