import os
import argparse
import subprocess

ENV_PARAMS = {
    'production': {
        'bucket-name': 'production-thankshell-react',
        'build-command': ['npm', 'run-script', 'build'],
    },
    'staging': {
        'bucket-name': 'staging-thankshell-react',
        'build-command': ['npm', 'run-script', 'build:staging'],
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

    os.chdir('../thankshell-react')

    params = ENV_PARAMS[args.environment]

    subprocess.run(params['build-command'])
    subprocess.run([
        'aws',
        's3', 'sync',
        '--profile', 'thankshell',
        '--exclude', '".DS_Store"',
        './build',
        's3://{}/'.format(params['bucket-name']),
        '--delete'
    ])
