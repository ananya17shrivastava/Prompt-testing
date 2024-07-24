
from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET
from db.fetchprompts import fetch_prompt

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_aisolutions_prompt(usecase_name: str, usecase_description: str, industry_name: str, industry_category_name: str,langfuse):

    # prompts
    # if industry_name is None :
    prompts =fetch_prompt("ai_solutions_null",langfuse)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_name}}",usecase_name)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_description}}",usecase_description)
        
    
    # else:
    #     prompts =fetch_prompt("ai_solutions",langfuse)
    #     prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_name}}",usecase_name)
    #     prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_description}}",usecase_description)
    #     prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_name}}",industry_name)
    #     prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_category_name}}",industry_category_name)

    return prompts



    


def get_competitor_prompt(description_result:str,langfuse):
    prompts =fetch_prompt("ai_solutions_competitor",langfuse)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{description_result}}",description_result)
    return prompts




def get_xmlprompt(test_result:str)->str:

    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into ai solutions and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
    <SOLUTION>
        <NAME>name of solution</NAME>
        <URL>Url of solution</URL>
    </SOLUTION>
    <!-- Repeat the SOLUTION structure for each solution -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt


def aisolutions_parser(llm_response:str)->List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    for usecase in root.findall("SOLUTION"):
        name = usecase.find('NAME')
        urls = usecase.find('URL')
        result.append({
            "name": name.text.strip(),
            "urls": urls.text.strip()
        })
        
       
            

    return result






# "You are an Expert Software Analyst tasked with identifying what are the best software solutions for the following use case:
#     {{usecase_name}}
#     {{usecase_description}}

#     You need to provide the Software solutions that best apply to that use case for the {{industry_name}} industry and {{industry_category_name}} industry category. Your goal is to generate a completely accurate list of software solutions with their website url.
#     Exclude those solutions not mentioning specifically this use case on their website, resources, case studies or blogs.

#     Motivation:
#     Identifying these software solutions is crucial for leveraging technology to optimize operations, increase efficiency, and drive innovation in the {{industry_category_name}} category of the {{industry_name}} industry"