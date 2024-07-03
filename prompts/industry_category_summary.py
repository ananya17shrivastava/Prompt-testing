from typing import List, Dict
import xml.etree.ElementTree as ET


def get_prompt(industry: str, sources: List[str]):

    source_str = '\n\n'.join(['<source{}>\n{}\n</source{}>\n'.format(idx, source, idx) for idx, source in enumerate(sources)])
    prompt = f"""
    You are an expert analyst tasked with creating a comprehensive list of industry categories for a specific industry. 
    Your goal is to provide an accurate and detailed list based on products and services offered in this sector. Follow these instructions carefully:

    1. You will be given an industry name and three sources of information. The industry you are analyzing is:

    <industry>{industry}</industry>

    2. Here are the three curated lists from different sources:

    {source_str}


    3. Create your list of industry categories following these guidelines:
        a. Choose the best curated list of industry categories from the three sources provided.
        b. Create a concise but accurate list of categories that fully describe the industry.
        c. Ensure categories are not duplicated.
        d. Avoid making assumptions or using personal opinions.
        e. Provide a brief, original description for each category.
        f. Tailor the language to be suitable for C-level executives and company management.
        g. Ensure all descriptions are original and free from plagiarism.
        h. Make sure descriptions are brief and short.

    4. Present your answer in the following XML format:

    <RESPONSE>
        <SCRATCHPAD>your step by step reasoning for every category</SCRATCHPAD>
        <INDUSTRY_CATEGORY>
            <NAME>name of category</NAME>
            <DESCRIPTION>description of category</DESCRIPTION>
        </INDUSTRY_CATEGORY>
        <!-- Repeat the INDUSTRY_CATEGORY structure for each industry category -->
    </RESPONSE>


    5. Final instructions:
   - Create a comprehensive list of industry categories for the specified industry sector.
   - Ensure each category has a clear, concise name and an original description that explains its role in the industry.
   - Use language appropriate for high-level business executives.
   - Avoid any form of plagiarism in your descriptions.
   - Provide your response in strict XML format as specified above, with no additional text outside the XML structure.

   6. Think step by step for every source and category inside source and provide your reasoning in <SCRATCHPAD>
    Begin your analysis and category creation now. Make sure to respond only in XML format don't add any other text outside XML structure.
    
    """

    return prompt


def parser(llm_response: str) -> List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    for category in root.findall("INDUSTRY_CATEGORY"):
        name = category.find('NAME').text
        value = category.find('DESCRIPTION').text
        # print(f"Name: {name}, Value: {value}")
        result.append({"name": name, "description": value})

    return result
