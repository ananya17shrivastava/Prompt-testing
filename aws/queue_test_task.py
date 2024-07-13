import boto3
import json
import uuid
from queue_test_solutions import find_usecases

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    usecases = find_usecases()
    # print(usecases)

    for i in range(1):
        # Create a JSON message
        message_dict = {
            "type": "tasks",
            "use_case_id": usecases[i]["case_id"],
            "use_case_name": usecases[i]["name"],
            "business_area_name": usecases[i]["business_area_name"],
            "industry_name": usecases[i]["industry_name"],
            "industry_category_name": usecases[i]["industry_category_name"],
        }

        # Convert the dictionary to a JSON string
        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),
            'MessageBody': message_body
        })

        # Send the JSON message to the queue
        if i > 0 and i % 9 == 0:
            response = sqs.send_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            entries = []
            # response = sqs.send_message(
            #     QueueUrl=queue_url,
            #     MessageBody=message_body
            # )

            print(response)
            for success in response['Successful']:
                print(f"JSON message sent. MessageId: {success['MessageId']}")

            if 'Failed' in response:
                for failure in response['Failed']:
                    print(f"Failed to send message. Code: {failure['Code']}, Message: {failure['Message']}")

    if (len(entries) > 0):
        response = sqs.send_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )
        entries = []
        # response = sqs.send_message(
        #     QueueUrl=queue_url,
        #     MessageBody=message_body
        # )

        for success in response['Successful']:
            print(f"JSON message sent. MessageId: {success['MessageId']}")

        if 'Failed' in response:
            for failure in response['Failed']:
                print(f"Failed to send message. Code: {failure['Code']}, Message: {failure['Message']}")

except Exception as e:
    print(e)
    print(f"An error occurred: {str(e)}")