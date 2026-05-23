from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as event_sources,
)
from constructs import Construct


class SupportTicketTriageAgentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Dead Letter Queue
        dlq = sqs.Queue(
            self,
            "SupportTicketDLQ",
            retention_period=Duration.days(14)
        )

        # Main Queue
        ticket_queue = sqs.Queue(
            self,
            "SupportTicketQueue",
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=dlq
            )
        )

        # DynamoDB Table
        tickets_table = dynamodb.Table(
            self,
            "TicketsTable",
            partition_key=dynamodb.Attribute(
                name="ticket_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Lambda Function
        processor_lambda = _lambda.Function(
            self,
            "TicketProcessorLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("src"),
            timeout=Duration.seconds(60),
            environment={
                "TABLE_NAME": tickets_table.table_name
            }
        )

        # Permissions
        tickets_table.grant_write_data(processor_lambda)

        # SQS Trigger
        processor_lambda.add_event_source(
            event_sources.SqsEventSource(ticket_queue)
        )
