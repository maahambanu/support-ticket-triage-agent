import json
import os
from unittest.mock import MagicMock, patch

os.environ["TABLE_NAME"] = "fake-table"


@patch("boto3.resource")
def test_urgent_billing_ticket_regression(mock_boto_resource):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table

    import src.handler as handler

    event = {
        "Records": [
            {
                "body": json.dumps({
                    "ticket_id": "REG-001",
                    "message": "Urgent: I was charged twice and need a refund"
                })
            }
        ]
    }

    response = handler.lambda_handler(event, None)

    assert response["statusCode"] == 200

    item = mock_table.put_item.call_args.kwargs["Item"]

    assert item["ticket_id"] == "REG-001"
    assert item["urgency"] == "HIGH"
    assert "charged twice" in item["message"]
    assert item["drafted_reply"] != ""