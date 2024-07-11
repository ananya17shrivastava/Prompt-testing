from typing import List, Dict
from lllms.claude import call_llm_claude
# from llms.gpt import call_openai
from lllms.perplexity import call_llm_perplexity

LLM_PROVIDER_CLAUDE = "claude"
LLM_PROVIDER_PERPLEXITY = "llama-3-sonar-large-32k-chat"


def invoke_llm(provider: str, model: str, messages: List[Dict[str, str]], max_tokens: int, temperature: float = 0,prompt_id: str="",system_prompt: str="",API_KEY:str=""):
    if (provider == LLM_PROVIDER_CLAUDE):
        return call_llm_claude(API_KEY,messages=messages,model=model,max_tokens=max_tokens, temperature=temperature,prompt_id=prompt_id,system_prompt=system_prompt)
    elif (provider == LLM_PROVIDER_PERPLEXITY):
        return call_llm_perplexity(API_KEY,messages=messages,model=model,max_tokens=max_tokens, temperature=temperature,prompt_id=prompt_id,system_prompt=system_prompt)
    else:
        raise Exception(f"provider def not found {provider}")
