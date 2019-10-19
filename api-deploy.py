import os
import argparse
import subprocess

BUCKET_NAME = 'thankshell-api'

ENV_PARAMS = {
    'production': {
        'stack-name': 'thankshell-api',
    },
    'staging': {
        'stack-name': 'thankshell-api-stg',
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--environment',
        choices=ENV_PARAMS.keys(),
        default='staging',
    )
    args = parser.parse_args()

    os.chdir('../thankshell-api-2')

    params = ENV_PARAMS[args.environment]

    subprocess.run([
        'sam', 'package',
        '--output-template-file', 'packaged.yaml',
        '--s3-bucket', BUCKET_NAME,
    ])

    subprocess.run([
        'sam', 'deploy',
        '--template-file', 'packaged.yaml',
        '--stack-name', params['stack-name'],
        '--capabilities', 'CAPABILITY_IAM',
        '--parameter-overrides', 'Environment={}'.format(args.environment),
    ])
