import os
import json
import datetime
import boto3
import requests
from botocore.exceptions import ClientError

# DynamoDB table holding config items: { ticker: string, threshold: number }
dynamo = boto3.resource('dynamodb')
table = dynamo.Table(os.getenv('CONFIG_TABLE'))

# Name of the analyzer Lambda (set this in serverless.yml)
ANALYZER_FN = os.getenv('ANALYZER_FUNCTION_NAME')

# Coinbase REST endpoint
COINBASE_API = "https://api.exchange.coinbase.com"

def handler(event, context):
    # 1) Load all configured tickers
    configs = table.scan().get('Items', [])

    payload = []
    for cfg in configs:
        ticker = cfg['ticker']
        threshold = float(cfg.get('threshold', 0.02))

        # 2) Get current price
        resp = requests.get(f"{COINBASE_API}/products/{ticker}-USD/ticker")
        resp.raise_for_status()
        data = resp.json()
        current_price = float(data['price'])
        timestamp = data['time']  # ISO8601

        # 3) Fetch 5-minute-ago price via candles endpoint
        end = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        start = end - datetime.timedelta(minutes=5)
        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "granularity": 60
        }
        hist = requests.get(f"{COINBASE_API}/products/{ticker}-USD/candles", params=params)
        hist.raise_for_status()
        candles = hist.json()  # [[time, low, high, open, close], ...]
        prev_price = float(candles[-1][4]) if candles else current_price

        # 4) Build point tuple
        payload.append({
            "ticker": ticker,
            "price": current_price,
            "previous_price": prev_price,
            "time": timestamp,
            "threshold": threshold
        })

    # 5) Invoke the analyzer asynchronously
    if payload:
        lambda_client = boto3.client('lambda')
        try:
            lambda_client.invoke(
                FunctionName=ANALYZER_FN,
                InvocationType="Event",
                Payload=json.dumps(payload)
            )
        except ClientError as e:
            print("Error invoking analyzer:", e)

    return {
        "statusCode": 200,
        "body": json.dumps({"processed": len(payload)})
    }
