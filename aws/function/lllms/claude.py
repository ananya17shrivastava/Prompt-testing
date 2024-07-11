import os
import anthropic
from typing import List, Dict
import xml.etree.ElementTree as ET


CLAUDE_SONNET_35 = "claude-3-5-sonnet-20240620"
CLAUDE_HAIKU_3 = "claude-3-haiku-20240307"


def call_llm_claude(API_KEY:str,messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float = 0,prompt_id:str="",system_prompt: str="") -> str:
    client = anthropic.Anthropic(
        api_key=API_KEY
    )

    response = client.messages.create(
        system=system_prompt,
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature
    )
    text_block = response.content[0]
    xml_string = text_block.text
    # feed_data_to_mongodb(prompt_id,xml_string,model=CLAUDE_SONNET_35)
    return xml_string