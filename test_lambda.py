"""
Cloud Resume Challenge — test_lambda.py  (Step 11: Tests — pytest + moto)

5 unit tests that mock AWS using moto so no real AWS calls are made.
Run with:  pytest backend/tests/test_lambda.py -v
"""

import json
import os

import boto3
import pytest
from moto import mock_aws

# ---------------------------------------------------------------------------
# Point at a fake table before importing the module under test
# ---------------------------------------------------------------------------
os.environ["TABLE_NAME"]      = "cloud-resume-visitor-count"
os.environ["ALLOWED_ORIGIN"]  = "https://resume.example.com"
os.environ["AWS_DEFAULT_REGION"]        = "ap-south-1"
os.environ["AWS_ACCESS_KEY_ID"]         = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"]     = "testing"
os.environ["AWS_SECURITY_TOKEN"]        = "testing"
os.environ["AWS_SESSION_TOKEN"]         = "testing"

# Import after env vars are set
from backend.lambda.lambda_function import lambda_handler  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def dynamodb_table():
    """Spin up a mocked DynamoDB table for each test."""
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="ap-south-1")
        table = ddb.create_table(
            TableName="cloud-resume-visitor-count",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(
            TableName="cloud-resume-visitor-count"
        )
        yield table


def _post_event():
    return {"httpMethod": "POST", "body": None}


def _get_event():
    return {"httpMethod": "GET", "body": None}


def _options_event():
    return {"httpMethod": "OPTIONS", "body": None}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestVisitorCounter:

    # Test 1 — POST increments count from 0 → 1
    def test_post_increments_count_from_zero(self, dynamodb_table):
        response = lambda_handler(_post_event(), {})
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["visitor_count"] == 1

    # Test 2 — Multiple POSTs accumulate correctly
    def test_post_accumulates_on_repeated_calls(self, dynamodb_table):
        for _ in range(5):
            lambda_handler(_post_event(), {})
        response = lambda_handler(_post_event(), {})
        body = json.loads(response["body"])
        assert body["visitor_count"] == 6

    # Test 3 — GET returns current count without incrementing
    def test_get_does_not_increment_count(self, dynamodb_table):
        # Seed one visit
        lambda_handler(_post_event(), {})
        # GET twice — count must remain 1
        for _ in range(2):
            response = lambda_handler(_get_event(), {})
            body = json.loads(response["body"])
            assert body["visitor_count"] == 1

    # Test 4 — GET on empty table returns 0 (not an error)
    def test_get_on_empty_table_returns_zero(self, dynamodb_table):
        response = lambda_handler(_get_event(), {})
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["visitor_count"] == 0

    # Test 5 — OPTIONS pre-flight returns 200 with CORS headers
    def test_options_returns_cors_headers(self, dynamodb_table):
        response = lambda_handler(_options_event(), {})
        assert response["statusCode"] == 200
        headers = response["headers"]
        assert "Access-Control-Allow-Origin"  in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers
