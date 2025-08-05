# C:\David\src\app.py - Manual Step Pattern (Documentation)
import chainlit as cl
import ollama
import re

# --- Configuration ---
MODEL_NAME = "david"

@cl.on_chat_start
async def start_chat():
    cl.user_session.set("message_history", [])

@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})
    
    # Manual step instantiation - no Input/Output display
    async with cl.Step(name="Thinking", type="llm") as step:
        stream = await ollama.AsyncClient().chat(
            model=MODEL_NAME,
            messages=message_history,
            stream=True
        )
        
        full_response = ""
        
        async for chunk in stream:
            token = chunk["message"]["content"]
            full_response += token
        
        # Parse thinking vs final answer
        if "<think>" in full_response and "</think>" in full_response:
            # Extract thinking content for step display
            think_match = re.search(r'<think>(.*?)</think>', full_response, re.DOTALL)
            if think_match:
                think_content = think_match.group(1).strip()
                step.output = think_content
            
            # Extract final answer
            final_answer = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL).strip()
            
            if not final_answer:
                final_answer = "Hey there! 😊"
        else:
            # No think tags - treat entire response as final answer
            final_answer = full_response
            step.output = "Processing your message..."
    
    # Send final response outside the step
    await cl.Message(content=final_answer).send()
    
    message_history.append({"role": "assistant", "content": full_response})