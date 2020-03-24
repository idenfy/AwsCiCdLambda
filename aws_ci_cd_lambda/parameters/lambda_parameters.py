from aws_cdk.aws_iam import Role
from aws_cdk.aws_lambda import Runtime


class LambdaParameters:
    """
    Parameters, focusing on the Lambda function itself.
    """
    def __init__(
            self,
            execution_role: Role,
            lambda_memory: int,
            lambda_timeout: int,
            lambda_handler: str,
            lambda_runtime: Runtime,
    ) -> None:
        """
        Constructor.

        :param execution_role: Execution role for your function.
        :param lambda_memory: Amount of memory your function can use, exceeding it will result in an error (in megabytes).
        :param lambda_timeout: Time, after which the function times out and returns an error (in seconds).
        :param lambda_handler: File name and function name that handles lambda invocation.
        :param lambda_runtime: Runtime for your Lambda function (the programming language it uses).
        """
        self.execution_role = execution_role
        self.lambda_memory = lambda_memory
        self.lambda_timeout = lambda_timeout
        self.lambda_handler = lambda_handler
        self.lambda_runtime = lambda_runtime
