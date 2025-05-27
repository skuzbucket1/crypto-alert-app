import os, json, boto3

dynamo = boto3.client('dynamodb')
TABLE = os.getenv('CONFIG_TABLE')

def handler(event, context):
    method = event['httpMethod']
    body = json.loads(event.get('body','{}'))
    if method == 'GET':
        resp = dynamo.scan(TableName=TABLE)
        return {'statusCode': 200, 'body': json.dumps(resp['Items'])}
    if method == 'POST':
        dynamo.put_item(TableName=TABLE, Item={
            'ticker': {'S': body['ticker']},
            'threshold': {'N': str(body.get('threshold',1))}
        })
        return {'statusCode': 201}
    if method == 'DELETE':
        ticker = event['pathParameters']['ticker']
        dynamo.delete_item(TableName=TABLE, Key={'ticker':{'S':ticker}})
        return {'statusCode': 204}
    return {'statusCode': 400}
