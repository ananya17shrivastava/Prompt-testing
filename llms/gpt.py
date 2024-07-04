import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict
from db.mongo import feed_data_to_mongodb
from db.mysql import get_api_key
load_dotenv()


OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY
)

GPT4_MODEL = "gpt-4o"  # Specify the model you want to use


async def call_openai(messages: List[Dict[str, str]], model: str = GPT4_MODEL, max_tokens: int = 2048, temperature: float = 0,prompt_id: str="",system_prompt: str="") -> str:

    response = await client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature
    )
    # print(response.choices[0].message.content)
    print("GPT PROMPT !")
    print(prompt_id)
    # feed_data_to_mongodb(prompt,response,model=GPT4_MODEL)
    return response.choices[0].message.content.strip()
