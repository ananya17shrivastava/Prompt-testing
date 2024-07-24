from typing import List, Dict,TypedDict
import xml.etree.ElementTree as ET
from db.fetchprompts import fetch_prompt

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def get_kpi_prompt(solution_name:str,usecase_name:str,usecase_description:str,industry_category_name:str,industry_name:str,langfuse)->Prompt:
    prompts =fetch_prompt("kpi_prompt",langfuse)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{solution_name}}",solution_name)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_name}}",usecase_name)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{usecase_description}}",usecase_description)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_category_name}}",industry_category_name)
    prompts['system_prompt']=prompts['system_prompt'].replace("{{industry_name}}",industry_name)
    # print("KPI PROMPTS ARE :::")
    # print(prompts)
    return prompts

def get_xmlprompt(test_result:str)->str:

    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into KPIs and present it in a structured manner.

    Here is the test result you will be working with:

    <test_result>
    {test_result}
    </test_result>

    You must present this information in the following XML format:

    <RESPONSE>
        <STRATEGIC_KPI>
            <KPI_NAME>name of KPI</KPI_NAME>
            <KPI_DESCRIPTION>KPI description</KPI_DESCRIPTION>
            <EFFECT>Effect of kpi</EFFECT>
            <UNIT>Unit of kpi</UNIT>
            <EXPECTED_IMPACT>Expected impact of kpi</EXPECTED_IMPACT>
            <URLS>
                <URL></URL>
                <URL></URL>
                <URL></URL>
            </URLS>
        </STRATEGIC_KPI>
        <LEAD_INDICATOR_KPI>
            <KPI_NAME>name of KPI</KPI_NAME>
            <KPI_DESCRIPTION>KPI description</KPI_DESCRIPTION>
            <EFFECT>Effect of kpi</EFFECT>
            <UNIT>Unit of kpi</UNIT>
            <EXPECTED_IMPACT>Expected impact of kpi</EXPECTED_IMPACT>
            <URLS>
                <URL></URL>
                <URL></URL>
                <URL></URL>
            </URLS>
        </LEAD_INDICATOR_KPI>
        <!-- Repeat the STRATEGIC_KPI and LEAD_INDICATOR_KPI structure for each KPI -->
    </RESPONSE>

    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
    CRITICAL: Do not use any unescaped ampersand (&amp;) character in the file or any other character that makes parsing of xml document difficult"""

    return prompt


def kpi_parser(xml_response: str) -> Dict[str, List[Dict[str, str]]]:
    root = ET.fromstring(xml_response)
    result = {
        "strategic_kpis": [],
        "lead_indicator_kpis": []
    }

    for kpi_type in ["STRATEGIC_KPI", "LEAD_INDICATOR_KPI"]:
        for kpi in root.findall(kpi_type):
            kpi_data = {}
            for element in kpi:
                if element.tag == "URLS":
                    kpi_data[element.tag.lower()] = [url.text.strip() for url in element.findall("URL")]
                else:
                    kpi_data[element.tag.lower()] = element.text.strip()
            
            if kpi_type == "STRATEGIC_KPI":
                result["strategic_kpis"].append(kpi_data)
            else:
                result["lead_indicator_kpis"].append(kpi_data)

    return result




# You are an Expert AI Business Use Case and Software Analyst tasked with identifying what KPIs are impacted and what is the amount of the impact 
#     when you apply {{solution_name}} software to the use case {{usecase_name}}-{{usecase_description}} use case for the {{industry_category_name}} category in the {{industry_name}} industry. 
#     Your goal is to generate an accurate list of the KPIs and their expected values as provided by the software provider and expert analysts.
#     This is not about providing a long list of KPIs but about being very accurate naming and describing the impact of those KPIs. 
#     Separate the KPIs into strategic and lead indicator KPIs.
#     Use only public and accessible resources, avoiding copyright infringement.

#     Motivation: Identifying those KPIs is important for businesses to know the ROI of the implementation of a solution for an AI use case.