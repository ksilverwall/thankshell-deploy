import boto3
import os
import argparse
import subprocess
from dotenv import load_dotenv


def get_users(client, table_name):
    response = client.scan(
        TableName=table_name,
    )

    return [
        {
            'display_name': user['display_name']['S'] if 'display_name' in user else None,
            'user_id': user['user_id']['S'],
        }
        for user in response['Items']
    ]


def get_active_users(client, table_name):
    response = client.scan(
        TableName=table_name,
    )

    return [user['user_id']['S'] for user in response['Items']]


def get_auth(client, table_name):
    response = client.scan(
        TableName=table_name,
    )

    return [
        {
            'auth_id': user['auth_id']['S'],
            'user_id': user['user_id']['S'],
        }
        for user in response['Items']
    ]


def get_group(client, table_name):
    response = client.get_item(
        TableName=table_name,
        Key={'group_id': {'S': 'sla'} }
    )

    return response['Item']


def set_group_members(client, table_name, record):
    client.put_item(
        TableName=table_name,
        Item=record,
    )


def get_auth_id(member, auths):
    auth_id = None
    for auth in auths:
        if member == auth['user_id']:
            auth_id = auth['auth_id']

    return auth_id


def get_permission(member_id, group):
    if member_id == group['owner']['S']:
        return 'owner'
    if member_id in group['admins']['SS']:
        return 'admin'

    return 'member'


def get_display_name(member_id, users):
    for user in users:
        if user['user_id'] == member_id:
            return user['display_name']

    return None


def create_group_members(users, group, auths):
    active_users = tuple(user['user_id'] for user in users)

    group_registered_members = group['members']['SS']
    records = []
    for member in group_registered_members:
        state = 'ACTIVE' if member in active_users else 'UNREGISTERED'
        if state == 'ACTIVE':
            auth_id = get_auth_id(member, auths)
            display_name = get_display_name(member, users)

            record = {
                'group_id': {'S': 'sla'},
                'member_id': {'S': member},
                'state': {'S': state},
                'group_permission': {'S': get_permission(member, group)},
                'auth_id': {'S': auth_id},
            }
            if display_name:
                record['display_name'] = {'S': display_name}
        else:
            record = {
                'group_id': {'S': 'sla'},
                'member_id': {'S': member},
                'state': {'S': state},
            }

        records.append(record)

    return records


def run(args):
    session = boto3.Session(profile_name=os.getenv('PROFILE'))
    client = session.client('dynamodb')

    group = get_group(client, os.getenv('GROUPS_TABLE_NAME'))
    users = get_users(client, os.getenv('USERS_TABLE_NAME'))
    auths = get_auth(client, os.getenv('AUTH_TABLE_NAME'))

    records = create_group_members(users, group, auths)

    for record in records:
        set_group_members(client, os.getenv('GROUP_MEMBERS_TABLE_NAME'), record)


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
