from typing import Optional, List

from aws_ci_cd_lambda.parameters.ssh_parameters import SshParameters


class PipelineParameters:
    """
    Parameters, focused on retrieving an ssh key for remote repositories and other pipeline actions.
    """
    def __init__(
            self,
            ssh_params: SshParameters,
            install_args: Optional[List[str]] = None,
            test_args: Optional[List[str]] = None,
    ) -> None:
        """
        Constructor.

        :param ssh_params: Parameters, focused on retrieving an ssh key for remote repositories.
        :param install_args: Arguments for your ./install.sh script
        :param test_args: Arguments for your ./test.sh script
        """

        self.ssh_params = ssh_params
        self.install_args = install_args
        self.test_args = test_args
