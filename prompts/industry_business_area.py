from db.mysql import fetch_prompt
from typing import TypedDict

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_industry_business_area(industry_name:str)-> Prompt:
    prompts=fetch_prompt("industry_business_area")
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry}}",industry_name)
    return prompts

# system_prompt=Acting as an expert analyst tell me what are the business areas or departments unique of the {{industry}} industry. 
# Exclude from that list any business area or department unique to its INDUSTRY CATEGORIES 

# Exclude business areas common to the {{industry}} industry or common to other industries
# Avoid assumptions and use the most acknowledged list in expert research.
 
# user_prompt=Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
# Each description needs to be original and not fall into plagiarism.