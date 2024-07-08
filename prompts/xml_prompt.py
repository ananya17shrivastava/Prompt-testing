from db.mysql import fetch_prompt
def get_xmlprompt(test_result:str)->str:
    # prompts = fetch_prompt("xml_prompt")
    # prompts['user_prompt'] = prompts['user_prompt'].replace("{{test_result}}", test_result)
    # return prompts['user_prompt']
    xml_prompt=f"""
    You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into industry categories and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
        <INDUSTRY_CATEGORY>
            <NAME>name of category</NAME>
            <DESCRIPTION>description of category</DESCRIPTION>
        </INDUSTRY_CATEGORY>
        <!-- Repeat the INDUSTRY_CATEGORY structure for each industry category -->
    </RESPONSE>

    Follow these steps to process and present the information:

    1. Carefully analyze the test result to identify distinct industry categories.
    2. For each industry category you identify:
    a. Create an <INDUSTRY_CATEGORY> element.
    b. Within it, add a <NAME> element containing the name of the category.
    c. Add a <DESCRIPTION> element with a brief description of the category.
    3. Ensure that all identified categories are included in your response.

    It is crucial that you send the response in strict XML format. Do not include any text outside the XML structure. The entire response should be valid XML.

    Here's an example of how your output should be structured:

    <RESPONSE>
        <INDUSTRY_CATEGORY>
            <NAME>Technology</NAME>
            <DESCRIPTION>Companies involved in the development and manufacturing of electronic devices, software, and related services.</DESCRIPTION>
        </INDUSTRY_CATEGORY>
        <INDUSTRY_CATEGORY>
            <NAME>Healthcare</NAME>
            <DESCRIPTION>Organizations that provide medical services, develop pharmaceuticals, or manufacture medical equipment.</DESCRIPTION>
        </INDUSTRY_CATEGORY>
    </RESPONSE>

    Remember to include all identified industry categories and ensure strict adherence to the XML structure.
    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult
    """
    return xml_prompt