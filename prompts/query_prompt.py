import xml.etree.ElementTree as ET
from typing import Dict, Optional, TypedDict

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_query_prompt(statement:str):
    system_prompt = f"""cting as an expert business and software analyst classify the statement or question provided by the user as related one of the following categories:
    1. Metrics, KPIs
    2. Software capabilities
    3. Use cases 
    4. Use cases for a specific business area
    5. Business task that can be improved or automated
    6. Return of Investment
    Identify the specific value from the category the user inquires about. 
    Examples:
    - if the user asks how to increase, reduce, multiply, improve a value, classify the statement as category 1
    - If the user asks specifically about tools, softwares, features, products or existing options in the market to functionally perform a task with AI classify it as category 2...
    - If the user ask for use cases classify it as category 3 and extract the specific use case object of the statement or question
    - If the user mentions a business area or want to filter by a business area, department or job function classify it as category 4 and extract the business area or business areas inferred from the question
    - If the user mentions a specific job task or want to filter by a job task he performs classify it as category 5 and extract the task he performs
    - If the user ask about initiatives based on higher economic impact, ROI classify it as category 6 and extract what kind of use cases want to achieve and total economic impact
    Be accurate. Factual.

    You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into KPIs and present it in a structured manner.
    You must present this information in the following XML format:

    <RESPONSE>
        <CATEGORY>
            Name of category
        </CATEGORY>
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult
    """
    user_prompt=f"""
    This my statement or question:
    {statement}
    """

 

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )

    return prompts



def filter_parser(xml_response: str) -> Optional[Dict[str, str]]:
    try:
        root = ET.fromstring(xml_response)
        result = {}

        category = root.find("CATEGORY")
        if category is not None and category.text:
            # Strip any leading/trailing whitespace and extract the category number
            category_text = category.text.strip()
            category_parts = category_text.split('.', 1)
            if len(category_parts) == 2:
                result["category_number"] = category_parts[0].strip()
                result["category_description"] = category_parts[1].strip()
            else:
                result["category_description"] = category_text

        return result if result else None

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

