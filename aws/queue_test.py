import boto3
import json

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    # Create a JSON message
    message_dict = {
        "type": "solutions",
        "use_case_name" : "AI-facilitated Focus Groups",
        "use_case_description" : "Employ AI-powered tools to facilitate and analyze focus groups, providing insights into employee perceptions and sentiments.",
        "industry_name" : "consulting_strategy",
        "industry_category_name" : "Crisis Management & Turnaround",
        "timestamp": "2023-05-24T10:30:00Z"
    }

    # Convert the dictionary to a JSON string
    message_body = json.dumps(message_dict)

    # Send the JSON message to the queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )

    print(f"JSON message sent. MessageId: {response['MessageId']}")

except Exception as e:
    print(f"An error occurred: {str(e)}")
# 2024/07/10/[$LATEST]16d23f1af7a947c4a82e951b64a9f4ff