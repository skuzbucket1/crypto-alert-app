import os, boto3

sns = boto3.client('sns')
TOPIC = os.getenv('ALERT_TOPIC_ARN')

def handler(event, context):
    # event = list of alerts from analyzer
    for alert in event:
        sns.publish(
            TopicArn=TOPIC,
            Message=str(alert),
            Subject=f\"Alert: {alert['ticker']} {alert['signal']}\"
        )
    return {'statusCode': 200}
