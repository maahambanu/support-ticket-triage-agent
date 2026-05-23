import json
import os
import boto3
from datetime import datetime, UTC
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

bedrock = boto3.client("bedrock-runtime")

USE_BEDROCK = os.environ.get("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
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

Analyze the customer support ticket.

Return ONLY valid JSON in this exact format:

{{
  "urgency": "HIGH" or "LOW",
  "category": "Billing" or "Technical" or "General",
  "sentiment": "Angry" or "Neutral" or "Positive",
  "confidence_score": 0.0 to 1.0,
  "drafted_reply": "professional customer support reply"
}}

Ticket:
{message}
"""

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
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

    print(f"Raw Bedrock response text: {text_response}")

    cleaned_response = (
        text_response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(cleaned_response)


def process_ticket(body: dict) -> dict:

    ticket_id = body["ticket_id"]
    message = body["message"]

    if USE_BEDROCK:

        try:
            ai_result = analyze_ticket_with_bedrock(message)

            urgency = ai_result["urgency"]
            category = ai_result["category"]
            sentiment = ai_result["sentiment"]
            confidence_score = Decimal(
                str(ai_result["confidence_score"])
                    )
            drafted_reply = ai_result["drafted_reply"]

            ai_used = True

        except Exception as error:

            print(f"Bedrock failed, using fallback logic: {str(error)}")

            urgency = classify_urgency(message)
            category = "General"
            sentiment = "Neutral"
            confidence_score = 0.5

            drafted_reply = draft_reply(message, urgency)

            ai_used = False

    else:

        urgency = classify_urgency(message)

        category = "General"
        sentiment = "Neutral"
        confidence_score = 0.5

        drafted_reply = draft_reply(message, urgency)

        ai_used = False

    item = {
        "ticket_id": ticket_id,
        "message": message,
        "urgency": urgency,
        "category": category,
        "sentiment": sentiment,
        "confidence_score": confidence_score,
        "drafted_reply": drafted_reply,
        "ai_used": ai_used,
        "model_id": BEDROCK_MODEL_ID if ai_used else "fallback-logic",
        "processing_status": "COMPLETED",
        "created_at": datetime.now(UTC).isoformat()
    }

    print(json.dumps({
        "event": "ticket_processed",
        "ticket_id": ticket_id,
        "urgency": urgency,
        "category": category,
        "ai_used": ai_used
    }))

    return item


def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        item = process_ticket(body)
        table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps("Processed successfully")
    }