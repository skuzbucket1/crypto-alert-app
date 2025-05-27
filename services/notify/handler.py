import os
import json
import boto3

# SES for email; fallback to SNS for SMS if you like
ses = boto3.client('ses')
EMAIL_FROM = os.getenv('EMAIL_FROM')     # e.g. "alerts@yourdomain.com"
EMAIL_TO = os.getenv('EMAIL_TO')         # comma-separated or list

def handler(event, context):
    # SNS-triggered Lambda delivers via event['Records']
    for record in event.get('Records', []):
        msg = record['Sns']['Message']
        alerts = json.loads(msg)

        for a in alerts:
            subject = f"{a['ticker']} {a['signal']} ({a['algo']})"
            body = (
                f"Time:  {a['time']}\n"
                f"Price: {a['price']:.4f}\n"
                f"Signal: {a['signal']} via {a['algo']}\n"
            )
            ses.send_email(
                Source=EMAIL_FROM,
                Destination={"ToAddresses": EMAIL_TO.split(",")},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}}
                }
            )

    return {"statusCode": 200}
