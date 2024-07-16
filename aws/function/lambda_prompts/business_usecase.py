from db.fetchprompts import fetch_prompt
from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET
import asyncio

# def get_usecase_prompt(industry_name:str,industry_category_name:str,business_area_name:str):
#     prompts=fetch_prompt("business_usecase")
#     prompts[1]=prompts[1].replace("{{industry_name}}",industry_name)
#     prompts[1]=prompts[1].replace("{{industry_category_name}}",industry_category_name)
#     prompts[1]=prompts[1].replace("{{business_area_name}}",business_area_name)
    
#     return prompts

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_usecase_prompt(industry_name: str, industry_category_name: str, business_area_name: str,langfuse) -> Prompt:
    prompt =fetch_prompt("business_usecase",langfuse)
    # asyncio.run(getprompt(prompt_name))
    
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_name}}", industry_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{industry_category_name}}", industry_category_name)
    prompt['system_prompt'] = prompt['system_prompt'].replace("{{business_area_name}}", business_area_name)
    
    return prompt

def usecase_parser(llm_response: str) -> List[Dict[str, object]]:
    root = ET.fromstring(llm_response)
    result = []

    for usecase in root.findall("USECASE"):
        result.append({
            "name": usecase.find('NAME').text,
            "description": usecase.find('DESCRIPTION').text,
            "urls": [url.text for url in usecase.find('URLS')]
        })

    return result

def get_xmlprompt(test_result:str)->str:
    # prompts = fetch_prompt("usecase_xml")
    # prompts['user_prompt'] = prompts['user_prompt'].replace("{{test_result}}", test_result)
    # return prompts['user_prompt']
    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into usecases and present it in a structured manner.
    Here is the test result you will be working with:
    <test_result>
    {test_result}
    </test_result>
    You must present this information in the following XML format:
    <RESPONSE>
        <USECASE>
            <NAME>name of business area</NAME>
            <DESCRIPTION>description of business area</DESCRIPTION>
            <URLS>
                <URL>url1</URL>
                <URL>url2</URL>
                <!-- Repeat URL tag for each URL -->
            </URLS>
        </USECASE>
        <!-- Repeat the USECASE structure for each usecase -->
    </RESPONSE>
    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure.
    CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult. Use &amp; for ampersands, &lt; for <, and &gt; for > within text content."""

    return prompt



# system_prompt=Acting as an expert analyst provide me as many use cases as you 
# find where AI can be used to improve or automate processes in the {{industry_name}}
# industry, {{industry_category_name}} category, {{business_area_name}} 
# Provide only those unique to {{business_area_name}} and avoid those not unique to it. 
# Avoid copyright infringement. Use only public resources. 

# user_prompt=Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
# Each description needs to be original and not fall into plagiarism.