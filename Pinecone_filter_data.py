from prompts.query_prompt import get_query_prompt,filter_parser
from llms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_GPT, LLM_PROVIDER_PERPLEXITY
from llms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from llms.gpt import GPT4_MODEL
from llms.perplexity import PERPLEXITY_MODEL

from Pinecone_usecase_query import query_usecase_pinecone, print_usecase_results
from Pinecone_kpi_query import query_kpi_pinecone, print_kpi_results
from Pinecone_business_query import query_business_pinecone, print_business_results


query_text="I'm a retail owner find usecases for me !"

prompts=get_query_prompt(query_text)
user_prompt = prompts['user_prompt']
system_prompt = prompts['system_prompt']

provider=LLM_PROVIDER_CLAUDE
model = CLAUDE_SONNET_35

description_result = invoke_llm(provider, model, [{
    "role": "user",
    "content": user_prompt,
}], max_tokens=4096, temperature=.2,prompt_id="data_category",system_prompt=system_prompt)
# print(description_result)

description_result = description_result.replace("&", "&amp;")
json_result = filter_parser(description_result)
# print(json_result)


category_number=json_result['category_number']
category_description=json_result['category_description']
# print(category_number)


if category_number=='1' or category_number=='2':
    results=query_kpi_pinecone(query_text)
    print_kpi_results(results['matches'], query=query_text)
elif category_number=='3' or category_number=='4':
    results=query_usecase_pinecone(query_text)
    print_usecase_results(results['matches'],query=query_text)
elif category_number=='5':
    results=query_business_pinecone(query_text)
    print_business_results(results['matches'],query=query_text)
else:
    print("category not developed !!")



print(json_result)







