import asyncio
from db.mysql import insert_industry_business_areas,find_industries
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from pathlib import Path
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
# from prompts.business_area_xml import get_xmlprompt
from prompts.industry_category import business_parser 
import json
import os
from prompts.industry_business_area import get_industry_business_area, get_xmlprompt
async def main():
    industries=find_industries()
    for industryObj in industries:
        
        industry_name = industryObj["name"]
        industry_id = industryObj["id"]
        # if "retail" in industry_name.lower():
        print(f"processing for {industry_name} and {industry_id}")
        provider = LLM_PROVIDER_CLAUDE
        file_path = f"dump/industry_business/{provider}/{industry_name.replace(' ', '_')}.json"
        if not Path(file_path).is_file():
            prompts=await get_industry_business_area(industry_name)
            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']

            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL

            description_result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="industry_business_area",system_prompt=system_prompt)
            

            xml_prompt=get_xmlprompt(description_result)

            xml_result= await invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="industry_category")

            json_result = business_parser(xml_result)
            print(json_result)

            industry_category_id=None
            for business_result in json_result:
                name=business_result['name']
                description=business_result['description']
                if len(industry_id)>0:
                    insert_industry_business_areas(name,description,industry_id)

            json_result = json.dumps(json_result, indent='\t')
            print(json_result)

            # Ensure the 'dump' folder exists
            if not os.path.exists(f'dump/industry_business/{provider}'):
                    os.makedirs(f'dump/industry_business/{provider}')

            # Save the json_result to a file
            with open(file_path, "w") as file:
                file.write(json_result)
            


if __name__ == '__main__':
    asyncio.run(main())