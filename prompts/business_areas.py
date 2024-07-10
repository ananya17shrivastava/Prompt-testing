from db.fetchprompts import fetch_prompt
from typing import TypedDict



class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

async def get_business_prompt(industry_name:str,industry_category_name:str)->Prompt:
    prompts=await fetch_prompt("business_areas")
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_category_name}}",industry_category_name)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_name}}",industry_name)
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




# Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
# Each description needs to be original and not fall into plagiarism.




# Acting as an expert analyst tell me what are the business areas or departments unique for the category {{industry_category_name}} of the {{industry_name}} industry. 
# Exclude from that list any business area or department unique to other INDUSTRY CATEGORIES 
# Exclude business areas common to the {{industry_name}} industry or common to other industries











# prompt=f"""Acting as an expert analyst tell me what are the business areas or departments unique for the category {{industry_category_name}} of the {{industry_name}} industry. 
#     Exclude from that list any business area or department unique to other INDUSTRY CATEGORIES 
#     Exclude business areas common to the {{industry_name}} industry or common to other industries

#     Avoid assumptions and use the most acknowledged list in expert research. 
#     Each description needs to be original and not fall into plagiarism.

#     Provide it in code format ready to be entered on a .xml table of a database

#     Provide the answer as a simple list with a brief description in a language addressed to C-level or company management user personas.  Provide it in code format ready to be entered on a mysql table of a database
#     You must present this information in the following XML format:

    # <RESPONSE>
    #     <BUSINESS_AREA_NAME>
    #         <NAME>name of business area</NAME>
    #         <DESCRIPTION>description of business area</DESCRIPTION>
    #     </BUSINESS_AREA_NAME>
    #     <!-- Repeat the INDUSTRY_CATEGORY structure for each industry category -->
    # </RESPONSE>
#     Remember to include all identified industry categories and ensure strict adherence to the XML structure.
#     IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
#     CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult

#     """

#     return prompt