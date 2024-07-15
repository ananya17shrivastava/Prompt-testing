from botocore.exceptions import ClientError
import logging
import boto3
import jsonpickle
from lllms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_PERPLEXITY
from lllms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from lllms.perplexity import PERPLEXITY_MODEL
import time
from typing import List
import json
from urllib.parse import urlparse
import os

from db.mysql import create_db_connection, feed_kpi
from db.fetchprompts import connect_langfuse
from lambda_prompts.kpi_prompt import get_kpi_prompt, get_xmlprompt,kpi_parser


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
langfuse=connect_langfuse(secrets['LANGFUSE_SECRET_KEY'],secrets['LANGFUSE_PUBLIC_KEY'])



PERPLEXITY_API_KEY = secrets['PERPLEXITY_API_KEY']
ANTHROPIC_API_KEY=secrets['ANTHROPIC_API_KEY']


def check_db_kpi(solution_id: str,case_id:str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM impact_kpis
        WHERE solution_id = %s AND case_id=%s
        """
        my_cursor.execute(check_query, (solution_id,case_id))
        existing_records = my_cursor.fetchall()

        return len(existing_records) > 0
    finally:
        if my_cursor:
            my_cursor.close()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))

    print(event)
    for record in event['Records']:
        
        start_time_whole = time.time()
        
        message_body = record['body']
        
        parsed_message=json.loads(message_body)
        message_type = parsed_message.get('type', '')
        if 'kpi' not in message_type.lower():
            continue

        solution_id=parsed_message.get('solution_id', 'N/A')
        solution_name=parsed_message.get('solution_name', 'N/A')
        case_id=parsed_message.get('use_case_id', 'N/A')
        usecase_name=parsed_message.get('use_case_name', 'N/A')
        usecase_description=parsed_message.get('use_case_description', 'N/A')
        industry_category_name=parsed_message.get('industry_category_name', 'N/A')
        industry_name=parsed_message.get('industry_name', 'N/A')
        

        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        try:
            validation = check_db_kpi(solution_id,case_id, conn)
            if validation:
                print("kpi already exists !")
                continue
        finally:
            if conn:
                conn.close()


        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL
        prompts=get_kpi_prompt(solution_name,usecase_name,usecase_description,industry_category_name,industry_name)
        user_prompt = prompts['user_prompt']
        system_prompt = prompts['system_prompt']
        start_time_perplexity = time.time()
        description_result = invoke_llm(provider, model, [{
            "role": "user",
            "content": user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt,API_KEY=PERPLEXITY_API_KEY)
        print("--- %s Time for PERPLEXITY  ---" % (time.time() - start_time_perplexity))
        # print(description_result)



        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3
        xml_prompt=get_xmlprompt(description_result)
        start_time_claude = time.time()
        result= invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
        }], max_tokens=4096, temperature=0,prompt_id="ai_solutions",API_KEY=ANTHROPIC_API_KEY)
        print("--- %s Time for CLAUDE  ---" % (time.time() - start_time_claude))
        result = result.replace("&", "&amp;")
        json_result = kpi_parser(result)

        # print("\nStrategic Indicator KPIs:")

        for kpi in json_result['strategic_kpis']:
            name=kpi['kpi_name']
            description=kpi['kpi_description']
            effect=kpi['effect']
            unit=kpi['unit']
            expected_impact=kpi['expected_impact']
            urls=kpi['urls']
            type='Strategic KPI'
            conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
            feed_kpi(solution_id,case_id,name, description, effect, unit, expected_impact, urls, type,conn)
            conn.close()

        # print("\nLead Indicator KPIs:")
        for kpi in json_result['lead_indicator_kpis']:
            name=kpi['kpi_name']
            description=kpi['kpi_description']
            effect=kpi['effect']
            unit=kpi['unit']
            expected_impact=kpi['expected_impact']
            urls=kpi['urls']
            type='Lead Indicator KPI'
            conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
            feed_kpi(solution_id,case_id,name, description, effect, unit, expected_impact, urls, type,conn)
            conn.close()
        
        print("--- %s Time for ONE ITERATION ---" % (time.time() - start_time_whole))
    result = {
        'statusCode': 200,
    }
    return result
