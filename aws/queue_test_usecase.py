import boto3
import json
from queue_test_solutions import find_business_areas, find_null_business_areas
import uuid

# Create an SQS client
sqs = boto3.client('sqs')

# Specify the queue name
queue_name = 'llm-queue-usecase'

try:
    # Get the queue URL
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    entries = []
    business_areas = find_null_business_areas()
    print(len(business_areas))
    # i=0
    for business_area in business_areas:
        # Create a JSON message
        message_dict = {
            "type": "usecases",
            "business_area_id": business_area["business_area_id"],
            "business_area_name": business_area["business_area_name"],
            # "industry_id": business_area["industry_id"],
            # "industry_name": business_area["industry_name"],
            # "industry_category_id": business_area["industry_category_id"],
            # "industry_category_name": business_area["industry_category_name"],
        }
        print(message_dict)
        # process.exit(0)
        message_body = json.dumps(message_dict)

        entries.append({
            'Id': str(uuid.uuid4()),
            'MessageBody': message_body
        })
        # if(i==2):
        #     break
            
        # i+=1


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