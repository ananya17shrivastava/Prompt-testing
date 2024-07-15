import asyncio
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from pathlib import Path
from db.mysql import find_usecases
from prompts.ai_solutions import get_aisolutions_prompt, get_xmlprompt,aisolutions_parser, get_competitor_prompt
import json
import os
from db.mysql import insert_solutions
from urllib.parse import urlparse
import time

def extract_name_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split by '.' and take all parts except the last if there are more than 2 parts
    parts = domain.split('.')
    if len(parts) > 2:
        name = '.'.join(parts[:-1])
    else:
        name = domain
    return name


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
        usecase_description=use_case['description']
        industry_name=use_case['industry_name']
        industry_category_name=use_case['industry_category_name']
        provider=LLM_PROVIDER_PERPLEXITY
        file_path = f"dump/solutions/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}/{usecase_name.replace(' ', '_').replace('/', '_')}.json"
        if not Path(file_path).is_file():
            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL

            prompts=get_aisolutions_prompt(usecase_name,usecase_description,industry_name,industry_category_name)

            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']
            print(system_prompt)
            description_result = invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt)
            print(description_result)

            process.exit(0)

            provider=LLM_PROVIDER_CLAUDE
            model = CLAUDE_HAIKU_3

            xml_prompt=get_xmlprompt(description_result)
            result= invoke_llm(provider, model, [{
                    "role": "user",
                    "content": xml_prompt,
            }], max_tokens=4096, temperature=0,prompt_id="ai_solutions")

            result = result.replace("&", "&amp;")
            json_result = aisolutions_parser(result)
            json_result = json.dumps(json_result, indent='\t')

            #iteration 2 for getting competitors
            provider=LLM_PROVIDER_PERPLEXITY
            model = PERPLEXITY_MODEL

            competitor_prompt=get_competitor_prompt(description_result)
            competitor_user_prompt=competitor_prompt['user_prompt']
            competitor_system_prompt=competitor_prompt['system_prompt']

            competitor_result=invoke_llm(provider, model, [{
                "role": "user",
                "content": competitor_user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=competitor_system_prompt)
            print("competitor result ::")
            print(competitor_result)


            provider=LLM_PROVIDER_CLAUDE
            model = CLAUDE_HAIKU_3

            competitor_xml_prompt=get_xmlprompt(competitor_result)
            result2= invoke_llm(provider, model, [{
                    "role": "user",
                    "content": competitor_xml_prompt,
            }], max_tokens=4096, temperature=0,prompt_id="ai_solutions")

            result2 = result2.replace("&", "&amp;")
            competitor_json_result = aisolutions_parser(result2)
            competitor_json_result = json.dumps(competitor_json_result, indent='\t')

            print(competitor_json_result)
            print(json_result)

            solutions = json.loads(json_result)
            competitors = json.loads(competitor_json_result)

            combined_results = []

            for solution in solutions:
                combined_results.append(solution)

            for competitor in competitors:
                combined_results.append(competitor)
            
            combined_json = json.dumps(combined_results, indent='\t')

            print(combined_json)
            # process.exit(0)

            for solution in combined_results:
                url=solution['urls']
                name = extract_name_from_url(url)
                insert_solutions(case_id,name,url)

            provider=LLM_PROVIDER_PERPLEXITY
            model = PERPLEXITY_MODEL

            combined_json = json.dumps(combined_results, indent='\t')
            

            if not os.path.exists(f'dump/solutions/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}'):
                    os.makedirs(f'dump/solutions/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}')

            # Save the json_result to a file
            with open(file_path, "w") as file:
                file.write(json_result)
                
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