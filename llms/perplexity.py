from openai import OpenAI

from db.mongo import feed_data_to_mongodb
import os
from typing import List, Dict

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "llama-3-sonar-large-32k-chat"


async def call_llm_perplexity(messages: List[Dict[str, str]], model: str = PERPLEXITY_MODEL, max_tokens: int = 150, temperature: float = 0,prompt: str="") -> str:
    # if 'OpenAI' in globals():
    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    # else:
    #     openai.api_key = PERPLEXITY_API_KEY
    #     openai.api_base = "https://api.perplexity.ai"
    #     response = openai.ChatCompletion.create(
    #         model=model,
    #         messages=messages,
    #         max_tokens=max_tokens,
    #         temperature=temperature
    #     )
    # print(response)
    print("PERPLEXITY PROMPT !")
    print(prompt)
    # feed_data_to_mongodb(prompt,response,model=PERPLEXITY_MODEL)
    return response.choices[0].message.content.strip()
