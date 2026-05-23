import io
import json
import os
import importlib
from unittest.mock import MagicMock, patch


@patch("boto3.client")
@patch("boto3.resource")
def test_bedrock_success_with_markdown_json(mock_boto_resource, mock_boto_client):
    os.environ["TABLE_NAME"] = "fake-table"
    os.environ["USE_BEDROCK"] = "true"
    os.environ["BEDROCK_MODEL_ID"] = "test-model"

    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table

    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock

    bedrock_response = {
        "content": [
            {
                "text": """```json
{
  "urgency": "HIGH",
  "drafted_reply": "We are escalating this immediately."
}
```"""
            }
        ]
    }

    mock_bedrock.invoke_model.return_value = {
        "body": io.BytesIO(json.dumps(bedrock_response).encode("utf-8"))
    }

    import src.handler as handler
    importlib.reload(handler)

    body = {
        "ticket_id": "BEDROCK-TEST-001",
        "message": "Urgent: I was charged twice"
    }

    item = handler.process_ticket(body)

    assert item["ticket_id"] == "BEDROCK-TEST-001"
    assert item["urgency"] == "HIGH"
    assert item["drafted_reply"] == "We are escalating this immediately."


@patch("boto3.client")
@patch("boto3.resource")
def test_bedrock_failure_falls_back_to_mock_logic(mock_boto_resource, mock_boto_client):
    os.environ["TABLE_NAME"] = "fake-table"
    os.environ["USE_BEDROCK"] = "true"
    os.environ["BEDROCK_MODEL_ID"] = "test-model"

    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table

    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock
    mock_bedrock.invoke_model.side_effect = Exception("Bedrock unavailable")

    import src.handler as handler
    importlib.reload(handler)

    body = {
        "ticket_id": "FALLBACK-001",
        "message": "Urgent: Payment failed"
    }

    item = handler.process_ticket(body)

    assert item["ticket_id"] == "FALLBACK-001"
    assert item["urgency"] == "HIGH"
    assert "urgent support ticket" in item["drafted_reply"].lower()