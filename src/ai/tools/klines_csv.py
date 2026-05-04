import pandas as pd
import os, sys

from datetime import datetime
from anthropic.types import ToolParam

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.api.bybit.history_data import get_data

# Tool function to fetch klines data and return it as a CSV string
def get_klines_csv(symbol, interval="5", limit=200):
    """
    Fetch klines data and return as CSV string
    """
    if not symbol:
        raise ValueError("symbol cannot be empty")

    try:
        klines = get_data(symbol, quote="USDT", timeframe=interval, limit=limit)
        df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        return df.to_csv(index=False)
    except Exception as e:
        raise ValueError(f"Error fetching klines data: {str(e)}")

# Define the tool schema for get_klines_csv to specify how the model should call this function and what parameters it expects
get_klines_csv_schema = ToolParam(
    {
        "name": "get_klines_csv",
        "description": "Fetch klines data for a given symbol and time range, and return it as a CSV string.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The trading symbol to fetch klines for, e.g. 'SOL'. The quote currency is assumed to be 'USDT' and will be appended to the symbol automatically.",
                },
                "interval": {
                    "type": "string",
                    "description": "The interval for the klines. Supported values are '1','3','5','15','30','60','120','240','360','720','D','W','M' respectively. ",
                    "default": "5",
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of klines to fetch. The default is 200, and the maximum allowed is 2000.",
                    "default": 200,
                },
            },
            "required": ["symbol"],
        }
    }
)
