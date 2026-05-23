import json
import os
import boto3
from datetime import datetime, UTC

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

bedrock = boto3.client("bedrock-runtime")

USE_BEDROCK = os.environ.get("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)


def classify_urgency(message: str) -> str:
    if "urgent" in message.lower():
        return "HIGH"
    return "LOW"


def draft_reply(message: str, urgency: str) -> str:
    if urgency == "HIGH":
        return (
            "We received your urgent support ticket. "
            "Our team will prioritize it and respond shortly."
        )

    return (
        "We received your support ticket and "
        "our team will respond shortly."
    )


def analyze_ticket_with_bedrock(message: str) -> dict:
    prompt = f"""
You are a support ticket triage assistant.

Classify the ticket urgency and draft a short professional customer reply.

Return ONLY valid JSON in this format:
{{
  "urgency": "HIGH" or "LOW",
  "drafted_reply": "reply text"
}}

Ticket:
{message}
"""

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    text_response = response_body["content"][0]["text"]

    return json.loads(text_response)


def process_ticket(body: dict) -> dict:
    ticket_id = body["ticket_id"]
    message = body["message"]

    if USE_BEDROCK:
        ai_result = analyze_ticket_with_bedrock(message)
        urgency = ai_result["urgency"]
        drafted_reply = ai_result["drafted_reply"]
    else:
        urgency = classify_urgency(message)
        drafted_reply = draft_reply(message, urgency)

    return {
        "ticket_id": ticket_id,
        "message": message,
        "urgency": urgency,
        "drafted_reply": drafted_reply,
        "created_at": datetime.now(UTC).isoformat()
    }


def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        item = process_ticket(body)
        table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps("Processed successfully")
    }