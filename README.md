## AWS Lambda Pipeline

A library that creates a full out-of-the-box solution for AWS Lambda with CI/CD pipeline.

#### Remarks

The project is written by [Deividas Tamkus](https://github.com/deitam), supervised by 
[Laimonas Sutkus](https://github.com/laimonassutkus) and is owned by 
[iDenfy](https://github.com/idenfy). This is an open source
library intended to be used by anyone. [iDenfy](https://github.com/idenfy) aims
to share its knowledge and educate market for better and more secure IT infrastructure.

#### Related technology

This project utilizes the following technology:

- *AWS* (Amazon Web Services).
- *AWS CDK* (Amazon Web Services Cloud Development Kit).
- *AWS CloudFormation*.
- *AWS Lambda*.
- *AWS CodePipeline*.

#### Assumptions

This library project assumes the following:

- You have knowledge in AWS (Amazon Web Services).
- You have knowledge in AWS CloudFormation and AWS loadbalancing.
- You are managing your infrastructure with AWS CDK.
- You are writing AWS CDK templates with a python language.

#### Install

The project is built and uploaded to PyPi. Install it by using pip.

```bash
pip install aws-lambda-pipeline
```

### Description

This package creates a Lambda function and a pipeline 
for a complete out-of-the-box hosting infrastructure.

The pipeline takes your source code from CodeCommit and deploys it to Lambda.

### Examples

##### Complete tutorial

- Create a full infrastructure around AWS Lambda by using the following code below in your stack.

```python
from aws_lambda_pipeline.lambda_pipeline import LambdaPipeline
from aws_cdk import core, aws_ec2, aws_iam

class MainStack(core.Stack):
    def __init__(self, scope: core.App) -> None:
        super().__init__(
            scope=scope,
            id='MyCoolStack'
        )

        # Create your own vpc or use an existing one.
        vpc = aws_ec2.Vpc(...)
        
        # Create an execution role for your function.
        role = aws_iam.Role(...)
        
        # Create a security group for your function.
        sg = aws_ec2.SecurityGroup(...)
        
        self.pipeline = LambdaPipeline(
            scope=self,
            prefix='MyCool',
            vpc=vpc,
            subnets=vpc.isolated_subnets,
            security_groups=[sg],
            execution_role=role,
            lambda_memory=1024,
            lambda_timeout=60,
            lambda_handler='manage.runner',
            bucket_name='MyCoolBucket',
            secret_id='MyCoolSecret',
            secret_arn='arn:aws:secretsmanager:region:account_id:secret:MyCoolSecret-rAnDomStrinG'
        )
```

- Provision you infrastructure with `CloudFormation` by calling `cdk deploy`.

- After you provision your infrastructure, go to `AWS CodeCommit` in your AWS Console.

- Find a newly created git repository.

- Commit any code you want to the newly created repository to trigger a pipeline.

(A tutorial on pushing code to remote repositories: [AWS Tutorial](https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-create-commit.html)).

(A tutorial on setting up git ssh with aws git repositories: [AWS Tutorial](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html))
