"""
Cloud Resume Challenge — lambda_function.py  (Step 10: Python / boto3)

Lambda handler for the visitor counter API.
- GET  /count  → returns current count (no increment)
- POST /count  → increments and returns new count

DynamoDB table schema:
  PK (String): "visitor_count"   ← single record, atomic update
  count (Number): <integer>
"""

import json
import os
import boto3
from botocore.exceptions import ClientError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TABLE_NAME = os.environ.get("TABLE_NAME", "cloud-resume-visitor-count")
RECORD_KEY  = "visitor_count"

dynamodb = boto3.resource("dynamodb")
table    = dynamodb.Table(TABLE_NAME)

# ---------------------------------------------------------------------------
# CORS headers — allow your CloudFront domain
# ---------------------------------------------------------------------------
CORS_HEADERS = {
    "Access-Control-Allow-Origin":  os.environ.get("ALLOWED_ORIGIN", "*"),
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers":    {**CORS_HEADERS, "Content-Type": "application/json"},
        "body":       json.dumps(body),
    }


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------
def lambda_handler(event, context):
    method = event.get("httpMethod", "POST").upper()

    # CORS pre-flight
    if method == "OPTIONS":
        return _response(200, {})

    try:
        if method == "POST":
            # Atomic increment — safe under concurrent requests
            resp = table.update_item(
                Key={"id": RECORD_KEY},
                UpdateExpression="SET #c = if_not_exists(#c, :zero) + :one",
                ExpressionAttributeNames={"#c": "count"},
                ExpressionAttributeValues={":one": 1, ":zero": 0},
                ReturnValues="UPDATED_NEW",
            )
            count = int(resp["Attributes"]["count"])

        else:  # GET — read only
            resp = table.get_item(Key={"id": RECORD_KEY})
            item  = resp.get("Item", {})
            count = int(item.get("count", 0))

        return _response(200, {"visitor_count": count})

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        print(f"DynamoDB ClientError [{error_code}]: {exc}")
        return _response(500, {"error": "Database error", "detail": error_code})

    except Exception as exc:
        print(f"Unhandled exception: {exc}")
        return _response(500, {"error": "Internal server error"})
