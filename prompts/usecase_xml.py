from db.mysql import fetch_prompt

def get_xmlprompt(test_result:str)->str:
    prompts = fetch_prompt("usecase_xml")
    prompts['user_prompt'] = prompts['user_prompt'].replace("{{test_result}}", test_result)
    return prompts['user_prompt']


# def get_xmlprompt(test_result: str) -> str:
#     user_prompt, system_prompt = fetch_prompt("usecase_xml")
    
#     user_prompt = user_prompt.replace("{{test_result}}", test_result)
    
#     return user_prompt




# You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into usecases and present it in a structured manner.

# Here is the test result you will be working with:

# <test_result>
# {{test_result}}
# </test_result>

# You must present this information in the following XML format:

# <RESPONSE>
#     <USECASE>
#         <NAME>name of business area</NAME>
#         <DESCRIPTION>description of business area</DESCRIPTION>
#     </USECASE>
#     <!-- Repeat the BUSINESS structure for each usecase -->
# </RESPONSE>
# IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
# CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult