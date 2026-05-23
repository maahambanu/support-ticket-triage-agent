# Support Ticket Triage Agent

AI-powered serverless support ticket triage system built with AWS CDK (Python), Amazon Bedrock, AWS Lambda, Amazon SQS, and DynamoDB.

The system automatically:
- Reads support tickets from Amazon SQS
- Classifies urgency using Amazon Bedrock
- Drafts customer support replies using Claude models
- Stores processed tickets in DynamoDB
- Falls back to deterministic logic if Bedrock fails

---

# Architecture
<img width="1774" height="887" alt="ChatGPT Image May 23, 2026, 05_00_09 PM" src="https://github.com/user-attachments/assets/91ffd8a4-b329-4164-92d0-4644fb03a692" />


```text
Support Ticket
      ↓
Amazon SQS
      ↓
AWS Lambda
      ↓
Amazon Bedrock Runtime (Claude)
      ↓
Amazon DynamoDB
```

---

# Tech Stack

- AWS CDK (Python)
- AWS Lambda
- Amazon SQS
- Amazon DynamoDB
- Amazon Bedrock Runtime
- Claude 3 / Claude 3.5 Models
- Python
- Pytest
- boto3

---

# Features

## AI Ticket Processing
- AI-generated urgency classification
- AI-generated ticket categorization
- AI-generated sentiment analysis
- AI-generated customer support replies
- Confidence score generation
- Structured JSON response parsing
- Markdown-wrapped JSON cleanup

## Serverless Architecture
- Event-driven processing
- Fully managed AWS services
- Auto-scaling Lambda execution

## Resilience & Reliability
- Graceful Bedrock fallback logic
- Retry-safe architecture
- Regression-tested parsing logic

## Testing
- Unit tests
- Regression tests
- Mocked Bedrock responses
- Mocked DynamoDB interactions

---

# Project Structure

```text
support-ticket-triage-agent/
│
├── src/
│   └── handler.py
│
├── tests/
│   ├── unit/
│   │   ├── test_lambda.py
│   │   └── test_bedrock.py
│   │
│   └── regression/
│       ├── test_regression_lambda.py
│       └── test_regression_bedrock.py
│
├── support_ticket_triage_agent/
│   └── support_ticket_triage_agent_stack.py
│
├── app.py
├── cdk.json
├── requirements.txt
└── README.md
```

---

# AWS Services Used

## Amazon SQS
Used as the ingestion layer for support tickets.

## AWS Lambda
Processes SQS messages and orchestrates ticket analysis.

## Amazon Bedrock Runtime
Invokes Claude foundation models for:
- urgency classification
- response drafting

## Amazon DynamoDB
Stores processed support tickets.

---

# Deployment

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Bootstrap CDK

```bash
cdk bootstrap aws://ACCOUNT_ID/eu-west-1
```

---

## Deploy Infrastructure

```bash
cdk deploy
```

---

# Environment Variables

Configured via AWS CDK:

```python
environment={
    "TABLE_NAME": tickets_table.table_name,
    "USE_BEDROCK": "true",
    "BEDROCK_MODEL_ID": "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
}
```

---

# Sending Test Tickets

## Example Ticket

```json
{
  "ticket_id": "TICKET-001",
  "message": "Urgent: I was charged twice and need a refund"
}
```

---

## Send Message to SQS

```bash
aws sqs send-message \
  --queue-url "<QUEUE_URL>" \
  --message-body file://ticket.json \
  --region eu-west-1
```

---

# Running Tests

## Run All Tests

```bash
python -m pytest
```

---

# Test Coverage

## Unit Tests
- Lambda processing logic
- Bedrock response parsing
- Fallback behavior

## Regression Tests
- Markdown-wrapped JSON parsing
- Critical billing ticket workflows

---

# Bedrock Fallback Logic

If Bedrock fails:
- Lambda continues processing
- Deterministic fallback logic is used
- Ticket still gets stored in DynamoDB

Example:

```python
try:
    ai_result = analyze_ticket_with_bedrock(message)
except Exception:
    urgency = classify_urgency(message)
    drafted_reply = draft_reply(message, urgency)
```

---

# Example DynamoDB Record

```json
{
  "ticket_id": "TICKET-001",
  "message": "Urgent: I was charged twice",
  "urgency": "HIGH",
  "category": "Billing",
  "sentiment": "Angry",
  "confidence_score": 0.95,
  "drafted_reply": "Thank you for contacting us. I sincerely apologize for the duplicate charge. Our billing team is investigating this immediately.",
  "ai_used": true,
  "model_id": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "processing_status": "COMPLETED",
  "created_at": "2026-05-23T12:14:40Z"
}
```
---
## DynamoDB Decimal Serialization

Resolved DynamoDB float serialization issues by converting AI-generated confidence scores to Decimal types before persistence.
---

# CloudWatch Logging

Structured logs are emitted for:
- Bedrock responses
- processing failures
- fallback execution

Example:

```text
{
  "event": "ticket_processed",
  "ticket_id": "BEDROCK-001",
  "urgency": "HIGH",
  "category": "Billing",
  "ai_used": true
}
```

---

# Challenges Solved

## Bedrock Model Access
Resolved:
- Marketplace subscription permissions
- Anthropic use-case approval
- inference profile configuration

## AI JSON Parsing
Handled markdown-wrapped JSON responses from Claude models.

## Graceful Degradation
Implemented fallback logic to prevent pipeline failure during AI outages.

---

# Production Engineering Challenges Encountered

During development several real-world cloud engineering issues were encountered and resolved:

- Bedrock marketplace subscription permissions
- Anthropic model access approval
- inference profile model invocation
- markdown-wrapped JSON responses from Claude models
- DynamoDB float serialization issues
- graceful AI fallback handling
- environment variable isolation in pytest
- mocked Bedrock runtime testing
---

# Future Improvements

- Dead Letter Queue (DLQ)
- Confidence scoring
- Ticket categorization
- API Gateway integration
- GitHub Actions CI/CD
- CloudWatch dashboards
- Amazon X-Ray tracing

---

# Author

Maaham Banu

GitHub:
https://github.com/maahambanu
