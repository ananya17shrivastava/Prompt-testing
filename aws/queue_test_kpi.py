import boto3
import json
from queue_test_solutions import find_aisolutions
import uuid

sqs = boto3.client('sqs')

queue_name = 'llm-queue-kpi'

try:
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    ai_solutions = find_aisolutions()
    print("total_ai_solutions :")
    print(len(ai_solutions))
    for solution in ai_solutions:
        message_dict = {
            "type": "kpi",
            "solution_id":solution["solution_id"],
            "solution_name": solution["solution_name"],
            "use_case_id": solution["case_id"],
            "use_case_name": solution["usecase_name"],
            "use_case_description": solution["usecase_description"],
            "industry_category_name": solution["industry_category_name"],
            "industry_name": solution["industry_name"],
        }
        # print(message_dict)
        # break

        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),
            'MessageBody': message_body
        })

        if len(entries) == 10:
       
            response = sqs.send_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )

            for success in response['Successful']:
                print(f"JSON message sent. MessageId: {success['MessageId']}")

            if 'Failed' in response:
                for failure in response['Failed']:
                    print(f"Failed to send message. Code: {failure['Code']}, Message: {failure['Message']}")

            entries = []


    if entries:
        response = sqs.send_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )

        for success in response['Successful']:
            print(f"JSON message sent. MessageId: {success['MessageId']}")

        if 'Failed' in response:
            for failure in response['Failed']:
                print(f"Failed to send message. Code: {failure['Code']}, Message: {failure['Message']}")

except Exception as e:
    print(e)
    print(f"An error occurred: {str(e)}")






# id->unique_id
# name-> name of usecase
# case_id-> usecase id
# task_id-> yet to confirm
# winner_solution_id-> id of first solution
# creator_organization_id->user_2iNQ8GoBBlyG8NODy4DtUcAIXR2
# business_area_id-> 
# industry_id->
# industry_category_id->
# opportunity_id->yet to confirm

