#!/bin/bash
set -eu

BUCKET_NAME='thankshell-api'

cd ../thankshell-api
sam package --output-template-file packaged.yaml --s3-bucket ${BUCKET_NAME}
sam deploy --template-file packaged.yaml --stack-name thankshell-api --capabilities CAPABILITY_IAM
