import asyncio
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from pathlib import Path
from db.mysql import find_usecases
from prompts.business_task_prompt import get_business_task_prompt,get_xmlprompt, business_task_parser
import json
import os
# from db.mysql import insert_tasks
from urllib.parse import urlparse
import time




async def main():
    use_cases=find_usecases()
    
    print(use_cases)
    print(len(use_cases))
    i=0
    total_data=len(use_cases)
    
    # process.exit(0)
    


    for use_case in use_cases:
        print(f"data {i + 1} of {total_data}")
        # process.exit(0)

        case_id=use_case['case_id']
        usecase_name=use_case['name']
        business_area_name=use_case['business_area_name']
        industry_name=use_case['industry_name']
        industry_category_name=use_case['industry_category_name']
        provider=LLM_PROVIDER_PERPLEXITY
        file_path = f"dump/business_tasks/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}/{business_area_name.replace(' ', '_').replace('/', '_')}/{usecase_name.replace(' ', '_').replace('/', '_')}.json"
        if not Path(file_path).is_file():
            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL

            prompts= get_business_task_prompt(industry_name, industry_category_name, usecase_name,business_area_name)
            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']
            print(system_prompt)

            description_result =  invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_tasks",system_prompt=system_prompt)
            print(description_result)

            provider=LLM_PROVIDER_CLAUDE
            model = CLAUDE_HAIKU_3

            xml_prompt=get_xmlprompt(description_result)
            result= invoke_llm(provider, model, [{
                    "role": "user",
                    "content": xml_prompt,
            }], max_tokens=4096, temperature=0,prompt_id="ai_solutions")

            result = result.replace("&", "&amp;")
            json_result = business_task_parser(result)

            # for task_result in json_result:
            #     name=task_result['name']
            #     description=task_result['description']
            #     urls=task_result['urls']
            #     insert_tasks(name,description,urls,case_id)
                
            json_result = json.dumps(json_result, indent='\t')


            print(json_result)


            process.exit(0)



            
                
        i+=1







# if __name__ == '__main__':
#     asyncio.run(main())

if __name__ == "__main__":
    # for i in range(1000):
    #     try:
    asyncio.run(main())
        #     break
        # except Exception as e:
        #     print(e)
        #     print(f"""Restarting...{i}""")
        #     time.sleep(15)