import os
from dotenv import load_dotenv
import anthropic
from typing import List, Dict
import xml.etree.ElementTree as ET

load_dotenv()

assert os.environ.get("ANTHROPIC_API_KEY") != "", "ANTHROPIC_API_KEY is not set or is an empty string"

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

CLAUDE_SONNET_35 = "claude-3-5-sonnet-20240620"
CLAUDE_HAIKU_3 = "claude-3-haiku-20240307"


async def call_llm_claude(messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float = 0) -> Dict:
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature
    )
    text_block = message.content[0]
    xml_string = text_block.text

    return xml_string