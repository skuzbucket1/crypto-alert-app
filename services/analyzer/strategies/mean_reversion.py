import datetime
import requests
import numpy as np

COINBASE_API = "https://api.exchange.coinbase.com"

def check(point, window=20, stddev_mult=2):
    """
    Fetches the last `window` minutes of 1-minute candles,
    computes SMA and stddev, and returns True if current price
    is outside [SMA ± stddev_mult * stddev].
    """
    ticker = point['ticker']
    end = datetime.datetime.fromisoformat(point['time'].replace('Z', '+00:00'))
    start = end - datetime.timedelta(minutes=window)
    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "granularity": 60
    }
    resp = requests.get(f"{COINBASE_API}/products/{ticker}-USD/candles", params=params)
    resp.raise_for_status()
    candles = resp.json()
    closes = [c[4] for c in candles]
    if len(closes) < window:
        return False

    arr = np.array(closes, dtype=float)
    sma = arr.mean()
    sd = arr.std()
    curr = point['price']

    upper = sma + stddev_mult * sd
    lower = sma - stddev_mult * sd
    return (curr > upper) or (curr < lower)
