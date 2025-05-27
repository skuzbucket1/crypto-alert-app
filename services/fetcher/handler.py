# services/fetcher/handler.py

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import json
import datetime
import boto3
import requests
from botocore.exceptions import ClientError


CB_API_URL = "https://api.exchange.coinbase.com"
dynamo = boto3.resource("dynamodb")
config_table = dynamo.Table(os.getenv("CONFIG_TABLE"))
lambda_client = boto3.client("lambda")
ANALYZER_FN = os.getenv("ANALYZER_FUNCTION_NAME")

def handler(event, context):
    try:
        configs = config_table.scan().get("Items", [])
    except ClientError as e:
        print("DynamoDB scan failed:", e)
        return {"statusCode":500,"body":json.dumps({"error":"Config read failed"})}

    payload = []
    for cfg in configs:
        ticker    = cfg["ticker"]
        threshold = float(cfg.get("threshold",0.02))

        # public ticker endpoint (no auth required)
        r1 = requests.get(f"{CB_API_URL}/products/{ticker}-USD/ticker")
        r1.raise_for_status()
        d1 = r1.json()
        current_price = float(d1["price"])
        timestamp     = d1["time"]

        # public candles endpoint (no auth required)
        end_dt   = datetime.datetime.fromisoformat(timestamp.replace("Z","+00:00"))
        start_dt = end_dt - datetime.timedelta(minutes=5)
        params   = {
            "start": start_dt.isoformat(),
            "end":   end_dt.isoformat(),
            "granularity": 60
        }
        r2 = requests.get(f"{CB_API_URL}/products/{ticker}-USD/candles", params=params)
        r2.raise_for_status()
        candles = r2.json()
        prev_price = float(candles[-1][4]) if candles else current_price

        payload.append({
            "ticker": ticker,
            "price": current_price,
            "previous_price": prev_price,
            "time": timestamp,
            "threshold": threshold
        })

    if payload:
        lambda_client.invoke(
            FunctionName=ANALYZER_FN,
            InvocationType="Event",
            Payload=json.dumps(payload)
        )

    return {"statusCode":200, "body":json.dumps({"processed": len(payload)})}
