import boto3
import json
from queue_test_solutions import find_usecases
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
    usecases = find_usecases()
    print(len(usecases))

    for usecase in usecases:
        # Create a JSON message
        message_dict = {
            "type": "tasks",
            "use_case_id": usecase["case_id"],
            "use_case_name": usecase["name"],
            "business_area_name": usecase["business_area_name"],
            "industry_name": usecase["industry_name"],
            "industry_category_name": usecase["industry_category_name"],
        }

        # Convert the dictionary to a JSON string
        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),  # Generate a unique ID
            'MessageBody': message_body
        })

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