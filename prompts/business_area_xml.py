from db.mysql import fetch_prompt
def get_xmlprompt(test_result:str):
    prompts = fetch_prompt("business_area_xml")
    prompts[0] = prompts[0].replace("{{test_result}}", test_result)
    return prompts[0]





# You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into business areas and present it in a structured manner.

# Here is the test result you will be working with:

# <test_result>
# {{test_result}}
# </test_result>

# You must present this information in the following XML format:

# <RESPONSE>
#     <BUSINESS_AREA_NAME>
#         <NAME>name of business area</NAME>
#         <DESCRIPTION>description of business area</DESCRIPTION>
#     </BUSINESS_AREA_NAME>
#     <!-- Repeat the BUSINESS structure for each industry category -->
# </RESPONSE>
# IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
# CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult