import os
import asyncio
from langfuse import Langfuse
from typing import List, Dict, Union,TypedDict
from dotenv import load_dotenv

load_dotenv()

langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host="https://cloud.langfuse.com"
)

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def fetch_prompt(prompt_name:str)-> Prompt:
    prompt_client =langfuse.get_prompt(prompt_name)
    prompt_content = prompt_client.prompt

    system_prompt=''
    user_prompt=''
    for content in prompt_content:
        if content['role']=='system':
            system_prompt=content['content']
        elif content['role']=='user':
            user_prompt=content['content']
    
    result = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )
    return result



    
