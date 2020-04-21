from typing import Optional, Tuple


class SshParameters:
    """
    Parameters, focused on retrieving an ssh key for remote repositories.
    """
    def __init__(
            self,
            aws_secret: Optional[Tuple[str, str, Optional[str]]] = None,
            ssh_key: Optional[str] = None,
    ) -> None:
        """
        Constructor. At most one parameter must be fulfilled, as they are all multiple ways of retrieving an SSH key.

        :param aws_secret: An aws secret id and aws secret arn pair which point to a secret from which
        an ssh key can be retrieved. The secret should be stored as PLAINTEXT. If the secret is encrypted using
        a KMS key, the third member should be the ARN of that key, otherwise the third member should be None. Read more:
        https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html
        :param kms_key_arn: If your secret is encrypted using a KMS key, you need to specify the ARN of that key,
        so CodeBuild can decrypt the secret using that key.
        :param ssh_key: A direct supply of an ssh key without needing to retrieve it from anywhere else.
        """
        message = 'Only one way of retrieving SSH key is allowed.'
        assert sum([arg is not None for arg in [aws_secret, ssh_key]]) in [1, 0], message

        self.secret_id = None
        self.secret_arn = None
        self.kms_key_arn = None

        if aws_secret:
            self.secret_id, self.secret_arn, self.kms_key_arn = aws_secret

        self.private_key = ssh_key
