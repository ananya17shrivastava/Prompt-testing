from openai import OpenAI
import os
from typing import List, Dict
import json
from db.mysql import feed_response_to_sql

PERPLEXITY_MODEL = "llama-3-sonar-large-32k-chat"


def call_llm_perplexity(conn,API_KEY,messages: List[Dict[str, str]], model: str = PERPLEXITY_MODEL, max_tokens: int = 150, temperature: float = 0, prompt_id: str = "", system_prompt: str = "",ai_machine_id:str="") -> str:
    client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")
    
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    response_data = {
        "id": response.id,
        "created": response.created,
        "model": response.model,
        "object": response.object,
        "usage": {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens
        },
        "choices": [
            {
                "finish_reason": choice.finish_reason,
                "index": choice.index,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content
                }
            } for choice in response.choices
        ]
    }
    response_data=json.dumps(response_data, indent='\t')

    feed_response_to_sql(prompt_id,ai_machine_id,response_data,conn)
    return response.choices[0].message.content.strip()