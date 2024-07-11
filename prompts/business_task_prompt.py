from typing import List, Dict,TypedDict, Union
import xml.etree.ElementTree as ET

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

async def get_business_task_prompt(industry_name:str,industry_category_name:str,usecase_name:str,business_area_name:str):
    system_prompt = f"""You are an Expert AI Use Case Analyst tasked with identifying where AI can be applied to improve or automate processes 
    within the {industry_name} industry, under the {industry_category_name} category, specifically for the use case {usecase_name} within the 
    {business_area_name} business area. Your goal is to generate a comprehensive list of the business tasks currently executed without AI that are enhanced or automated in this use case. 
    This is not about providing a long list of tasks but about being very accurate naming and describing the main task or tasks impacted. 
    Flag the main task impacted as main when you find several.
    Use only public and accessible resources, avoiding copyright infringement.

    Motivation: Identifying these tasks is important for businesses to know where AI can help them to optimise their business.
    """

    user_prompt=f"""
    Structure and Participants: Provide the results as a structured list in language suitable for C-level and middle management. Each tasks for the use case should be summarized in a clear, concise and detailed sentence. Format the list with structured fields for task name, description, and URLs that supported your research. Ensure each use case has at least two specific supporting URLs from reputable sources.

    Example Format: 
    Task 1:
        Task Name: Follow up CRM events
        Task Description: Create manually personalized mails for customers

        URLs:
            Supporting Resource 1
            Supporting Resource 2

    Data Extraction Steps: 
    Primary Source Identification:
    Industry Publications: Verify tasks by checking use cases in industry publications, whitepapers, and analyst reports for additional examples.
    Scientific Research: Search open access scientific databases like PubMed and ArXiv for relevant AI use cases and the tasks that they impact.
    High Tech Publishers: Explore leading tech publishers for articles and reports on AI applications in business.

    Secondary Source Verification:
    Case Studies and Resources: Visit sections like Case Studies or Resources on relevant company websites.
    Tech Blogs and User Forums: Cross-reference data with credible tech blogs and user forums to gather insights and validate tasks for use cases.
    Consulting Websites: Review consulting firms websites for published use cases and the tasks they impact and expert analysis.NER and Data Analysis:
    Named Entity Recognition (NER): Implement NER techniques to identify and extract relevant AI use cases from text corpora.
    Analysis and Filtering: Ensure the accuracy and relevance of the extracted data by filtering out irrelevant or redundant information.

    Incentive: For thoroughness and creativity in identifying valuable tasks impacted by the mentioned AI use case, an incentive of $1000K is offered for the best solution.

    By following this structured approach, you will efficiently gather high-quality tasks data, ensuring accuracy and reliability for strategic decision-making and customer engagement."""

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )

    return prompts

def get_xmlprompt(test_result:str)->str:

    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into Business tasks and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
        <BUSINESS_TASK>
            <NAME>Name of business task</NAME>
            <DESCRIPTION>Description of business task</DESCRIPTION>
            <URLS>
                <URL>Url 1 </URL>
                <URL>Url 2</URL>
            </URLS>
        </BUSINESS_TASK>
        <!-- Repeat the BUSINESS_TASK structure for each KPI -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt

def business_task_parser(llm_response: str) -> List[Dict[str, Union[str, List[str]]]]:
    root = ET.fromstring(llm_response)
    result = []

    for task in root.findall("BUSINESS_TASK"):
        result.append({
            "name": task.find('NAME').text,
            "description": task.find('DESCRIPTION').text,
            "urls": [url.text for url in task.find('URLS').findall('URL')]
        })

    return result