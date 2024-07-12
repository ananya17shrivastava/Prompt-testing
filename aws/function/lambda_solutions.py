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
from mysql.connector import Error
from urllib.parse import urlparse
import os

from lllms.perplexity import call_llm_perplexity

from db.mysql import get_api_key, create_db_connection, insert_solutions, bulk_insert_solutions
from db.fetchprompts import fetch_prompt, connect_langfuse
from Prompts.ai_solutions import get_aisolutions_prompt, get_xmlprompt, get_competitor_prompt, aisolutions_parser


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


# conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])


# if not conn.is_connected():
#     conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])


# PERPLEXITY_API_KEY = get_api_key("PERPLEXITY_API_KEY",conn)
# ANTHROPIC_API_KEY=get_api_key("ANTHROPIC_API_KEY",conn)


PERPLEXITY_API_KEY = secrets['PERPLEXITY_API_KEY']
ANTHROPIC_API_KEY=secrets['ANTHROPIC_API_KEY']

def extract_name_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split by '.' and take all parts except the last if there are more than 2 parts
    parts = domain.split('.')
    if len(parts) > 2:
        name = '.'.join(parts[:-1])
    else:
        name = domain
    return name

def check_db(case_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM case_to_solution
        WHERE case_id = %s 
        """
        my_cursor.execute(check_query, (case_id,))
        existing_records = my_cursor.fetchall()

        return len(existing_records) > 0
    finally:
        if my_cursor:
            my_cursor.close()

def lambda_handler(event, context):


    
    # conn=create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
    # print(conn.is_connected())
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    # print("--- %s seconds ---" % (time.time() - start_time))
    print(event)
    for record in event['Records']:
        
        start_time_whole = time.time()
        
        message_body = record['body']
        
        parsed_message=json.loads(message_body)
        message_type = parsed_message.get('type', '')
        if 'solutions' not in message_type.lower():
            continue

        case_id=parsed_message.get('use_case_id', 'N/A')
        usecase_name=parsed_message.get('use_case_name', 'N/A')
        usecase_description=parsed_message.get('use_case_description', 'N/A')
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
        prompts=get_aisolutions_prompt(usecase_name,usecase_description,industry_name,industry_category_name)
        user_prompt = prompts['user_prompt']
        system_prompt = prompts['system_prompt']
        start_time_perplexity = time.time()
        description_result=invoke_llm(provider, model, [{
            "role": "user",
            "content": user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt,API_KEY=PERPLEXITY_API_KEY)
        print("--- %s Time for PERPLEXITY 1 ---" % (time.time() - start_time_perplexity))

        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3
        
        xml_prompt=get_xmlprompt(description_result)
        start_time_claude = time.time()
        result= invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
        }], max_tokens=4096, temperature=0,prompt_id="ai_solutions",API_KEY=ANTHROPIC_API_KEY)
        print("--- %s Time for CLAUDE 1 ---" % (time.time() - start_time_claude))
        result = result.replace("&", "&amp;")
        json_result = aisolutions_parser(result)
        json_result = json.dumps(json_result, indent='\t')


        #iteration 2 for getting competitors
        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL
        
        competitor_prompt=get_competitor_prompt(description_result)
        competitor_user_prompt=competitor_prompt['user_prompt']
        competitor_system_prompt=competitor_prompt['system_prompt']
        start_time_perplexity_2 = time.time()
        competitor_result=invoke_llm(provider, model, [{
            "role": "user",
            "content": competitor_user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=competitor_system_prompt,API_KEY=PERPLEXITY_API_KEY)
        print("--- %s Time for PERPLEXITY 2  ---" % (time.time() - start_time_perplexity_2))

        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3
        competitor_xml_prompt=get_xmlprompt(competitor_result)
        start_time_claude_2 = time.time()
        result2=invoke_llm(provider, model, [{
                "role": "user",
                "content": competitor_xml_prompt,
        }], max_tokens=4096, temperature=0,prompt_id="ai_solutions",API_KEY=ANTHROPIC_API_KEY)
        print("--- %s Time for CLAUDE 2 ---" % (time.time() - start_time_claude_2))
        result2 = result2.replace("&", "&amp;")
        competitor_json_result = aisolutions_parser(result2)
        competitor_json_result = json.dumps(competitor_json_result, indent='\t')

        solutions = json.loads(json_result)
        competitors = json.loads(competitor_json_result)

        # Combine the lists
        combined_results = []

        # Iterate over solutions and append to combined_results
        for solution in solutions:
            combined_results.append(solution)

        # Iterate over competitors and append to combined_results
        for competitor in competitors:
            combined_results.append(competitor)
        print("COMBINED _ RESULTS ARE ::")
        print(combined_results)

        for solution in combined_results:
            url=solution['urls']
            name = extract_name_from_url(url)
            start_time_db = time.time()
            conn=create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
            print("--- %s Time for db connection ---" % (time.time() - start_time_db))
            start_time_insert = time.time()
            insert_solutions(case_id,name,url,conn)
            conn.close()
            print("--- %s Time for db insertion ---" % (time.time() - start_time_insert))


        # start_time_db = time.time()
        # conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        # print("--- %s Time for db connection ---" % (time.time() - start_time_db))

        # start_time_insert = time.time()
        # bulk_insert_solutions(case_id, combined_results, conn, batch_size=1)
        # print("--- %s Time for db insertion ---" % (time.time() - start_time_insert))
        # conn.close()

        print("--- %s Time for ONE ITERATION ---" % (time.time() - start_time_whole))
                
        # for solution in combined_results:
        #         url=solution['urls']
        #         name = extract_name_from_url(url)
        #         start_time_db = time.time()
        #         conn=create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
        #         print("--- %s Time for db connection ---" % (time.time() - start_time_db))
        #         start_time_insert = time.time()
        #         insert_solutions(case_id,name,url,conn)
        #         print("--- %s Time for db insertion ---" % (time.time() - start_time_insert))

        
    # conn.close()










        
        




        


        
    result = {
        'statusCode': 200,
    }
    return result
