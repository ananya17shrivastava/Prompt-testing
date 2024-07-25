from botocore.exceptions import ClientError
import logging
import boto3
import jsonpickle
import json
import os

from lambda_prompts.query_prompt import get_query_prompt,filter_parser
from lllms.index import invoke_llm, LLM_PROVIDER_CLAUDE
from lllms.claude import CLAUDE_SONNET_35


from Pinecone.Pinecone_business_query import query_business_pinecone, print_business_results
from Pinecone.Pinecone_usecase_query import query_usecase_pinecone, print_usecase_results
from Pinecone.Pinecone_kpi_query import query_kpi_pinecone, print_kpi_results


logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')


def get_secret():

    secret_name = "llmapp"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # print(get_secret_value_response)
    secret = get_secret_value_response['SecretString']
    secretJSON = json.loads(secret)
    return secretJSON


secrets = get_secret()


logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info(f"Event: {event}")

    query_parameters = event.get('queryStringParameters', {})
    query_text = query_parameters.get('message', 'No message provided')

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

    logger.info(f"Received message: {query_text}")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': f"Processed message: {query_text}"})
    }
    
   
