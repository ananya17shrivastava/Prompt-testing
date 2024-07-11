from botocore.exceptions import ClientError
import os
import logging
import boto3
import jsonpickle
from lllms.index import invoke_llm, LLM_PROVIDER_CLAUDE, LLM_PROVIDER_PERPLEXITY
from lllms.claude import CLAUDE_HAIKU_3, CLAUDE_SONNET_35
from lllms.perplexity import PERPLEXITY_MODEL
import time
from typing import List, TypedDict
import json
from mysql.connector import Error
import mysql.connector
from lllms.perplexity import call_llm_perplexity

from db.mysql import get_api_key, create_db_connection
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
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # {'ARN': 'arn:aws:secretsmanager:us-east-1:975049940276:secret:llmapp-4tZw2V', 'Name': 'llmapp', 'VersionId': 'b59f76ba-4cea-4dac-8bb6-085f64f79c36', 'SecretString': '{"MYSQL_DATABASE":"impact360","MYSQL_HOST":"aws.connect.psdb.cloud","MYSQL_USER":"v25eqlp7h4xkf9zilm2w","MYSQL_PASSWORD":"pscale_pw_zkb7BSjGI7oYrnH8MZcdzyhpvVWr8E5HwEC6PTcePnV"}', 'VersionStages': ['AWSCURRENT'], 'CreatedDate': datetime.datetime(2024, 7, 10, 13, 45, 2, 658000, tzinfo=tzlocal()), 'ResponseMetadata': {'RequestId': 'c071a879-c5ae-44a6-97db-51b0cd74c0d2', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': 'c071a879-c5ae-44a6-97db-51b0cd74c0d2', 'content-type': 'application/x-amz-json-1.1', 'content-length': '416', 'date': 'Wed, 10 Jul 2024 14:28:28 GMT'}, 'RetryAttempts': 0}}

    print(get_secret_value_response)
    secret = get_secret_value_response['SecretString']
    logger.info(f"secret string {secret}")
    secretJSON = json.loads(secret)
    logger.info(f"secret {secretJSON}")
    return secretJSON


secrets = get_secret()
logger.info(f"secrets73 {secrets}")
langfuse=connect_langfuse(secrets['LANGFUSE_SECRET_KEY'],secrets['LANGFUSE_PUBLIC_KEY'])

logger.info(f"langfuse secret key {secrets['LANGFUSE_SECRET_KEY']}")
logger.info(f"langfuse public key {secrets['LANGFUSE_PUBLIC_KEY']}")
logger.info(f"secrets73 {secrets}")


conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])


if not conn.is_connected():
    conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])


PERPLEXITY_API_KEY = get_api_key("PERPLEXITY_API_KEY",conn)
ANTHROPIC_API_KEY=get_api_key("ANTHROPIC_API_KEY",conn)

logger.info(f"PERPLEXITY_API_KEY {PERPLEXITY_API_KEY}")
logger.info(f"langfuse public key {ANTHROPIC_API_KEY}")


class AISolution(TypedDict):
    solution_id: str
    solution_name: str
    usecase_name: str
    usecase_description: str
    industry_category_name: str
    industry_name: str


