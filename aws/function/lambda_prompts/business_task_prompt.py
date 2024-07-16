from typing import List, Dict,TypedDict, Union
import xml.etree.ElementTree as ET
from db.fetchprompts import fetch_prompt

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_business_task_prompt(industry_name:str,industry_category_name:str,usecase_name:str,business_area_name:str,langfuse):
    prompt =fetch_prompt("business_task",langfuse)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_name}}", industry_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_category_name}}", industry_category_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{usecase_name}}", usecase_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{business_area_name}}", business_area_name)
    return prompt

def get_xmlprompt(test_result:str)->str:

    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into Business tasks and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
        <BUSINESS_TASK>
            <NAME>Name of business task</NAME>
            <DESCRIPTION>Description of business task</DESCRIPTION>
            <URLS>
                <URL>Url 1 </URL>
                <URL>Url 2</URL>
            </URLS>
        </BUSINESS_TASK>
        <!-- Repeat the BUSINESS_TASK structure for each KPI -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt

def business_task_parser(llm_response: str) -> List[Dict[str, Union[str, List[str]]]]:
    root = ET.fromstring(llm_response)
    result = []

    for task in root.findall("BUSINESS_TASK"):
        result.append({
            "name": task.find('NAME').text,
            "description": task.find('DESCRIPTION').text,
            "urls": [url.text for url in task.find('URLS').findall('URL')]
        })

    return result





# You are an Expert AI Use Case Analyst tasked with identifying where AI can be applied to improve or automate processes 
#     within the {{industry_name}} industry, under the {{industry_category_name}} category, specifically for the use case {{usecase_name}} within the 
#     {{business_area_name}} business area. Your goal is to generate a comprehensive list of the business tasks currently executed without AI that are enhanced or automated in this use case. 
#     This is not about providing a long list of tasks but about being very accurate naming and describing the main task or tasks impacted. 
#     Flag the main task impacted as main when you find several and give a maximum of 3 main tasks only.
#     Use only public and accessible resources, avoiding copyright infringement.

#     Motivation: Identifying these tasks is important for businesses to know where AI can help them to optimise their business.