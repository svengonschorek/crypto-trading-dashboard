import requests, datetime

import pandas as pd

def get_data(coin, base_coin, timeframe):

    url="https://data-api.binance.vision/api/v3/uiKlines"
    symbol = coin + base_coin

    filter = {
        'symbol': symbol,
        'interval': timeframe
    }

    result = requests.get(url, params=filter)
    result_json = result.json()

    data = []
    for kline in result_json:
        row = {
            "time": datetime.datetime.fromtimestamp(kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5]),
        }
        data.append(row)

    return data

if __name__ == "__main__":
    data = get_data("SOL", "USDT", "1m")
    print(pd.DataFrame(data))
