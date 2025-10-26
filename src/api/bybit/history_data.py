import pandas as pd
import numpy as np

from pybit.unified_trading import HTTP

session = HTTP(testnet=False)

def _normalize_history_df(df: pd.DataFrame, timeframe) -> pd.DataFrame:
    """
    Normalize history dataframe for chart:
    - ensure 'time' column present and parsed
    - coerce OHLC/volume to numeric
    - drop rows without close
    - drop duplicate timestamps (keep last)
    - sort ascending and reset index
    - return 'time' as '%Y-%m-%d %H:%M:%S' strings (not integers)
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    df = df.copy()

    # parse time (handle numeric seconds/ms or ISO strings)
    ts = df['time']
    if pd.api.types.is_integer_dtype(ts) or pd.api.types.is_float_dtype(ts):
        maxv = int(ts.max())
        unit = 'ms' if maxv > 1_000_000_000_000 else 's'
        df['time'] = pd.to_datetime(df['time'], unit=unit, errors='coerce')
    else:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')

    df = df.dropna(subset=['time'])

    # coerce numeric OHLC/volume
    for c in ('open', 'high', 'low', 'close', 'volume'):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # if OHLC missing but close exists, fill them with close so chart can render
    if 'close' in df.columns:
        for c in ('open', 'high', 'low'):
            if c not in df.columns or df[c].isnull().all():
                df[c] = df['close']

    # drop rows without required candle values
    df = df.dropna(subset=['close'])

    # sort and remove duplicate times (keep last / most recent)
    df = df.sort_values('time').drop_duplicates(subset=['time'], keep='last').sort_values('time').reset_index(drop=True)

    # remove tz if present then format as requested string
    if pd.api.types.is_datetime64_any_dtype(df['time']):
        if df['time'].dt.tz is not None:
            df['time'] = df['time'].dt.tz_convert(None).dt.tz_localize(None)
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # ensure required columns exist
    for c in ('open', 'high', 'low', 'close'):
        if c not in df.columns:
            df[c] = np.nan
    if 'volume' not in df.columns:
        df['volume'] = 0

    return df

def get_data(symbol: str, quote: str, timeframe: str = "5", limit: int = 2000) -> list:

    symbol = f"{symbol}{quote}"

    result = session.get_kline(
        category="linear",
        symbol=symbol,
        interval=timeframe,
        limit=limit
    )

    data = []
    for kline in result['result']['list']:
        row = {
            "time": float(kline[0]),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5]),
        }
        data.append(row)

    raw_df = pd.DataFrame(data)
    return _normalize_history_df(raw_df, timeframe)
