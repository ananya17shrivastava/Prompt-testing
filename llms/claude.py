import os
from dotenv import load_dotenv
import anthropic
from typing import List, Dict
import xml.etree.ElementTree as ET
# from db.mongo import feed_data_to_mongodb
from db.mysql import get_api_key,feed_response_to_sql
import json

# load_dotenv()

# assert os.environ.get("ANTHROPIC_API_KEY") != "", "ANTHROPIC_API_KEY is not set or is an empty string"


ANTHROPIC_API_KEY = get_api_key("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY
)

CLAUDE_SONNET_35 = "claude-3-5-sonnet-20240620"
CLAUDE_HAIKU_3 = "claude-3-haiku-20240307"


def call_llm_claude(messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float = 0,prompt_id:str="",system_prompt: str="",ai_machine_id:str="") -> str:
    response = client.messages.create(
        system=system_prompt,
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature
    )
    print(response)

    response_dict = {
        "id": response.id,
        "content": [
            {
                "text": content.text,
                "type": content.type
            } for content in response.content
        ],
        "model": response.model,
        "role": response.role,
        "stop_reason": response.stop_reason,
        "stop_sequence": response.stop_sequence,
        "type": response.type,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
    
    # Convert the dictionary to a JSON string
    response_data = json.dumps(response_dict, indent='\t')
    print(response_data)
    feed_response_to_sql(prompt_id,ai_machine_id,response_data)
    text_block = response.content[0]
    xml_string = text_block.text
    # feed_data_to_mongodb(prompt_id,xml_string,model=CLAUDE_SONNET_35)
    return xml_string
