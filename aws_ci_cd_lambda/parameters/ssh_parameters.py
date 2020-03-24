from typing import Optional, Tuple


class SshParameters:
    """
    Parameters, focused on retrieving an ssh key for remote repositories.
    """
    def __init__(
            self,
            aws_secret: Optional[Tuple[str, str]] = None,
            ssh_key: Optional[str] = None
    ) -> None:
        """
        Constructor.

        :param aws_secret: An aws secret id and aws secret arn pair which point to a secret from which
        an ssh key can be retrieved. The secret should be stored as PLAINTEXT. Read more:
        https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html
        :param ssh_key: A direct supply of an ssh key without needing to retrieve it from anywhere else.
        """
        message = 'Only one way of retrieving SSH key is allowed.'
        assert sum([arg is not None for arg in [aws_secret, ssh_key]]) == 1, message

        self.secret_id = None
        self.secret_arn = None

        if aws_secret:
            self.secret_id, self.secret_arn = aws_secret

        self.private_key = ssh_key