def find_aisolutions(conn) -> List[AISolution]:
    my_cursor = None
    ai_solutions: List[AISolution] = []
    print(conn.is_connected())
    if not conn.is_connected():
        conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])

    try:
        my_cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                s.id AS solution_id,
                s.name AS solution_name,
                c.name AS usecase_name,
                c.description AS usecase_description,
                ic.name AS industry_category_name,
                i.name AS industry_name
            FROM 
                solutions s
            JOIN 
                case_to_solution cts ON s.id = cts.solution_id
            JOIN 
                cases c ON cts.case_id = c.id
            JOIN 
                industries i ON c.industry_id = i.id
            JOIN 
                industry_categories ic ON c.industry_category_id = ic.id
            WHERE 
                s.ai_generated = 1 AND s.id='006ef88b-15a2-4ea3-9348-09b5dc30396d';
        """

        my_cursor.execute(query)
        results = my_cursor.fetchall()

        for row in results:
            ai_solutions.append({
                "solution_id": row['solution_id'],
                "solution_name": row['solution_name'].replace('_', ' '),
                "usecase_name": row['usecase_name'].replace('_', ' '),
                "usecase_description": row['usecase_description'],
                "industry_category_name": row['industry_category_name'].replace('_', ' '),
                "industry_name": row['industry_name'].replace('_', ' ')
            })

    except Error as e:
        print(f"An error occurred while fetching AI solutions: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        # if conn:
            # conn.close()

    return ai_solutions


def lambda_handler(event, context):

    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    start_time = time.time()
    conn=create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
    print(conn.is_connected())
    res = find_aisolutions(conn=conn)
    
    print("--- %s seconds ---" % (time.time() - start_time))
    print(fetch_prompt("business_areas",langfuse))
    print(res)
    print(event)
    logger.info(f"Received {len(event['Records'])} messages")
    for record in event['Records']:
       
        message_body = record['body']
        parsed_message=json.loads(message_body)
        print("this is message body -")
        print( parsed_message)
        usecase_name=parsed_message.get('use_case_name', 'N/A')
        usecase_description=parsed_message.get('use_case_description', 'N/A')
        industry_name=parsed_message.get('industry_name', 'N/A')
        industry_category_name=parsed_message.get('industry_category_name', 'N/A')
        print(parsed_message.get('use_case_name', 'N/A'))
        print(parsed_message.get('use_case_description', 'N/A'))
        print(parsed_message.get('industry_name', 'N/A'))
        print(parsed_message.get('industry_category_name', 'N/A'))

        
        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL
        prompts=get_aisolutions_prompt(usecase_name,usecase_description,industry_name,industry_category_name)
        # print(prompts)
        user_prompt = prompts['user_prompt']
        system_prompt = prompts['system_prompt']

        description_result=invoke_llm(provider, model, [{
            "role": "user",
            "content": user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=system_prompt,API_KEY=PERPLEXITY_API_KEY)
        # print(description_result)
        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3

        xml_prompt=get_xmlprompt(description_result)
        result= invoke_llm(provider, model, [{
                "role": "user",
                "content": xml_prompt,
        }], max_tokens=4096, temperature=0,prompt_id="ai_solutions",API_KEY=ANTHROPIC_API_KEY)

        # print(result)
        result = result.replace("&", "&amp;")
        json_result = aisolutions_parser(result)
        json_result = json.dumps(json_result, indent='\t')


        #iteration 2 for getting competitors
        provider=LLM_PROVIDER_PERPLEXITY
        model = PERPLEXITY_MODEL

        competitor_prompt=get_competitor_prompt(description_result)
        competitor_user_prompt=competitor_prompt['user_prompt']
        competitor_system_prompt=competitor_prompt['system_prompt']

        competitor_result=invoke_llm(provider, model, [{
            "role": "user",
            "content": competitor_user_prompt,
        }], max_tokens=4096, temperature=.2,prompt_id="business_area",system_prompt=competitor_system_prompt,API_KEY=PERPLEXITY_API_KEY)
        # print("competitor result ::")
        # print(competitor_result)


        provider=LLM_PROVIDER_CLAUDE
        model = CLAUDE_HAIKU_3

        competitor_xml_prompt=get_xmlprompt(competitor_result)
        result2=invoke_llm(provider, model, [{
                "role": "user",
                "content": competitor_xml_prompt,
        }], max_tokens=4096, temperature=0,prompt_id="ai_solutions",API_KEY=ANTHROPIC_API_KEY)

        result2 = result2.replace("&", "&amp;")
        competitor_json_result = aisolutions_parser(result2)
        competitor_json_result = json.dumps(competitor_json_result, indent='\t')

        # print(competitor_json_result)
        # print(json_result)

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








        
        




        


        
    result = {
        'statusCode': 200,
    }
    return result
