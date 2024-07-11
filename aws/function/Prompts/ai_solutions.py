
from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_aisolutions_prompt(usecase_name: str, usecase_description: str, industry_name: str, industry_category_name: str):
    system_prompt = f"""You are an Expert Software Analyst tasked with identifying what are the best software solutions for the following use case:
    {usecase_name}
    {usecase_description}

    You need to provide the Software solutions that best apply to that use case for the {industry_name} industry and {industry_category_name} industry category. Your goal is to generate a completely accurate list of software solutions with their website url.
    Exclude those solutions not mentioning specifically this use case on their website, resources, case studies or blogs.

    Motivation:
    Identifying these software solutions is crucial for leveraging technology to optimize operations, increase efficiency, and drive innovation in the {industry_category_name} category of the {industry_name} industry
    """

    user_prompt=f"""
    Structure and Participants:
    Provide the results as a list of the URLs of the solutions. 

    Example Format:

    Use Case 1:
    Name of the solution: vistasocial.com 
    website URL: https://vistasocial.com/


    Data Extraction Steps:

    Primary Source Identification:
    Industry Publications: Verify which software solutions apply to this use case by checking industry publications, whitepapers, and analyst reports for additional examples.
    Scientific Research: Search open access scientific databases like PubMed and ArXiv for relevant mentions about software solutions for the AI use case.
    High Tech Publishers: Explore leading tech publishers for articles and reports on AI applications and softwares.

    Secondary Source Verification:
    Case Studies and Resources: Visit sections such as: Case Studies, Resources, blogs… on relevant company websites.
    Tech Blogs and User Forums: Cross-reference data with credible tech blogs and user forums to find software solutions mentions.
    Consulting Websites: Review the websites of consulting firms for published use cases and expert analyses.

    NER and Data Analysis:

    Named Entity Recognition (NER): Implement NER techniques to identify and extract relevant AI use cases from text corpora.
    Analysis and Filtering: Ensure the accuracy and relevance of the extracted data by filtering out irrelevant or redundant information.

    Incentive:
    For thoroughness and creativity in identifying valuable software solutions, an incentive of $1000 is offered for the best solution.

    By following this structured approach, you will efficiently gather high-quality data, ensuring accuracy and reliability for strategic decision-making and customer engagement."""

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )

    return prompts


def get_competitor_prompt(description_result:str):
    system_prompt=f"""Please, provide a list of competitors software solutions to {description_result}"""

    user_prompt=f"""
    Exclude from your research comparator websites such as trustpilot, capterra or G2.
    Provide them an exhaustive list of urls without limitation of the number of results

    Software solution 1:
    Name of the solution: vistasocial.com
    URLs: http://vistasocial.com/

    """

    prompts = Prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )
    return prompts




def get_xmlprompt(test_result:str)->str:

    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into ai solutions and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
    <SOLUTION>
        <NAME>name of solution</NAME>
        <URL>Url of solution</URL>
    </SOLUTION>
    <!-- Repeat the SOLUTION structure for each solution -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt


def aisolutions_parser(llm_response:str)->List[Dict[str, str]]:
    root = ET.fromstring(llm_response)
    result = []

    for usecase in root.findall("SOLUTION"):
        name = usecase.find('NAME')
        urls = usecase.find('URL')
        result.append({
            "name": name.text.strip(),
            "urls": urls.text.strip()
        })
        
       
            

    return result