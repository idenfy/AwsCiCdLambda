from typing import List
from aws_cdk.aws_ec2 import Vpc, Subnet, SecurityGroup


class VpcParameters:
    """
    Parameters, focused on Virtual Private Cloud settings.
    """
    def __init__(
            self,
            vpc: Vpc,
            subnets: List[Subnet],
            security_groups: List[SecurityGroup],
    ) -> None:
        """
        Constructor.

        :param vpc: VPC your function should be deployed to.
        :param subnets: List of subnets your function should be deployed to.
        :param security_groups: List of security groups for your function.
        """
        self.vpc = vpc
        self.subnets = subnets
        self.security_groups = security_groups
