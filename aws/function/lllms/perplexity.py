from openai import OpenAI
import os
from typing import List, Dict

PERPLEXITY_MODEL = "llama-3-sonar-large-32k-chat"


def call_llm_perplexity(API_KEY,messages: List[Dict[str, str]], model: str = PERPLEXITY_MODEL, max_tokens: int = 150, temperature: float = 0, prompt_id: str = "", system_prompt: str = "") -> str:
    client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")
    
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )

    # print("PERPLEXITY PROMPT !")
    # print(prompt_id)
    return response.choices[0].message.content.strip()