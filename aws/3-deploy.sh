#!/bin/bash

STACK_NAME=wapify-llm-stack

aws cloudformation package --template-file template.yaml --s3-bucket $STACK_NAME --output-template-file out.yml
aws cloudformation deploy --template-file out.yml --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM


# Get the queue URL and log group ARN from CloudFormation outputs
QUEUE_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='QueueURL'].OutputValue" --output text)
LOG_GROUP_ARN=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='SQSLogGroupARN'].OutputValue" --output text)

# Set the queue attributes to enable CloudWatch logging
# aws sqs set-queue-attributes --queue-url $QUEUE_URL --attributes "{\"CloudWatchLogsLogGroupArn\":\"$LOG_GROUP_ARN\"}"

echo "CloudWatch logging enabled for SQS queue: $QUEUE_URL"