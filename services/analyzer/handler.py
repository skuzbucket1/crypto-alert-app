import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import json
import boto3
from strategies.momentum import check as momentum_check
from strategies.mean_reversion import check as mr_check

# SNS Topic that the “notify” function is subscribed to
SNS = boto3.client('sns')
ALERT_TOPIC = os.getenv('ALERT_TOPIC_ARN')

def handler(event, context):
    # event is a list of price-point dicts
    alerts = []

    for pt in event:
        ticker = pt['ticker']
        # momentum: % change from previous
        if momentum_check(pt, pt['threshold']):
            alerts.append({
                "ticker": ticker,
                "signal": "BUY",
                "algo": "momentum",
                "price": pt['price'],
                "time": pt['time']
            })

        # mean-reversion: outside Bollinger Bands
        if mr_check(pt, window=20, stddev_mult=2):
            alerts.append({
                "ticker": ticker,
                "signal": "SELL",
                "algo": "mean_reversion",
                "price": pt['price'],
                "time": pt['time']
            })

    # publish all alerts as a single SNS message
    if alerts:
        SNS.publish(
            TopicArn=ALERT_TOPIC,
            Subject="Crypto Alert",
            Message=json.dumps(alerts)
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"alerts": alerts})
    }
