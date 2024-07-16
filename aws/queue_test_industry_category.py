import boto3
import json
from queue_test_solutions import find_industries
import uuid

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue-industry'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    industries = find_industries()
    print(len(industries))

    for industry in industries:
        
        message_dict = {
            "type": "industry",

            "industry_id": industry["industry_id"],
            "industry_name": industry["industry_name"],
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