import os

from typing import Any, Dict, Optional
from aws_cdk import core
from aws_cdk.aws_codecommit import Repository
from aws_cdk.aws_iam import Role, PolicyStatement, PolicyDocument, Effect, ServicePrincipal
from aws_cdk.custom_resources import AwsCustomResource, PhysicalResourceId


class InitialCommit:
    """
    Custom CloudFormation resource which creates a git commit action to set initial function code.
    """
    def __init__(
            self,
            stack: core.Stack,
            prefix: str,
            code_repository: Repository,
    ) -> None:
        """
        Constructor.

        :param stack: A CloudFormation stack to which add this resource.
        :param prefix: Prefix for resource names.
        :param code_repository: A codecommit git repository to create commits for.
        """
        self.__stack = stack
        self.__prefix = prefix
        self.__code_repository = code_repository

    def get_resource(self):
        """
        Creates a custom resource to create commits to codecommit.

        :return: Custom resource to create commits to codecommit.
        """
        return AwsCustomResource(
            self.__stack,
            self.__prefix + "CiCdLambdaCustomCommitResource",
            on_create=self.__on_create(),
            on_update=self.__on_update(),
            on_delete=self.__on_delete(),
            role=self.__role()
        )

    def __role(self) -> Role:
        """
        A role for custom resource which manages git commits to codecommit.

        :return: Custom resource's role.
        """
        return Role(
            self.__stack,
            self.__prefix + 'CiCdLambdaCustomCommitRole',
            inline_policies={
                self.__prefix + 'CiCdLambdaCustomCommitPolicy': PolicyDocument(
                    statements=[
                        PolicyStatement(
                            actions=[
                                "codecommit:CreateCommit",
                            ],
                            resources=[self.__code_repository.repository_arn],
                            effect=Effect.ALLOW
                        ),
                        PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=['*'],
                            effect=Effect.ALLOW
                        )
                    ]
                )},
            assumed_by=ServicePrincipal('lambda.amazonaws.com')
        )

    @staticmethod
    def service_name() -> str:
        """
        Returns a service name that this custom resource manages.

        :return: Service name.
        """
        return 'CodeCommit'

    def __on_create(self) -> Optional[Dict[Any, Any]]:
        """
        Creates an "on_create" command.

        :return: A dictionary command.
        """

        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, '../files')

        return {
                "service": self.service_name(),
                "action": "createCommit",
                "parameters": {
                    'branchName': 'master',
                    'repositoryName': self.__code_repository.repository_name,
                    'commitMessage': 'Initial files.',
                    'putFiles': [
                        {
                            'filePath': 'install.sh',
                            'fileMode': 'NORMAL',
                            'fileContent': open(os.path.join(path, 'install.sh'), 'r').read(),
                        },
                        {
                            'filePath': 'manage.py',
                            'fileMode': 'NORMAL',
                            'fileContent': open(os.path.join(path, 'manage.py'), 'r').read(),
                        },
                        {
                            'filePath': 'test.sh',
                            'fileMode': 'NORMAL',
                            'fileContent': open(os.path.join(path, 'test.sh'), 'r').read(),
                        },
                    ]
                },
                "physical_resource_id": PhysicalResourceId.of(self.__prefix + 'CiCdLambdaCreateCommit'),
            }

    def __on_update(self) -> Optional[Dict[Any, Any]]:
        """
        Creates an "on_update" command".

        :return: A dictionary command.
        """
        return None

    def __on_delete(self) -> Optional[Dict[Any, Any]]:
        """
        Creates an "on_delete" command".

        :return: A dictionary command.
        """
        return None
