import asyncio
import json
import os
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE,LLM_PROVIDER_GPT,LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from prompts.industry_category import get_prompt, parser as industry_parser
from pathlib import Path
from db.mysql import create_db_connection, find_industries

async def main():

   
    industries=find_industries()
    # industries=["banking financial services","retail consumer products"]
    
    for industry in industries:

        file_path = f"dump/perplexity/{industry.replace(' ', '_')}.json"
        if Path(file_path).is_file():
            continue

        prompt = get_prompt(industry=industry)

        result = await invoke_llm(LLM_PROVIDER_PERPLEXITY, PERPLEXITY_MODEL, [{
            "role": "user",
            "content": prompt,
        }], max_tokens=2048, temperature=.2)

        json_result = industry_parser(result,industry)
        

        json_result = json.dumps(json_result, indent='\t')
        print(json_result)

        # Ensure the 'dump' folder exists
        if not os.path.exists('dump/perplexity'):
            os.makedirs('dump/perplexity')

        # Save the json_result to a file
        with open(file_path, "w") as file:
            file.write(json_result)



if __name__ == '__main__':
    asyncio.run(main())
