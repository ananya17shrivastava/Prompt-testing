import boto3
import json
from queue_test_solutions import find_usecases_null
import uuid

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue-tasks'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    usecases = find_usecases_null()
    print(len(usecases))
    # i=0
    for usecase in usecases:
        # Create a JSON message
        message_dict = {
            "type": "tasks",
            "use_case_id": usecase.get("case_id", None),
            "use_case_name": usecase.get("name", None),
            "business_area_name": usecase.get("business_area_name",None),
            "industry_name": usecase.get("industry_name", None),
            "industry_category_name": usecase.get("industry_category_name", None)
        }

        # Convert the dictionary to a JSON string
        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),  # Generate a unique ID
            'MessageBody': message_body
        })
        # if i==1:
        #     break
        # i+=1

        # Send the JSON message to the queue in batches of 10
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

            entries = []  # Reset entries for the next batch

    # Send any remaining messages
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