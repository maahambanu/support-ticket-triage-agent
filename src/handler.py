import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    for record in event["Records"]:

        body = json.loads(record["body"])

        ticket_id = body["ticket_id"]
        message = body["message"]

        # Mock AI Classification
        urgency = "HIGH" if "urgent" in message.lower() else "LOW"

        drafted_reply = (
            "We received your support ticket and "
            "our team will respond shortly."
        )

        item = {
            "ticket_id": ticket_id,
            "message": message,
            "urgency": urgency,
            "drafted_reply": drafted_reply,
            "created_at": datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps("Processed successfully")
    }