
from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_sample_prompt(usecase_name: str, usecase_description: str, industry_name: str, industry_category_name: str):
    system_prompt = f""""""

    user_prompt=f""""""

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )

    return prompts


def get_competitor_prompt(description_result:str):
    system_prompt=f"""Please, provide a list of competitors software solutions to {description_result}"""

    user_prompt=f"""
    Exclude from your research comparator websites such as trustpilot, capterra or G2.
    Provide them an exhaustive list of urls without limitation of the number of results

    Software solution 1:
    Name of the solution: vistasocial.com
    URLs: http://vistasocial.com/

    """

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )
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