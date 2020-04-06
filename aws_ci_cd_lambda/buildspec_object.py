from typing import Optional, List
from aws_cdk.aws_s3 import Bucket


class BuildSpecObject:
    def __init__(
            self,
            prefix: str,
            bucket: Bucket,
            aws_secret_id: Optional[str] = None,
            ssh_key: Optional[str] = None,
            install_args: Optional[List[str]] = None,
            test_args: Optional[List[str]] = None,
    ) -> None:
        assert aws_secret_id is None or ssh_key is None, 'Both aws secret id and ssh key cannot be set. Choose one.'

        self.__prefix = prefix
        self.__bucket = bucket
        self.__aws_secret_id = aws_secret_id
        self.__private_key = ssh_key
        self.__install_args = install_args or []
        self.__test_args = test_args or []

    def get_object(self):
        if self.__aws_secret_id is not None:
            install_ssh_commands = [
                'apt install jq',
                '{ aws secretsmanager get-secret-value --secret-id ' + self.__aws_secret_id +
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
                        ' '.join(['./install.sh'] + self.__install_args)
                    ]
                },
                'pre_build': {
                    'commands': [
                        'chmod +x test.sh',
                        ' '.join(['./test.sh'] + self.__test_args)
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
