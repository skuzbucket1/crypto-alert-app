def check(point, threshold=0.02):
    """
    Returns True if |(current - previous) / previous| >= threshold.
    """
    prev = point.get('previous_price', 0)
    curr = point['price']
    if prev == 0:
        return False
    change = (curr - prev) / prev
    return abs(change) >= threshold
