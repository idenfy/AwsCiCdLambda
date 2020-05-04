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
            custom_pre_build_commands: Optional[List[str]] = None
    ) -> None:
        """
        Constructor.

        :param ssh_params: Parameters, focused on retrieving an ssh key for remote repositories.
        :param install_args: Arguments for your ./install.sh script
        :param test_args: Arguments for your ./test.sh script
        :param custom_pre_build_commands: Commands, that CodeBuild should execute between installation and testing. Optional
        """

        self.ssh_params = ssh_params
        self.install_args = install_args
        self.test_args = test_args
        self.custom_pre_build_commands = custom_pre_build_commands
