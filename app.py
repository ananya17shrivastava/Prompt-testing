import asyncio
import json
import os
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL
from prompts.industry_category import get_prompt, parser as industry_parser
from prompts.xml_prompt import get_xmlprompt
from pathlib import Path
from db.mysql import insert_industry_category, find_industries, delete_all_industry_category
from prompts.industry_category_summary import get_prompt as get_prompt_summary


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

    industries = find_industries()

    for industryObj in industries:
        
        industry_name = industryObj["name"]
        industry_id = industryObj["id"]
        # if "retail" in industry_name.lower():
        print(f"processing for {industry_name} and {industry_id}")
        provider = LLM_PROVIDER_CLAUDE
        print(f"generating for model {provider}")

        file_path = f"dump/{provider}/{industry_name.replace(' ', '_')}.json"
        if not Path(file_path).is_file():
            prompts = get_prompt(industry_name)
            # print(prompts)
            
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
            }], max_tokens=4096, temperature=.2,prompt_id="industry_category",system_prompt=system_prompt)

            xml_prompt=get_xmlprompt(description_result)

            xml_result= await invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
            }], max_tokens=4096, temperature=.2,prompt_id="industry_category")

            print(xml_result)
            json_result = industry_parser(xml_result)
        
            for industry_result in json_result:
                name = industry_result["name"]
                product_services = industry_result["description"]
                if len(industry_id) > 0:
                    insert_industry_category(industry_id, name, product_services)

                    
            json_result = json.dumps(json_result, indent='\t')
            print(json_result)

            

            # Ensure the 'dump' folder exists
            if not os.path.exists(f'dump/{provider}'):
                os.makedirs(f'dump/{provider}')

            # Save the json_result to a file
            with open(file_path, "w") as file:
                file.write(json_result)
            # process.exit(0)
            
        else:
            json_result = read_json_file(file_path)
            if json_result:
                text = json.dumps(json_result, indent=4)
                for industry_result in json_result:
                    name = industry_result["name"]
                    product_services = industry_result["description"]
                    if len(industry_id) > 0:
                        insert_industry_category(industry_id, name, product_services)



        # if "retail" in industry_name.lower():
        #     providers = [LLM_PROVIDER_PERPLEXITY, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT]
        #     results_by_models = []
        #     for provider in providers:
        #         print(f"generating for model {provider}")

        #         file_path = f"dump/{provider}/{industry_name.replace(' ', '_')}.json"
        #         if not Path(file_path).is_file():

        #             prompt = get_prompt(industry=industry_name)
    

        #             model = PERPLEXITY_MODEL
        #             if (provider == LLM_PROVIDER_CLAUDE):
        #                 model = CLAUDE_SONNET_35
        #             elif (provider == LLM_PROVIDER_GPT):
        #                 model = GPT4_MODEL
        #             elif (provider == LLM_PROVIDER_PERPLEXITY):
        #                 model = PERPLEXITY_MODEL

        #             result = await invoke_llm(provider, model, [{
        #                 "role": "user",
        #                 "content": prompt,
        #             }], max_tokens=4096, temperature=.2,prompt_id="industry_category",system_prompt=system_prompt)

        #             json_result = industry_parser(result)

        #             json_result = json.dumps(json_result, indent='\t')
        #             results_by_models.append(json_result)
        #             print(json_result)

        #             # Ensure the 'dump' folder exists
        #             if not os.path.exists(f'dump/{provider}'):
        #                 os.makedirs(f'dump/{provider}')

        #             # Save the json_result to a file
        #             with open(file_path, "w") as file:
        #                 file.write(json_result)
        #         else:
        #             data = read_json_file(file_path)
        #             if data:
        #                 text = json.dumps(data, indent=4)
        #                 results_by_models.append(text)

        #     print(len(results_by_models))
        #     summary_prompt = get_prompt_summary(industry_name, results_by_models)
        #     print(summary_prompt)
        #     print("==========")

        #     result = await invoke_llm(LLM_PROVIDER_CLAUDE, CLAUDE_SONNET_35, [{
        #         "role": "user",
        #                 "content": summary_prompt,
        #     }], max_tokens=4096, temperature=0,prompt="industry_category_summary",system_prompt=system_prompt)

            

        #     print(result)

        #     json_result = industry_parser(result)

        #     for industry_result in json_result:
        #         name = industry_result["name"]
        #         product_services = industry_result["description"]
        #         if len(industry_id) > 0:
        #             insert_industry_category(industry_id, name, product_services)

        #     json_result = json.dumps(json_result, indent='\t')

        #     file_path = f"dump/combined/{industry_name.replace(' ', '_')}.json"
        #     if not os.path.exists(f'dump/combined'):
        #         os.makedirs(f'dump/combined')

        #     with open(file_path, "w") as file:
        #         file.write(json_result)

        # else:
            
        


if __name__ == '__main__':
    asyncio.run(main())
