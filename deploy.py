import os
import argparse
import subprocess
from dotenv import load_dotenv

BUCKET_NAME = 'thankshell-api'

ENV_PARAMS = {
    'production': {
        'stack-name': 'thankshell-api',
    },
    'staging': {
        'stack-name': 'thankshell-api-stg',
    },
}


def deploy_platform(args):
    os.chdir('../thankshell-platforms')

    subprocess.run([
        'sam', 'deploy',
        '--profile', os.getenv('PROFILE'),
        '--template-file', 'template.yaml',
        '--stack-name', os.getenv('PLATFORM_STACK_NAME'),
        '--capabilities', 'CAPABILITY_IAM',
        '--parameter-overrides', 'Environment={}'.format(args.environment),
    ])


def deploy_api(args):
    os.chdir('../thankshell-api')

    subprocess.run([
        'sam', 'package',
        '--output-template-file', 'packaged.yaml',
        '--s3-bucket', os.getenv('CFN_BUCKET_NAME'),
    ])

    subprocess.run([
        'sam', 'deploy',
        '--profile', os.getenv('PROFILE'),
        '--template-file', 'packaged.yaml',
        '--stack-name', os.getenv('API_STACK_NAME'),
        '--capabilities', 'CAPABILITY_IAM',
        '--parameter-overrides', 'Environment={}'.format(args.environment),
    ])


def run(args):
    if args.target == 'platform':
        deploy_platform(args)
    elif args.target == 'api':
        deploy_api(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--environment',
        choices=ENV_PARAMS.keys(),
        default='staging',
    )
    parser.add_argument(
        'target',
        choices=['platform', 'api'],
        default='staging',
    )
    args = parser.parse_args()

    load_dotenv(f'.env.{args.environment}')

    run(args)
