from typing import Optional


class PipelineParameters:
    def __init__(
            self,
            bucket_name: str,
            secret_id: Optional[str] = None,
            secret_arn: Optional[str] = None,
            private_key: Optional[str] = None
    ):
        """
        Parameters, focused on your deployment pipeline.

        :param bucket_name: Name of S3 bucket to store pipeline artifacts.
        :param secret_id: ID of a secret where you can store the secret key to access your remote repository
        for installation, e.g. a BitBucket SSH key. The key should be stored as plaintext. This parameter is optional.
        :param secret_arn: ARN of that same secret. This parameter is optional.
        :param private_key: Secret key to access your remote repository for installation, e.g. a BitBucket SSH key. This parameter is optional
        """
        self.bucket_name = bucket_name
        self.secret_id = secret_id
        self.secret_arn = secret_arn
        self.private_key = private_key
