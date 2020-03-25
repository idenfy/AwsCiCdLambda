from aws_cdk.aws_cloudwatch import CfnAlarm
from aws_cdk.aws_lambda import IFunction
from aws_cdk.aws_sns import ITopic
from aws_cdk.core import Stack


class LambdaAlarms:
    def __init__(
            self,
            scope: Stack,
            prefix: str,
            sns_topic: ITopic,
            lambda_function: IFunction
    ) -> None:
        self.__prefix = prefix
        self.__scope = scope
        self.__sns_topic = sns_topic
        self.__lambda_function = lambda_function

        self.__errors_alarm = CfnAlarm(
            scope=self.__scope,
            id=self.__prefix + 'ErrorsCountAlarm',
            actions_enabled=True,
            alarm_name=self.__prefix + 'ErrorsCountAlarm',
            alarm_description=f'Lambda function {self.__lambda_function.function_name} errors count alarm.',
            dimensions=[CfnAlarm.DimensionProperty(name='FunctionName', value=self.__lambda_function.function_name)],
            metric_name='Errors',
            namespace='AWS/Lambda',
            alarm_actions=[
                self.__sns_topic.topic_arn
            ],

            # Fire an alarm if at least one event has occurred within 10 minutes.
            # This way we will immanently know when a function has crashed or is crashing.
            evaluation_periods=1,
            period=600,
            comparison_operator='GreaterThanThreshold',
            threshold=0,
            statistic='Sum',
        )

        self.__throttles_alarm = CfnAlarm(
            scope=self.__scope,
            id=self.__prefix + 'ThrottlesAlarm',
            actions_enabled=True,
            alarm_name=self.__prefix + 'ThrottlesAlarm',
            alarm_description=f'Lambda function {self.__lambda_function.function_name} throttles count alarm.',
            dimensions=[CfnAlarm.DimensionProperty(name='FunctionName', value=self.__lambda_function.function_name)],
            metric_name='Throttles',
            namespace='AWS/Lambda',
            alarm_actions=[
                self.__sns_topic.topic_arn
            ],

            # Fire an alarm if average events is higher than 0 within 1 minute.
            # This way we can constantly push alarm notifications that a throttling is happening.
            evaluation_periods=1,
            period=60,
            comparison_operator='GreaterThanThreshold',
            statistic='Average',
            threshold=0,
        )

    @property
    def errors_alarm(self) -> CfnAlarm:
        return self.__errors_alarm

    @property
    def throttles_alarm(self) -> CfnAlarm:
        return self.__throttles_alarm
