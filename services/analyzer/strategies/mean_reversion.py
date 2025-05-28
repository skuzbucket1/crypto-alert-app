import datetime
import requests
import math

COINBASE_API = "https://api.exchange.coinbase.com"

def check(point, window=20, stddev_mult=2):
    """
    Fetch the last `window` minutes of 1-minute candles,
    compute SMA and population stddev in pure Python, and
    return True if current price is outside [SMA ± stddev_mult * stddev].
    """
    ticker = point['ticker']
    # build time window
    end = datetime.datetime.fromisoformat(point['time'].replace('Z', '+00:00'))
    start = end - datetime.timedelta(minutes=window)
    params = {
        "start": start.isoformat(),
        "end":   end.isoformat(),
        "granularity": 60
    }

    # fetch candles
    resp = requests.get(f"{COINBASE_API}/products/{ticker}-USD/candles", params=params)
    resp.raise_for_status()
    candles = resp.json()  # [[time, low, high, open, close], ...]

    # extract closing prices
    closes = [c[4] for c in candles]
    if len(closes) < window:
        return False

    # take most recent `window` values
    closes = closes[-window:]

    # compute mean
    mean = sum(closes) / len(closes)
    # compute population variance & stddev
    variance = sum((c - mean) ** 2 for c in closes) / len(closes)
    sd = math.sqrt(variance)

    curr = point['price']
    upper = mean + stddev_mult * sd
    lower = mean - stddev_mult * sd

    return (curr > upper) or (curr < lower)