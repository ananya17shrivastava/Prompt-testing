import asyncio
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from pathlib import Path
from llms.perplexity import PERPLEXITY_MODEL
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from prompts.business_usecase import get_usecase_prompt,usecase_parser, get_xmlprompt
# from prompts.usecase_xml import get_xmlprompt
import json
import time
import os
from db.mysql import find_business_areas,insert_usecase


async def main():
    business_areas=find_business_areas()
    print(len(business_areas))
    i=0
    total_data=len(business_areas)
    # process.exit(0)


    for business_area in business_areas:
        print(f"data {i + 1} of {total_data}")


        business_area_id=business_area['business_area_id']
        business_area_name=business_area['business_area_name']
        industry_id=business_area['industry_id']
        industry_name=business_area['industry_name']
        industry_category_name=business_area['industry_category_name']
        industry_category_id=business_area['industry_category_id']


        #case id, usecase name, industry_id, organization_created_id, description, industry_category_id, business_area_id
                
        if not industry_category_name:
            industry_category_name="direct_industry_values"
        print(f"processing use case for business area {business_area_name} belonging to industry category {industry_category_name} of industry {industry_name} ")
        provider=LLM_PROVIDER_PERPLEXITY
        print(f"generating for model {provider}")
        
        

        file_path = f"dump/usecases/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}/{business_area_name.replace(' ', '_').replace('/', '_')}.json"
        if not Path(file_path).is_file():
            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL


            prompts=await get_usecase_prompt(industry_name,industry_category_name,business_area_name)
            # user_prompt=prompts[0]
            # system_prompt=prompts[1]
            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']
            # print(user_prompt)
            # print(system_prompt)
            # user_prompt, system_prompt = get_usecase_prompt(industry_name, industry_category_name, business_area_name)
            description_result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt)
            print(description_result)
            provider=LLM_PROVIDER_CLAUDE
            
            model = CLAUDE_HAIKU_3
            
            xml_prompt=get_xmlprompt(description_result)

            result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
            }], max_tokens=4096, temperature=0,prompt_id="business_area_xml")
            print(result)
            # process.exit(0)
            # print(result)
            result = result.replace("&", "&amp;")
            json_result = usecase_parser(result)
            # json_result = json.dumps(json_result, indent='\t')
            # print(json_result)

            # process.exit(0)
            for usecases_result in json_result:
                name=usecases_result['name']
                description=usecases_result['description']
                urls=usecases_result['urls']
                # print(type(urls))
                # process.exit(0)
                if len(business_area_id)>0:
                    insert_usecase(name,description,business_area_id,industry_category_id,industry_id,urls)


            json_result = json.dumps(json_result, indent='\t')
            print(json_result)

            provider=LLM_PROVIDER_PERPLEXITY
            model = PERPLEXITY_MODEL
            if not os.path.exists(f'dump/usecases/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}'):
                os.makedirs(f'dump/usecases/{provider}/{industry_name.replace(' ', '_').replace('/', '_')}/{industry_category_name.replace(' ', '_').replace('/', '_')}')

            # Save the json_result to a file
            with open(file_path, "w") as file:
                file.write(json_result)
            
        i+=1

        # process.exit(0)


            #case id, usecase name, industry_id, organization_created_id, description, industry_category_id, business_area_id
                















# if __name__ == '__main__':
#     asyncio.run(main())

if __name__ == "__main__":
    for _ in range(1000):
        try:
            asyncio.run(main())
            break
        except Exception as e:
            print(e)
            print('Restarting...')
            time.sleep(15)