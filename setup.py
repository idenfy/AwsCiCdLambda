from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()
setup(
    name='aws_ci_cd_lambda',
    version='2.2.0',
    license='GNU GENERAL PUBLIC LICENSE Version 3',
    packages=find_packages(exclude=['venv', 'test']),
    description=(
        'AWS CDK package that helps deploying a lambda function.'
    ),
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'aws_cdk.core==1.27.0',
        'aws_cdk.aws_iam==1.27.0',
        'aws_cdk.custom_resources==1.27.0',
        'aws_cdk.aws_lambda==1.27.0',
        'aws_cdk.aws_codecommit==1.27.0',
        'aws_cdk.aws_codebuild==1.27.0',
        'aws_cdk.aws_codepipeline==1.27.0',
        'aws_cdk.aws_codepipeline_actions==1.27.0',
        'aws_cdk.aws_ec2==1.27.0',
        'aws-empty-bucket>=2.0.0,<3.0.0'
    ],
    author='Deividas Tamkus',
    author_email='dtamkus@gmail.com',
    keywords='AWS CDK Ci/Cd Lambda Pipeline',
    url='https://github.com/idenfy/AwsCiCdLambda.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
