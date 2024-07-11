#!/bin/bash
FUNCTION=$(aws cloudformation describe-stack-resource --stack-name wapify-llm-stack --logical-resource-id MyLambdaFunction --query 'StackResourceDetail.PhysicalResourceId' --output text)

echo $FUNCTION

while true; do
  aws lambda invoke --function-name $FUNCTION --payload fileb://sqs.event.json out.json
  cat out.json
  echo ""
  sleep 2
  break
done
