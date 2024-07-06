from db.mysql import fetch_prompt
from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET

# def get_usecase_prompt(industry_name:str,industry_category_name:str,business_area_name:str):
#     prompts=fetch_prompt("business_usecase")
#     prompts[1]=prompts[1].replace("{{industry_name}}",industry_name)
#     prompts[1]=prompts[1].replace("{{industry_category_name}}",industry_category_name)
#     prompts[1]=prompts[1].replace("{{business_area_name}}",business_area_name)
    
#     return prompts

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_usecase_prompt(industry_name: str, industry_category_name: str, business_area_name: str) -> Prompt:
    prompt = fetch_prompt("business_usecase")
    
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_name}}", industry_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_category_name}}", industry_category_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{business_area_name}}", business_area_name)
    
    return prompt

def usecase_parser(llm_response: str) -> List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    for category in root.findall("USECASE"):
        name = category.find('NAME').text
        value = category.find('DESCRIPTION').text
        # print(f"Name: {name}, Value: {value}")
        result.append({"name": name, "description": value})

    return result



# system_prompt=Acting as an expert analyst provide me as many use cases as you 
# find where AI can be used to improve or automate processes in the {{industry_name}}
# industry, {{industry_category_name}} category, {{business_area_name}} 
# Provide only those unique to {{business_area_name}} and avoid those not unique to it. 
# Avoid copyright infringement. Use only public resources. 

# user_prompt=Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
# Each description needs to be original and not fall into plagiarism.