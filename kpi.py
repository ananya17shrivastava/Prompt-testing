import asyncio
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from pathlib import Path
from prompts.kpi_prompt import get_kpi_prompt,get_xmlprompt, kpi_parser
from db.mysql import find_aisolutions
import time
import json
async def main():
    ai_solutions=find_aisolutions()
    print(ai_solutions)

    for ai_solution in ai_solutions:
        solution_name=ai_solution['solution_name']
        usecase_name=ai_solution['usecase_name']
        usecase_description=ai_solution['usecase_description']
        industry_category_name=ai_solution['industry_category_name']
        industry_name=ai_solution['industry_name']
        provider=LLM_PROVIDER_PERPLEXITY
        file_path = f"dump/kpi/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}/{usecase_name.replace(' ', '_').replace('/', '_')}/{solution_name.replace(' ', '_').replace('/', '_')}.json"
        if not Path(file_path).is_file():
            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL

            prompts=await get_kpi_prompt(solution_name,usecase_name,usecase_description,industry_category_name,industry_name)
            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']
            description_result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt)
            print(description_result)

            provider=LLM_PROVIDER_CLAUDE
            model = CLAUDE_HAIKU_3

            xml_prompt=get_xmlprompt(description_result)
            result= await invoke_llm(provider, model, [{
                    "role": "user",
                    "content": xml_prompt,
            }], max_tokens=4096, temperature=0,prompt_id="ai_solutions")



            result = result.replace("&", "&amp;")
            json_result = kpi_parser(result)
            json_result = json.dumps(json_result, indent='\t')
            print(json_result)
            

            process.exit(0)














        









if __name__ == "__main__":
    # for i in range(1000):
    #     try:
    asyncio.run(main())
        #     break
        # except Exception as e:
        #     print(e)
        #     print(f"""Restarting...{i}""")
        #     time.sleep(15)