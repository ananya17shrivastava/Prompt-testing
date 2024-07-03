from typing import List, Dict
import xml.etree.ElementTree as ET


def get_systemprompt(industry: str):
    system_prompt=f"""Acting as an expert analyst please provide me a list of industry categories based on the product or services provided for the {industry} industry.
    Avoid assumptions and use the most acknowledged categorization in expert research"""
    return system_prompt

def get_prompt():

    base_prompt=f"""
    Provide the answer as a comprehensive list. Describe each of them in a language addressed to C-level or company management user personas.
    Each description needs to be original and not fall into plagiarism.
    """
    return base_prompt

def get_xmlprompt(test_result:str):
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

    Now, begin your response by presenting the test result in the required XML format. Remember to include all identified industry categories and ensure strict adherence to the XML structure.
    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&) character in the file.
    """

    return xml_prompt


#     base_prompt = f"""
#     You are an expert analyst tasked with creating a list of industry categories based on the product or services provided for the {industry} industry.
#     Your goal is to provide a exhaustive and accurate list based on products and services offered in this sector.
#     Follow these guidelines:

#     1. Use only widely acknowledged categorizations from expert research.
#     2. Avoid making assumptions or using personal opinions.
#     3. Provide a brief, original description for each category
#     4. Tailor the language to be suitable for C-level executives and company management.
#     5. Ensure all descriptions are original and free from plagiarism.
#     6. Make sure descriptions are brief and short."""

#     if "retail" in industry.lower():
#         base_prompt += """
#     7. Provide at least 30 categories or more
# """

#     base_prompt += f"""
#     Present your answer in the following XML format:

#     <RESPONSE>
#         <INDUSTRY_CATEGORY>
#             <NAME>name of category</NAME>
#             <DESCRIPTION>description of category</DESCRIPTION>
#         </INDUSTRY_CATEGORY>
#         <!-- Repeat the INDUSTRY_CATEGORY structure for each industry category -->
#     </RESPONSE>

#     Based on this request, create a comprehensive list of industry categories for the {industry} sector. Ensure each category has a clear, concise name and an original description that explains its role in the industry. Remember to use language appropriate for high-level business executives and avoid any form of plagiarism in your descriptions.
#     IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure.
#     """

    # return base_prompt


def parser(llm_response: str) -> List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    for category in root.findall("INDUSTRY_CATEGORY"):
        name = category.find('NAME').text
        value = category.find('DESCRIPTION').text
        # print(f"Name: {name}, Value: {value}")
        result.append({"name": name, "description": value})

    return result
