import asyncio
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from pathlib import Path
from db.mysql import find_industry_categories,insert_business_areas
import json
import os
from prompts.business_areas import get_business_prompt, get_xmlprompt
from prompts.industry_category import business_parser 
# from prompts.business_area_xml import get_xmlprompt
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

async def main():
    industry_categories=find_industry_categories()
    print(industry_categories)
    # process.exit(0)

    for industry_category_obj in industry_categories:

        industry_category_name=industry_category_obj['category_name']
        industry_name=industry_category_obj['industry_name']
        industry_id=industry_category_obj['industry_id']
        industry_category_id=industry_category_obj['industry_category_id']
        print(f"processing for {industry_category_name} of industry {industry_name} whose industry id is {industry_id}")
        provider = LLM_PROVIDER_CLAUDE
        file_path = f"dump/business_areas/{provider}/{industry_name}/{industry_category_name.replace(' ', '_').replace('/', '_')}.json"
        if not Path(file_path).is_file():
            # prompt=get_business_prompt(industry_name,industry_category_name)
            model = PERPLEXITY_MODEL
            if (provider == LLM_PROVIDER_CLAUDE):
                model = CLAUDE_SONNET_35
            elif (provider == LLM_PROVIDER_GPT):
                model = GPT4_MODEL
            elif (provider == LLM_PROVIDER_PERPLEXITY):
                model = PERPLEXITY_MODEL
            
            prompts = await get_business_prompt(industry_name,industry_category_name)
            user_prompt = prompts['user_prompt']
            system_prompt = prompts['system_prompt']

            description_result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": user_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt)


            xml_prompt=get_xmlprompt(description_result)

            result = await invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="business_area_xml")

            print(result)

            json_result = business_parser(result)
        

            print(json_result)
            for business_result in json_result:
                name=business_result['name']
                description=business_result['description']
                if len(industry_category_id)>0:
                    insert_business_areas(name,description,industry_category_id,industry_id)

            json_result = json.dumps(json_result, indent='\t')
            print(json_result)

            # Ensure the 'dump' folder exists
            if not os.path.exists(f'dump/business_areas/{provider}/{industry_name}'):
                    os.makedirs(f'dump/business_areas/{provider}/{industry_name}')

            # Save the json_result to a file
            with open(file_path, "w") as file:
                file.write(json_result)

            # process.exit(0)

        # else:
        #     json_result = read_json_file(file_path)
        #     if json_result:
        #         text = json.dumps(json_result, indent=4)
        #         for industry_result in json_result:
        #             name = industry_result["name"]
        #             product_services = industry_result["description"]
        #             if len(industry_id) > 0:
        #                 insert_industry_category(industry_id, name, product_services)

        






if __name__ == '__main__':
    asyncio.run(main())