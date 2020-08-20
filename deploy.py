import os
import argparse
import subprocess
import re
from dotenv import load_dotenv


def deploy_platform(dry_run):
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

    if dry_run:
        command.append('--no-execute-changeset')

    subprocess.run(command)


def deploy_api(dry_run, version):
    os.chdir('../thankshell-api')

    result = re.fullmatch(r'v\d\.\d', version)
    if not result:
        raise RuntimeError('illegal version format, example v1.0')

    stack_name = "{}-{}".format(os.getenv('API_STACK_NAME'), version.replace('.', '-'))

    subprocess.run([
        'sam', 'package',
        '--output-template-file', 'packaged.yaml',
        '--s3-bucket', os.getenv('CFN_BUCKET_NAME'),
    ])

    params = {
        'GroupsTableName': os.getenv('GROUPS_TABLE_NAME_2'),
        'GroupMembersTableName': os.getenv('GROUP_MEMBERS_TABLE_NAME'),
        'TokenTransactionsTableName': os.getenv('TOKEN_TRANSACTIONS_TABLE_NAME'),
    }
    subprocess.run(
        [
            'sam', 'deploy',
            '--profile', os.getenv('PROFILE'),
            '--template-file', 'packaged.yaml',
            '--stack-name', stack_name,
            '--capabilities', 'CAPABILITY_IAM',
            '--parameter-overrides',
        ] + [
            f'{key}={value}'
            for key, value in params.items()
        ]
    )


def run(args):
    load_dotenv(f'.env.{args.environment}')

    if args.target == 'platform':
        deploy_platform(args.dry_run)
    elif args.target == 'api':
        deploy_api(args.dry_run, args.version)


def get_parser():
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

    subparsers = parser.add_subparsers(dest='target', help='sub-command help')
    subparsers.required = True

    parser_platform = subparsers.add_parser('platform', help='deploy platform')

    parser_api = subparsers.add_parser('api', help='deploy api')
    parser_api.add_argument('version')

    return parser


if __name__ == '__main__':
    parser = get_parser()

    run(parser.parse_args())
