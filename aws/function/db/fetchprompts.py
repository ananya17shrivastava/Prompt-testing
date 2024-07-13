import os
from langfuse import Langfuse
from typing import List, Dict, Union,TypedDict



def connect_langfuse(secret_key:str,public_key:str):
    langfuse = Langfuse(
        secret_key=secret_key,
        public_key=public_key,
        host="https://cloud.langfuse.com"
    )
    return langfuse


class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def fetch_prompt(prompt_name:str,langfuse)-> Prompt:
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



    
