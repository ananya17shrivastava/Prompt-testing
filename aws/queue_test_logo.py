import boto3
import json
from queue_test_solutions import find_aisolutions_logo
import uuid

sqs = boto3.client('sqs')

queue_name = 'llm-queue-logo'

try:
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    ai_solutions = find_aisolutions_logo()
    print("total_ai_solutions :")
    print(len(ai_solutions))
    # process.exit(0)
    # i=0
    for solution in ai_solutions:
        message_dict = {
            "type": "logo",
            "solution_id":solution["solution_id"],
            "documentation_url":solution["documentation_url"]
        }

        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),
            'MessageBody': message_body
        })
        # i+=1
        # if i==100:
        #     break

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

