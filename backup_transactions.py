import boto3
import os
import argparse
import subprocess
from dotenv import load_dotenv
import hashlib
import json


def get_all(client, table_name):
    response = client.scan(
        TableName=table_name,
    )

    return response['Items']


def run(args):
    session = boto3.Session(profile_name=os.getenv('PROFILE'))
    client = session.client('dynamodb')

    records = get_all(client, os.getenv('TOKEN_TRANSACTIONS_TABLE_NAME'))
    for record in records:
        print(json.dumps(record))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--environment',
        choices=['production', 'staging'],
        default='staging',
    )
    args = parser.parse_args()

    load_dotenv(f'.env.{args.environment}')

    run(args)
