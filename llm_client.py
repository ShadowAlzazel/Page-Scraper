import ollama
from openai import OpenAI
import asyncio
import requests
import base64
import json
from typing import Optional, Union

from settings import SETTINGS

KEYS = {}

def load_keys():
    global KEYS
    file_path = "keys.json"
    # Load KEYS obj with API secrets
    with open(file_path, "r") as f:
        obj = json.loads(f.read())
        for key, value in obj.items():
            if not value:
                continue
            KEYS[key] = value

def get_key(key: str) -> str:
    load_keys()
    return KEYS[key]


class BaseClient():
    """
        This is the base client class to handle inference for all the available APIs

    """
    def __init__(self, api: str, model: str):
        #model = "llama3.2:latest"
        #model = "deepseek-r1:8b"
        self.model: str = model
        self.api: str = api
        
        # Ollama
        if api == "ollama":
            self.endpoint = "http://localhost:11434/api/chat"
            self.client = ollama.AsyncClient(host="http://localhost:11434")
        elif api == "openai":
            self.api_key = get_key("OPENAI_API_KEY")
            self.client = OpenAI(api_key=self.api_key)
        

    ### --------------------------OLLAMA------------------------------------
    async def _ollama_inference(self, text: str, sys_prompt: str) -> str:
        # Parameters
        options = {
            "temperature": 0.2,
            "num_ctx": 4096,
        }
        params = {
            "model": self.model,
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
            chat_completion = await self.client.chat(**payload)
            #print(completion.message.content)
            return chat_completion.message.content               
        except Exception as err:
            print(f'Exception: {err}')
            return None    
     

    ### ----------------------------OPENAI----------------------------------
    async def _openai_inference(self, text: str, sys_prompt: str) -> str:
        # Parameters
        params = {
            "model": self.model,
            "temperature": 0.25,
        }
        
        # Create the payload 
        messages = []
        messages.append({ "role": "system", "content": sys_prompt})
        messages.append({ "role": "user", "content": text})
        payload = params 
        payload["messages"] = messages
        
        # Try inference using openai
        try:
            # Chat Completion
            chat_completion = self.client.chat.completions.create(**payload)
            return chat_completion.choices[0].message.contenet              
        except Exception as err:
            print(f'Exception: {err}')
            return None    


    ### --------------------------------------------------------------------
    async def chat_inference(self, text: str, sys_prompt: str) -> str:
        """The main method to interact and run chat completions to the LLM

            Args:
                text (str): The text that is being run inference on, like the contents of the pdf.
                sys_prompt (str): The system prompt that the LLM will use to construct the output.

            Raises:
                Exception: When there is not a valid api to run inference on.

            Returns:
                str: The raw string response of the content inference.
        """
        # API detection
        if self.api == "ollama":
            return await self._ollama_inference(text, sys_prompt)
        elif self.api == "openai":
            return await self._openai_inference(text, sys_prompt)
        else: 
            raise Exception("Not valid API architecture. Please use the available configure APIs.")
        
