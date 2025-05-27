import os, json, boto3, requests

dynamo = boto3.client('dynamodb')
TABLE = os.getenv('CONFIG_TABLE')

def handler(event, context):
    # 1) pull configured tickers from DynamoDB
    resp = dynamo.scan(TableName=TABLE)
    items = resp.get('Items', [])
    results = []
    for it in items:
        ticker = it['ticker']['S']
        url = f"https://api.exchange.coinbase.com/products/{ticker}-USD/ticker"
        r = requests.get(url)
        data = r.json()
        results.append({
            'ticker': ticker,
            'price': float(data['price']),
            'time': data['time']
        })
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
