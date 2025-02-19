import ollama
import asyncio
import requests
import base64
import json
from typing import Optional, Union

endpoint = "http://localhost:11434/api/chat"
client = ollama.AsyncClient(host="http://localhost:11434")
#model = "deepseek-r1:8b"
model = "llama3.2:latest"

### --------------------------------------------------------------------

async def analysis_inference(text: str, sys_prompt: str) -> str:
    # Parameters
    options = {
        "temperature": 0.2,
        "num_ctx": 4096,
    }
    params = {
        "model": model,
        "options": options
    }
    
    # Create the payload 
    messages = []
    messages.append({ "role": "system", "content": sys_prompt})
    messages.append({ "role": "user", "content": text})
    payload = params 
    payload["messages"] = messages
    
    # Try inference using ollama
    try:
        # Chat Completion
        chat_completion = await client.chat(**payload)
        #print(completion.message.content)
        return chat_completion.message.content               
    except Exception as err:
        print(f'Exception: {err}')
        return None    
     
    