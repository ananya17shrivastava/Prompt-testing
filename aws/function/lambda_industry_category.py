from botocore.exceptions import ClientError
import logging
import boto3
import jsonpickle
from lllms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_PERPLEXITY
from lllms.claude import CLAUDE_HAIKU_3
from lllms.perplexity import PERPLEXITY_MODEL
import time
from typing import List
import json
import os
from lambda_prompts.industry_category import get_prompt, get_xmlprompt, parser as industry_parser
from db.mysql import  create_db_connection,insert_industry_category
from db.fetchprompts import connect_langfuse


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


PERPLEXITY_API_KEY = secrets['PERPLEXITY_API_KEY_2']
ANTHROPIC_API_KEY=secrets['ANTHROPIC_API_KEY']


def check_db_industry_category(industry_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM industry_categories
        WHERE industry_id = %s 
        """
        my_cursor.execute(check_query, (industry_id,))
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

        if 'industry' not in message_type.lower():
            print("Not related to industry category lambda function!!")
            continue

        industry_name=parsed_message.get('industry_name', 'N/A')
        industry_id=parsed_message.get('industry_id', 'N/A')


        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        try:
            validation = check_db_industry_category(industry_id, conn)
            if validation:
                print("industry category already exists !")
                continue
        finally:
            if conn:
                conn.close()
        
        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL

        prompts=get_prompt(industry_name,langfuse)
            
        user_prompt = prompts['user_prompt']
        system_prompt = prompts['system_prompt']

        # print(system_prompt)
        start_time_perplexity = time.time()
        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        description_result = invoke_llm(conn,provider, model, [{
            "role": "user",
            "content": user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="industry_category",system_prompt=system_prompt,API_KEY=PERPLEXITY_API_KEY)

        conn.close()
        print("--- %s Time for PERPLEXITY  ---" % (time.time() - start_time_perplexity))


        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3


        xml_prompt=get_xmlprompt(description_result)
        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        start_time_claude = time.time()
        xml_result= invoke_llm(conn,provider, model, [{
            "role": "user",
            "content": xml_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="industry_category_xml",API_KEY=ANTHROPIC_API_KEY)
        print("--- %s Time for CLAUDE ---" % (time.time() - start_time_claude))
        conn.close()

        xml_result = xml_result.replace("&", "&amp;")
        json_result = industry_parser(xml_result)

        # print(json_result)

        for industry_result in json_result:
            name = industry_result["name"]
            product_services = industry_result["description"]
            if len(industry_id) > 0:
                conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
                insert_industry_category(industry_id, name, product_services,conn)
                conn.close()


        print("--- %s Time for ONE ITERATION ---" % (time.time() - start_time_whole))
        
    result = {
        'statusCode': 200,
    }
    return result
