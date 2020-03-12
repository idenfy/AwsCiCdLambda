import re

from aws_lambda_pipeline.custom.initial_commit import InitialCommit
from typing import Optional, List
from aws_empty_bucket.empty_s3_bucket import EmptyS3Bucket
from aws_cdk import (
    aws_codepipeline_actions,
    aws_codepipeline,
    aws_codecommit,
    aws_codebuild,
    aws_lambda,
    aws_ec2,
    aws_iam,
    core
)


class LambdaPipeline:
    def __init__(
            self,
            scope: core.Stack,
            prefix: str,
            vpc: aws_ec2.Vpc,
            subnets: List[aws_ec2.Subnet],
            security_groups: List[aws_ec2.SecurityGroup],
            execution_role: aws_iam.Role,
            lambda_memory: int,
            lambda_timeout: int,
            lambda_handler: str,
            bucket_name: str,
            secret_id: Optional[str] = None,
            secret_arn: Optional[str] = None
    ):
        """
        Constructor

        :param scope: A scope in which resources shall be created.
        :param prefix: Prefix for all of your resource IDs and names.
        :param vpc: VPC your function should be deployed to.
        :param subnets: List of subnets your function should be deployed to.
        :param security_groups: List of security groups for your function.
        :param execution_role: Execution role for your function.
        :param lambda_memory: Amount of memory your function can use, exceeding which returns an error (in megabytes).
        :param lambda_timeout: Time, after which the function times out and returns an error (in seconds).
        :param lambda_handler: File name and function name that handles lambda invocation.
        :param bucket_name: Name of S3 bucket to store pipeline artifacts.
        :param secret_id: ID of a secret where you can store the secret key to access your remote repository
        for installation, e.g. a BitBucket SSH key. The key should be stored as plaintext. This parameter is optional.
        :param secret_arn: ARN of that same secret. This parameter is optional.
        """

        # CodeCommmit repository to store your function source code.
        self.project_repository = aws_codecommit.Repository(
            scope, prefix + 'LambdaCodeCommitRepo',
            repository_name=prefix + 'LambdaCodeCommitRepo',
        )

        # The lambda function for which this package is made.
        self.function = aws_lambda.Function(
            scope, prefix + 'Function',
            code=aws_lambda.Code.from_inline(
                'def runner():\n'
                '    return \'Hello, World!\''
            ),
            handler=lambda_handler,
            runtime=aws_lambda.Runtime.PYTHON_3_6,
            function_name=prefix,
            memory_size=lambda_memory,
            role=execution_role,
            security_groups=security_groups,
            timeout=core.Duration.seconds(lambda_timeout),
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=subnets)
        )

        # Convert bucket name to an S3 friendly one.
        bucket_name = self.__convert(bucket_name)

        self.bucket = EmptyS3Bucket(
            scope, prefix + 'LambdaDeploymentBucket',
            bucket_name=bucket_name
        )

        # If no secret id is provided, we give it a fake value so it's not None.
        secret_id = secret_id or 'FakeSecretId'

        # CodeBuild project, that installs functions dependencies, runs tests and deploys it to Lambda.
        self.code_build_project = aws_codebuild.PipelineProject(
            scope, prefix + 'FargateCodeBuildProject',
            project_name=prefix + 'FargateCodeBuildProject',
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.STANDARD_3_0,
                compute_type=aws_codebuild.ComputeType.SMALL
            ),
            build_spec=aws_codebuild.BuildSpec.from_object(
                {
                    'version': 0.2,
                    'phases': {
                        'install': {
                            'commands': [
                                'apt install jq',
                                '{ aws secretsmanager get-secret-value --secret-id ' + secret_id +
                                '| jq --raw-output \'.SecretString\' > id_rsa;'
                                'eval `ssh-agent`; mv id_rsa ~/.ssh;'
                                'chmod 0600 ~/.ssh/id_rsa;'
                                'ssh-add ~/.ssh/id_rsa; } || { echo \"Invalid key\"; }',
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
                                f'KEY={prefix}',
                                f'aws s3 cp $BUILD_PATH s3://{self.bucket.bucket_name}/"$KEY".zip',
                                f'aws lambda update-function-code --function-name="$KEY" '
                                f'--s3-bucket={self.bucket.bucket_name} --s3-key="$KEY".zip --publish'
                            ]
                        },
                    }
                }
            ),
        )

        # Adding permissions that allow CodeBuild to do the aforementioned things.
        self.code_build_project.role.add_to_policy(
            statement=aws_iam.PolicyStatement(
                actions=[
                    's3:*',
                    'lambda:UpdateFunctionCode',
                ],
                resources=['*'],
                effect=aws_iam.Effect.ALLOW)
        )

        # If a secret is provided, we allow CodeBuild to read it.
        if secret_arn is not None:
            self.code_build_project.role.add_to_policy(
                statement=aws_iam.PolicyStatement(
                    actions=[
                        'secretsmanager:GetSecretValue'
                    ],
                    resources=[secret_arn],
                    effect=aws_iam.Effect.ALLOW)
            )

        # Push hte initial commit to CodeCommit.
        self.initial_commit = InitialCommit(
            scope, prefix, self.project_repository
        ).get_resource()

        self.source_artifact = aws_codepipeline.Artifact(artifact_name=prefix + 'SourceArtifact')

        # CodePipeline source action to read from CodeCommit.
        self.source_action = aws_codepipeline_actions.CodeCommitSourceAction(
            repository=self.project_repository,
            branch='master',
            action_name='CodeCommitSource',
            run_order=1,
            trigger=aws_codepipeline_actions.CodeCommitTrigger.EVENTS,
            output=self.source_artifact
        )

        # CodePipeline build action that uses the CodeBuild project.
        self.build_action = aws_codepipeline_actions.CodeBuildAction(
            input=self.source_artifact,
            project=self.code_build_project,
            action_name='BuildAction',
            run_order=1
        )

        # CodePipeline pipeline that executes both actions.
        self.codecommit_to_lambda_pipeline = aws_codepipeline.Pipeline(
            scope,
            prefix + 'LambdaPipeline',
            pipeline_name=prefix + 'LambdaPipeline',
            artifact_bucket=self.bucket,
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='SourceStage',
                    actions=[self.source_action]
                ),
                aws_codepipeline.StageProps(
                    stage_name='BuildStage',
                    actions=[

                    ]
                )
            ]
        )

    @staticmethod
    def __convert(name: str) -> str:
        """
        Converts CamelCase string to pascal-case where underscores are dashes.
        This is required due to S3 not supporting capital letters or underscores.
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
