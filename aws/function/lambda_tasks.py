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
from urllib.parse import urlparse
import os


from db.mysql import  create_db_connection,insert_tasks
from db.fetchprompts import connect_langfuse
from Prompts.business_task_prompt import get_business_task_prompt, get_xmlprompt,business_task_parser


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


def check_db(case_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM tasks
        WHERE case_id = %s 
        """
        my_cursor.execute(check_query, (case_id,))
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
        if 'tasks' not in message_type.lower():
            continue

        case_id=parsed_message.get('use_case_id', 'N/A')
        usecase_name=parsed_message.get('use_case_name', 'N/A')
        business_area_name=parsed_message.get('business_area_name', 'N/A')
        industry_name=parsed_message.get('industry_name', 'N/A')
        industry_category_name=parsed_message.get('industry_category_name', 'N/A')
        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        try:
            validation_id = check_db(case_id, conn)
            if validation_id:
                print("solution already exists !")
                continue
        finally:
            if conn:
                conn.close()
        
        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL
        prompts=get_business_task_prompt(industry_name, industry_category_name, usecase_name,business_area_name)
        user_prompt = prompts['user_prompt']
        system_prompt = prompts['system_prompt']
        # print(system_prompt)
        start_time_perplexity = time.time()
        description_result=invoke_llm(provider, model, [{
            "role": "user",
            "content": user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_tasks",system_prompt=system_prompt,API_KEY=PERPLEXITY_API_KEY)
        print("--- %s Time for PERPLEXITY  ---" % (time.time() - start_time_perplexity))
        print("DESCRIPTION RESULT !!")
        print(description_result)

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
        json_result = business_task_parser(result)
        print("BUSINESS RESULTS are :::")
        print(json_result)

        start_time_insert = time.time()
        for task_result in json_result:
            name=task_result['name']
            description=task_result['description']
            urls=task_result['urls']
            conn=create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
            print(f"Inserting business task: {task_result}")
            insert_tasks(name,description,urls,case_id,conn)
            conn.close()
        print("--- %s Time for one loop insertion ---" % (time.time() - start_time_insert))

        # json_result = json.dumps(json_result, indent='\t')    
        # print(json_result)
        print("--- %s Time for ONE ITERATION ---" % (time.time() - start_time_whole))
        
    result = {
        'statusCode': 200,
    }
    return result
