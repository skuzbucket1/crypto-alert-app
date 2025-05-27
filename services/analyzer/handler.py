import json
from strategies.momentum import check as momentum_check
from strategies.mean_reversion import check as mr_check

def handler(event, context):
    # event = list of { ticker, price, time }
    alerts = []
    for pt in event:
        if momentum_check(pt, {'threshold': 0.02}):
            alerts.append({'ticker': pt['ticker'], 'signal': 'BUY', 'algo': 'momentum'})
        if mr_check(pt, {'window': 20, 'stddev_mult': 2}):
            alerts.append({'ticker': pt['ticker'], 'signal': 'SELL', 'algo': 'mean_reversion'})
    return {
        'statusCode': 200,
        'body': json.dumps(alerts)
    }
