from db.mysql import fetch_prompt
from typing import TypedDict

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_industry_business_area(industry_name:str)-> Prompt:
    prompts=fetch_prompt("industry_business_area")
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry}}",industry_name)
    return prompts

def get_xmlprompt(test_result:str)->str:
    # prompts = fetch_prompt("business_area_xml")
    # prompts['user_prompt'] = prompts[0].replace("{{test_result}}", test_result)
    # return prompts['user_prompt']
    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into business areas and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
    <BUSINESS_AREA_NAME>
    <NAME>name of business area</NAME>
    <DESCRIPTION>description of business area</DESCRIPTION>
    </BUSINESS_AREA_NAME>
    <!-- Repeat the BUSINESS_AREA_NAME structure for each business area -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt

# system_prompt=Acting as an expert analyst tell me what are the business areas or departments unique of the {{industry}} industry. 
# Exclude from that list any business area or department unique to its INDUSTRY CATEGORIES 

# Exclude business areas common to the {{industry}} industry or common to other industries
# Avoid assumptions and use the most acknowledged list in expert research.
 
# user_prompt=Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
# Each description needs to be original and not fall into plagiarism.