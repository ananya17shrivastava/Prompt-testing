import os
from dotenv import load_dotenv
import openai
from typing import List, Dict

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

GPT4_MODEL = "gpt-4o"  # Specify the model you want to use

async def call_llm_gpt4(messages: List[Dict[str, str]], model: str = GPT4_MODEL, max_tokens: int = 150, temperature: float = 0) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            temperature=temperature
        )
        print(response.choices[0].message['content'].strip())
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return None