import os
import json
import boto3
from boto3.dynamodb.conditions import Key

dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.getenv('CONFIG_TABLE'))

def handler(event, context):
    method = event['httpMethod']
    path_params = event.get('pathParameters') or {}

    if method == 'GET':
        # List all configs
        resp = table.scan()
        return {
            "statusCode": 200,
            "body": json.dumps(resp.get('Items', []))
        }

    if method == 'POST':
        body = json.loads(event.get('body', '{}'))
        ticker = body['ticker']
        threshold = body.get('threshold', 0.02)
        table.put_item(Item={"ticker": ticker, "threshold": threshold})
        return {"statusCode": 201, "body": json.dumps({"message": "Added"})}

    if method == 'PUT' and 'ticker' in path_params:
        body = json.loads(event.get('body', '{}'))
        ticker = path_params['ticker']
        threshold = body.get('threshold', 0.02)
        table.update_item(
            Key={"ticker": ticker},
            UpdateExpression="SET threshold = :t",
            ExpressionAttributeValues={":t": threshold}
        )
        return {"statusCode": 200, "body": json.dumps({"message": "Updated"})}

    if method == 'DELETE' and 'ticker' in path_params:
        ticker = path_params['ticker']
        table.delete_item(Key={"ticker": ticker})
        return {"statusCode": 204, "body": ""}

    return {"statusCode": 400, "body": json.dumps({"error": "Bad Request"})}
