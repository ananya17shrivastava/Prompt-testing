#!/bin/bash
set -eo pipefail
ARTIFACT_BUCKET="wapify-llm-stack"
aws s3 mb s3://$ARTIFACT_BUCKET