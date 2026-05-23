import json
import os
from unittest.mock import MagicMock, patch


os.environ["TABLE_NAME"] = "fake-table"


@patch("boto3.resource")
def test_lambda_processes_urgent_ticket(mock_boto_resource):
    mock_table = MagicMock()
    mock_boto_resource.return_value.Table.return_value = mock_table

    import src.handler as handler

    event = {
        "Records": [
            {
                "body": json.dumps({
                    "ticket_id": "TICKET-100",
                    "message": "Urgent: I was charged twice"
                })
            }
        ]
    }

    response = handler.lambda_handler(event, None)

    assert response["statusCode"] == 200

    mock_table.put_item.assert_called_once()
    item = mock_table.put_item.call_args.kwargs["Item"]

    assert item["ticket_id"] == "TICKET-100"
    assert item["urgency"] == "HIGH"
    assert "drafted_reply" in item