import os
import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB table resource
dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.getenv('CONFIG_TABLE'))

def handler(event, context):
    # Support both REST API (httpMethod) and HTTP API v2 (requestContext.http.method)
    method = event.get('httpMethod') \
          or event.get('requestContext', {}) \
                     .get('http', {}) \
                     .get('method')
    path_params = event.get('pathParameters') or {}

    # GET /config -> list all ticker configs
    if method == 'GET':
        resp = table.scan()
        items = resp.get('Items', [])
        # Convert Decimal -> float for JSON serialization
        for it in items:
            if 'threshold' in it:
                it['threshold'] = float(it['threshold'])
        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }

    # POST /config -> add a new ticker config
    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        ticker = body['ticker']
        raw_threshold = body.get('threshold', 0.02)
        threshold = Decimal(str(raw_threshold))
        table.put_item(Item={
            "ticker": ticker,
            "threshold": threshold
        })
        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Added"})
        }

    # PUT /config/{ticker} -> update an existing ticker's threshold
    if method == 'PUT' and 'ticker' in path_params:
        body = json.loads(event.get('body', '{}'))
        ticker = path_params['ticker']
        raw_threshold = body.get('threshold', 0.02)
        threshold = Decimal(str(raw_threshold))
        table.update_item(
            Key={"ticker": ticker},
            UpdateExpression="SET threshold = :t",
            ExpressionAttributeValues={":t": threshold}
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Updated"})
        }

    # DELETE /config/{ticker} -> remove a ticker config
    if method == 'DELETE' and 'ticker' in path_params:
        ticker = path_params['ticker']
        table.delete_item(Key={"ticker": ticker})
        return {
            "statusCode": 204,
            "body": ""
        }

    # Fallback for unsupported methods
    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Bad Request"})
    }