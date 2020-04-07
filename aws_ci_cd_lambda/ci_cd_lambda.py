import re

from aws_ci_cd_lambda.lambda_alarms import LambdaAlarms
from aws_ci_cd_lambda.parameters.pipeline_parameters import PipelineParameters
from aws_ci_cd_lambda.parameters.lambda_parameters import LambdaParameters
from aws_ci_cd_lambda.parameters.vpc_parameters import VpcParameters
from aws_ci_cd_lambda.custom.initial_commit import InitialCommit
from aws_ci_cd_lambda.buildspec_object import BuildSpecObject
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


class CiCdLambda:
    def __init__(
            self,
            scope: core.Stack,
            prefix: str,
            pipeline_params: PipelineParameters,
            lambda_params: LambdaParameters,
            vpc_params: VpcParameters
    ):
        """
        AWS CDK package that helps deploying a lambda function.

        :param scope: A scope in which resources shall be created.
        :param prefix: Prefix for all of your resource IDs and names.
        :param pipeline_params: Parameters, letting you supply ssh key for accessing remote repositories.
        :param lambda_params: Parameters, focusing on the Lambda function itself.
        :param vpc_params: Parameters, focused on Virtual Private Cloud settings.
        """

        # CodeCommmit repository to store your function source code.
        self.project_repository = aws_codecommit.Repository(
            scope, prefix + 'CiCdLambdaCodeCommitRepo',
            repository_name=prefix + 'CiCdLambdaCodeCommitRepo',
        )

        # The lambda function for which this package is made.
        self.function = aws_lambda.Function(
            scope, prefix + 'Function',
            code=aws_lambda.Code.from_inline(
                'def runner():\n'
                '    return \'Hello, World!\''
            ),
            handler=lambda_params.lambda_handler,
            runtime=lambda_params.lambda_runtime,
            description=f'Lambda function {prefix}.',
            environment=lambda_params.environment,
            function_name=prefix,
            memory_size=lambda_params.lambda_memory,
            reserved_concurrent_executions=5,
            role=lambda_params.execution_role,
            security_groups=vpc_params.security_groups,
            timeout=core.Duration.seconds(lambda_params.lambda_timeout),
            vpc=vpc_params.vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc_params.subnets)
        )

        # Create alarms for the function.
        if lambda_params.alarms_sns_topic:
            self.alarms = LambdaAlarms(scope, prefix, lambda_params.alarms_sns_topic, self.function)
        else:
            self.alarms = None

        # Convert bucket name to an S3 friendly one.
        bucket_name = self.__convert(prefix + 'CiCdLambdaArtifactsBucket')

        self.bucket = EmptyS3Bucket(
            scope, prefix + 'CiCdLambdaDeploymentBucket',
            bucket_name=bucket_name
        )

        # Create a BuildSpec object for CodeBuild
        self.buildspec = BuildSpecObject(
            prefix,
            self.bucket,
            pipeline_params.secret_id,
            pipeline_params.private_key,
            pipeline_params.install_args,
            pipeline_params.test_args
        )

        # CodeBuild project, that installs functions dependencies, runs tests and deploys it to Lambda.
        self.code_build_project = aws_codebuild.PipelineProject(
            scope, prefix + 'CiCdLambdaCodeBuildProject',
            project_name=prefix + 'CiCdLambdaCodeBuildProject',
            environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.STANDARD_3_0,
                compute_type=aws_codebuild.ComputeType.SMALL
            ),
            build_spec=aws_codebuild.BuildSpec.from_object(self.buildspec.get_object()),
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
        if pipeline_params.secret_arn is not None:
            self.code_build_project.role.add_to_policy(
                statement=aws_iam.PolicyStatement(
                    actions=[
                        'secretsmanager:GetSecretValue'
                    ],
                    resources=[pipeline_params.secret_arn],
                    effect=aws_iam.Effect.ALLOW)
            )

        # Push hte initial commit to CodeCommit.
        self.initial_commit = InitialCommit(
            scope, prefix, self.project_repository
        ).get_resource()

        self.source_artifact = aws_codepipeline.Artifact(artifact_name=prefix + 'CiCdLambdaSourceArtifact')

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
            prefix + 'CiCdLambdaPipeline',
            pipeline_name=prefix + 'CiCdLambdaPipeline',
            artifact_bucket=self.bucket,
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='SourceStage',
                    actions=[self.source_action]
                ),
                aws_codepipeline.StageProps(
                    stage_name='BuildStage',
                    actions=[self.build_action]
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
