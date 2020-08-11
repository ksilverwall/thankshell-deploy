import os
import argparse
import subprocess
from dotenv import load_dotenv


def deploy_platform(args):
    os.chdir('../thankshell-platform')

    params = {
        'TokenTransactionsTableName': os.getenv('TOKEN_TRANSACTIONS_TABLE_NAME'),
        'GroupsTableName': os.getenv('GROUPS_TABLE_NAME_2'),
        'GroupMembersTableName': os.getenv('GROUP_MEMBERS_TABLE_NAME'),
        'CfnBucketName': os.getenv('CFN_BUCKET_NAME'),
    }

    command = [
        'sam', 'deploy',
        '--profile', os.getenv('PROFILE'),
        '--template-file', 'template.yml',
        '--stack-name', os.getenv('PLATFORM_STACK_NAME'),
        '--capabilities', 'CAPABILITY_IAM',
        '--parameter-overrides',
    ] + [
        f'{key}={value}'
        for key, value in params.items()
    ]

    if args.dry_run:
        command.append('--no-execute-changeset')

    subprocess.run(command)


def deploy_api(args):
    os.chdir('../thankshell-api')

    subprocess.run([
        'sam', 'package',
        '--output-template-file', 'packaged.yaml',
        '--s3-bucket', os.getenv('CFN_BUCKET_NAME'),
    ])

    params = {
        'Environment': args.environment,
        'EnvName': os.getenv('ENV_NAME'),
        'GroupsTableName': os.getenv('GROUPS_TABLE_NAME_2'),
        'GroupMembersTableName': os.getenv('GROUP_MEMBERS_TABLE_NAME'),
        'InfoTableName': os.getenv('INFO_TABLE_NAME'),
        'TransactionsTableName': os.getenv('TRANSACTION_TABLE_NAME'),
        'TokenTransactionsTableName': os.getenv('TOKEN_TRANSACTIONS_TABLE_NAME'),
    }
    subprocess.run(
        [
            'sam', 'deploy',
            '--profile', os.getenv('PROFILE'),
            '--template-file', 'packaged.yaml',
            '--stack-name', os.getenv('API_STACK_NAME'),
            '--capabilities', 'CAPABILITY_IAM',
            '--parameter-overrides',
        ] + [
            f'{key}={value}'
            for key, value in params.items()
        ]
    )


def run(args):
    if args.target == 'platform':
        deploy_platform(args)
    elif args.target == 'api':
        deploy_api(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--environment',
        choices=['production', 'staging'],
        default='staging',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
    )
    parser.add_argument(
        'target',
        choices=['platform', 'api'],
        default='staging',
    )
    args = parser.parse_args()

    load_dotenv(f'.env.{args.environment}')

    run(args)
