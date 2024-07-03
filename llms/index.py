from typing import List, Dict
from llms.claude import call_llm_claude
from llms.gpt import call_openai
from llms.perplexity import call_llm_perplexity

LLM_PROVIDER_CLAUDE = "claude"
LLM_PROVIDER_GPT = "gpt-4o"
LLM_PROVIDER_PERPLEXITY = "llama-3-sonar-large-32k-chat"


async def invoke_llm(provider: str, model: str, messages: List[Dict[str, str]], max_tokens: int, temperature: float = 0,prompt_id: str="",system_prompt: str=""):
    if (provider == LLM_PROVIDER_CLAUDE):
        return await call_llm_claude(max_tokens=max_tokens, messages=messages, model=model, temperature=temperature,prompt_id=prompt_id,system_prompt=system_prompt)
    elif (provider == LLM_PROVIDER_GPT):
        return await call_openai(max_tokens=max_tokens, messages=messages, model=model, temperature=temperature,prompt=prompt_id,system_prompt=system_prompt)
    elif (provider == LLM_PROVIDER_PERPLEXITY):
        return await call_llm_perplexity(max_tokens=max_tokens, messages=messages, model=model, temperature=temperature,prompt=prompt_id,system_prompt=system_prompt)
    else:
        raise Exception(f"provider def not found {provider}")
