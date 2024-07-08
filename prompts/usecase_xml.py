
def get_xmlprompt(test_result:str)->str:
    # prompts = fetch_prompt("usecase_xml")
    # prompts['user_prompt'] = prompts['user_prompt'].replace("{{test_result}}", test_result)
    # return prompts['user_prompt']
    prompt = f"""You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into usecases and present it in a structured manner.
    Here is the test result you will be working with:
    <test_result>
    {test_result}
    </test_result>
    You must present this information in the following XML format:
    <RESPONSE>
        <USECASE>
            <NAME>name of business area</NAME>
            <DESCRIPTION>description of business area</DESCRIPTION>
            <URLS>
                <URL>url1</URL>
                <URL>url2</URL>
                <!-- Repeat URL tag for each URL -->
            </URLS>
        </USECASE>
        <!-- Repeat the USECASE structure for each usecase -->
    </RESPONSE>
    IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure.
    CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult. Use &amp; for ampersands, &lt; for <, and &gt; for > within text content."""

    return prompt



# def get_xmlprompt(test_result: str) -> str:
#     user_prompt, system_prompt = fetch_prompt("usecase_xml")
    
#     user_prompt = user_prompt.replace("{{test_result}}", test_result)
    
#     return user_prompt




# You are tasked with presenting test results in a specific XML format. Your goal is to organize the information into usecases and present it in a structured manner.

# Here is the test result you will be working with:

# <test_result>
# {{test_result}}
# </test_result>

# You must present this information in the following XML format:

# <RESPONSE>
#     <USECASE>
#         <NAME>name of business area</NAME>
#         <DESCRIPTION>description of business area</DESCRIPTION>
#     </USECASE>
#     <!-- Repeat the BUSINESS structure for each usecase -->
# </RESPONSE>
# IMPORTANT: It's crucial to send the response in strict XML format. No additional text should be included outside the XML structure
# CRITICAL: Do not use any unescaped ampersand (&) character in the file or any other character that makes parsing of xml document difficult


# Acting as an expert analyst provide me as many use cases as you 
# find where AI can be used to improve or automate processes in the {{industry_name}} industry, {{industry_category_name}} category, {{business_area_name}} 
# Provide only those unique to {{business_area_name}} and avoid those not unique to it. 
# Avoid copyright infringement. Use only public resources.

# system_prompt= You are an Expert AI Use Case Analyst tasked with identifying where AI can be applied to improve or automate processes within the {{industry_name}} industry,
# under the {{industry_category_name}} category, specifically within the {{business_area_name}}  business area. 
# Your goal is to generate a comprehensive list of unique AI use cases tailored exclusively to {{business_area_name}}. 
# Avoid listing use cases that are not unique to this business area. Use only public and accessible resources, avoiding copyright infringement.
# Motivation:
# Identifying these AI use cases is crucial for leveraging technology to optimize operations, increase efficiency, and drive innovation in {{business_area_name}}
    



# user_prompt=Provide the results as a list in language suitable for C-level and middle management. Each use case should be summarized in a clear, concise sentence. Format the list for direct entry into a MySQL database, ensuring each entry is structured with fields for use case name, description, and supporting URLs. Ensure each use case has at least two specific supporting URLs from reputable sources.
# Example Format:
# Use Case 1:
# Name: Predictive Maintenance
# Description: Implement AI algorithms to predict equipment failures for proactive maintenance scheduling
# URLs:
# Supporting Resource 1
# Supporting Resource 2
# Supporting Resource 3


# Data Extraction Steps:
# Primary Source Identification:
# Industry Publications: Verify use cases by checking industry publications, whitepapers, and analyst reports for additional examples.
# Scientific Research: Search open access scientific databases like PubMed and ArXiv for relevant AI use cases.
# High Tech Publishers: Explore leading tech publishers for articles and reports on AI applications.
# Secondary Source Verification:
# Case Studies and Resources: Visit sections like Case Studies or Resources on relevant company websites.
# Tech Blogs and User Forums: Cross-reference data with credible tech blogs and user forums to gather insights and validate use cases.
# Consulting Websites: Review consulting firms' websites for published use cases and expert analyses.
# NER and Data Analysis:
# Named Entity Recognition (NER): Implement NER techniques to identify and extract relevant AI use cases from text corpora.
# Analysis and Filtering: Ensure the accuracy and relevance of the extracted data by filtering out irrelevant or redundant information.
# Incentive:
# For thoroughness and creativity in identifying valuable AI use cases, an incentive of $300K is offered for the best solution.
# By following this structured approach, you will efficiently gather high-quality use case data, ensuring accuracy and reliability for strategic decision-making and customer engagement.