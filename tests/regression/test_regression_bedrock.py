import io
import json
import os
import importlib
from unittest.mock import MagicMock, patch


@patch("boto3.client")
@patch("boto3.resource")
def test_bedrock_markdown_json_regression(
    mock_boto_resource,
    mock_boto_client
):

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
  "drafted_reply": "Thank you for contacting us. I am escalating this billing issue immediately."
}
```"""
            }
        ]
    }

    mock_bedrock.invoke_model.return_value = {
        "body": io.BytesIO(
            json.dumps(bedrock_response).encode("utf-8")
        )
    }

    import src.handler as handler
    importlib.reload(handler)

    item = handler.process_ticket({
        "ticket_id": "REG-BEDROCK-001",
        "message": "Urgent: I was charged twice"
    })

    assert item["ticket_id"] == "REG-BEDROCK-001"
    assert item["urgency"] == "HIGH"

    assert (
        "escalating"
        in item["drafted_reply"].lower()
    )