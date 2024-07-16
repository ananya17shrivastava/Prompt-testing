import boto3
import json
from queue_test_solutions import find_industry_categories
import uuid

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue-business-area'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    industry_categories = find_industry_categories()
    print(len(industry_categories))

    for industry_category in industry_categories:
        
        message_dict = {
            "type": "business",

            "industry_id": industry_category["industry_id"],
            "industry_name": industry_category["industry_name"],
            "industry_category_id": industry_category["industry_category_id"],
            "industry_category_name": industry_category["industry_category_name"],
        }
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