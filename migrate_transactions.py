import boto3
import os
import argparse
import subprocess
from dotenv import load_dotenv
import hashlib


def get_classic(client, table_name):
    response = client.scan(
        TableName=table_name,
    )

    return (
        {
            'timestamp': int(item['timestamp']['N']),
            'from_account': item['from_account']['S'],
            'to_account': item['to_account']['S'],
            'amount': item['amount']['N'],
            'comment': item['comment']['S'] if 'comment' in item else ' ',
        }
        for item in response['Items']
    )


def convert_member(member_column):
    value = member_column
    new_value = None
    if value == '--':
        new_value = '__VOID__'
    elif value == 'sla_bank':
        new_value = '__BANK__'
    else:
        new_value = value

    return new_value

def get_transaction_id(timestamp, from_member_id, to_member_id):
    hash_str = hashlib.sha256(f"{from_member_id}:{to_member_id}".encode()).hexdigest()

    return "{:016x}_{:s}".format(timestamp, hash_str[-8:])

def transform(classic_records):
    return [
        {
            'group_id': {'S': 'sla'},
            'transaction_id': {'S': get_transaction_id(record['timestamp'], record['from_account'], record['to_account'])},
            'from_member_id': {'S': convert_member(record['from_account'])},
            'to_member_id': {'S': convert_member(record['to_account'])},
            'amount': {'N': record['amount']},
            'timestamp': {'N': str(record['timestamp'])},
            'comment': {'S': record['comment'].strip()},
        }
        for record in classic_records
    ]


def set_transactions(client, table_name, records):
    requests = [
        {
            'PutRequest': {
                'Item': record,
            }
        }
        for record in records
    ]
    client.batch_write_item(
        RequestItems={
            table_name: requests,
        }
    )


def run(args):
    session = boto3.Session(profile_name=os.getenv('PROFILE'))
    client = session.client('dynamodb')

    classic_records = get_classic(client, os.getenv('TRANSACTION_TABLE_NAME'))

    records = transform(classic_records)

    for idx in range(0, len(records), 24):
        set_transactions(client, os.getenv('TOKEN_TRANSACTIONS_TABLE_NAME'), records[idx:idx + 24])


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
