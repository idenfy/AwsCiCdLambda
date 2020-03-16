from typing import Optional
from aws_cdk.aws_s3 import Bucket


class BuildSpecObject:
    def __init__(self, prefix: str, bucket: Bucket, secret_id: Optional[str] = None, private_key: Optional[str] = None):
        assert secret_id is None or private_key is None, 'Both secret id and private key cannot be set.'
        self.__prefix = prefix
        self.__bucket = bucket
        self.__secret_id = secret_id
        self.__private_key = private_key

    def get_object(self):

        if self.__secret_id is not None:
            install_ssh_commands = [
                'apt install jq',
                '{ aws secretsmanager get-secret-value --secret-id ' + self.__secret_id +
                '| jq --raw-output \'.SecretString\' > id_rsa;'
                'eval `ssh-agent`; mv id_rsa ~/.ssh;'
                'chmod 0600 ~/.ssh/id_rsa;'
                'ssh-add ~/.ssh/id_rsa; } || { echo \"Invalid key\"; }'
            ]
        elif self.__private_key is not None:
            install_ssh_commands = [
                'apt install jq',
                '{ echo ' + self.__private_key + ' > id_rsa;'
                'eval `ssh-agent`; mv id_rsa ~/.ssh;'
                'chmod 0600 ~/.ssh/id_rsa;'
                'ssh-add ~/.ssh/id_rsa; } || { echo \"Invalid key\"; }'
            ]
        else:
            install_ssh_commands = []

        return {
            'version': 0.2,
            'phases': {
                'install': {
                    'commands': install_ssh_commands + [
                        'VENV_PATH="/tmp/lambda-tmpenv"',
                        'virtualenv $VENV_PATH --python=python3.6',
                        '. $VENV_PATH/bin/activate',
                        'chmod +x install.sh',
                        './install.sh'
                    ]
                },
                'pre_build': {
                    'commands': [
                        'chmod +x test.sh',
                        './test.sh'
                    ]
                },
                'build': {
                    'commands': [
                        'INSTALL_PATH="/tmp/ivs-lambda-install-dir"',
                        'BUILD_PATH="/tmp/ivs-lambda-pack.zip"',
                        'cp -R . $INSTALL_PATH',
                        'cp -R $VENV_PATH/lib/python3.6/site-packages/. $INSTALL_PATH',
                        'cp -R $VENV_PATH/lib/python3.6/site-packages/. .',
                        'current_dir=$( pwd )',
                        'cd $INSTALL_PATH',
                        'zip -9 -r $BUILD_PATH *',
                        'cd $current_dir',
                        f'KEY={self.__prefix}',
                        f'aws s3 cp $BUILD_PATH s3://{self.__bucket.bucket_name}/"$KEY".zip',
                        f'aws lambda update-function-code --function-name="$KEY" '
                        f'--s3-bucket={self.__bucket.bucket_name} --s3-key="$KEY".zip --publish'
                    ]
                },
            }
        }
