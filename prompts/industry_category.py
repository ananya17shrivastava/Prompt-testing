from typing import List, Dict, TypedDict
import xml.etree.ElementTree as ET


def get_prompt(industry: str):
    prompt = f"""
    Acting as an expert analyst please provide me a list of industry categories based on the product or services provided for the {industry} industry.
    Avoid assumptions and use the most acknowledged categorization in expert research
    Follow these guidelines:

    1. Use only widely acknowledged categorizations from expert research.
    2. Avoid making assumptions or using personal opinions.
    3. Provide a brief, original description for each category
    4. Tailor the language to be suitable for C-level executives and company management.
    5. Ensure all descriptions are original and free from plagiarism.
    6. Make sure descriptions are brief and short."""

    if "retail" in industry.lower():
        prompt += """
            7. Provide at least 30 categories or more
        """

    prompt += f"""
    Present your answer in the following XML format:

    <RESPONSE>
        <INDUSTRY_CATEGORY>
            <NAME>name of category</NAME>
            <DESCRIPTION>description of category</DESCRIPTION>
        </INDUSTRY_CATEGORY>
        <!-- Repeat the INDUSTRY_CATEGORY structure for each industry category -->
    </RESPONSE>

    Based on this request, create a comprehensive list of industry categories for the {industry} sector. Ensure each category has a clear, concise name and an original description that explains its role in the industry. Remember to use language appropriate for high-level business executives and avoid any form of plagiarism in your descriptions.
    And its important to just send the response in strict xml format noting else must be there in response"""

    return prompt

class IndustryCategory(TypedDict):
    name: str
    description: str

def parser(llm_response: str) -> List[IndustryCategory]:
    root = ET.fromstring(llm_response)
    result = []

    for category in root.findall("INDUSTRY_CATEGORY"):
        name = category.find('NAME').text
        value = category.find('DESCRIPTION').text
        # print(f"Name: {name}, Value: {value}")
        result.append({"name": name, "description": value})

    return result
