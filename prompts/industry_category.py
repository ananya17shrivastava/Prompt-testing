from typing import List, Dict
import xml.etree.ElementTree as ET
from db.mysql import get_industryid,insert_industry_category

def get_prompt(industry: str):
    prompt = f"""
    You are an expert analyst tasked with creating a list of industry categories for the {industry} industry.
    Your goal is to provide a comprehensive and accurate list based on products and services offered in this sector.
    Follow these guidelines:

    1. Use only widely acknowledged categorizations from expert research.
    2. Avoid making assumptions or using personal opinions.
    3. Provide a brief, original description for each category
    4. Tailor the language to be suitable for C-level executives and company management.
    5. Ensure all descriptions are original and free from plagiarism.
    6. Make sure descriptions are brief.

    Present your answer in the following XML format:

    <RESPONSE>
        <INDUSTRY_CATEGORY>
            <NAME>name of category</NAME>
            <DESCRIPTION>description of category</DESCRIPTION>
        </category>
        </INDUSTRY_CATEGORY>
        <!-- Repeat the category structure for each industry category -->
    </RESPONSE>

    Based on this request, create a comprehensive list of industry categories for the {industry} sector. Ensure each category has a clear, concise name and an original description that explains its role in the industry. Remember to use language appropriate for high-level business executives and avoid any form of plagiarism in your descriptions.
    And its important to just send the response in strict xml format noting else must be there in response"""

    return prompt


def parser(llm_response: str, industryname: str) -> List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    industry_id=get_industryid(industryname)

    for category in root.findall("INDUSTRY_CATEGORY"):
        name = category.find('NAME').text
        value = category.find('DESCRIPTION').text
        
        insert_industry_category(industry_id,name,value)
        
        result.append({"name": name, "description": value})



    return result