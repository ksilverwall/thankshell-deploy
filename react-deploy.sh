#!/bin/bash

set -eu

BUCKET_NAME=production-thankshell-react

cd $(dirname $0)

cd ../thankshell-react
npm run-script build
aws s3 sync --profile thankshell --exclude ".DS_Store" ./build s3://${BUCKET_NAME}/ --delete
