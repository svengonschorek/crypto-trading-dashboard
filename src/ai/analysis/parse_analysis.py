import os, sys, json
import time, datetime

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.api.bybit.history_data import get_data

def load_latest_analysis(symbol=None):
    data_dir = os.path.join(project_root, "data", "analysis_results")
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"analysis results directory not found: {data_dir}")

    files = [os.path.join(data_dir, fn) for fn in os.listdir(data_dir) if fn.lower().endswith(".json") and (fn.startswith(f"analysis_{symbol}_"))]
    if not files:
        latest_file = None
        return json.dumps({
            "analysis_metadata": {},
            "market_structure": {},
            "liquidity": {"nearest_swing_high": {}, "nearest_swing_low": {}},
            "order_blocks": [],
            "fair_value_gaps": [],
            "chart_patterns": [],
            "trading_setups": [],
            "summary": {}
        })
    else:
        files = sorted(files, key=os.path.getmtime, reverse=True)
        latest_file = files[0]
        with open(latest_file, "r") as f:
            last_analysis = json.load(f)

        return last_analysis

def get_analysis_metadata(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['analysis_metadata']

def get_market_structure(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['market_structure']

def get_liquidity_zones(symbol=None, interval=None):
    last_analysis = load_latest_analysis(symbol)
    if int(interval) >= 5:
        return json.loads(last_analysis)['liquidity']
    else:
        return {"nearest_swing_high": {}, "nearest_swing_low": {}}

def get_order_blocks(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['order_blocks']

def get_fair_value_gaps(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['fair_value_gaps']

def get_chart_patterns(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['chart_patterns']

def get_trading_setups(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['trading_setups']

def get_summary(symbol=None):
    last_analysis = load_latest_analysis(symbol)
    return json.loads(last_analysis)['summary']

def get_priority_trading_setup(symbol=None):
    trading_setups = get_trading_setups(symbol)
    summary = get_summary(symbol)
    prio_setup = None

    for setup in trading_setups:
        if setup.get("id", 0) == summary.get("recommended_setup_id", -1):
            prio_setup = setup
            break
    
    return json.dumps(prio_setup, indent=2) if prio_setup else json.dumps({"error": "No priority trading setup found"}, indent=2)

def get_trading_setup_timesstamps(symbol=None):
    prio_trading_setup = get_priority_trading_setup(symbol=symbol)
    analysis_metadata = get_analysis_metadata(symbol=symbol)

    # return empty dict if no analysis metadata found
    if analysis_metadata == {}:
        return {}

    analysis_timestamp = analysis_metadata.get("timestamp", 0)

    # transform analysis timestamp in from iso to milliseconds
    analysis_timestamp_milli = datetime.datetime.fromisoformat(analysis_timestamp).timestamp() * 1000

    # calculate limit based on current time and analysis timestamp
    current_timestamp = int(time.time() * 1000)
    minutes_diff = (current_timestamp - analysis_timestamp_milli) / (1000 * 60)
    limit = int(minutes_diff / 5) + 1

    # load historic data from bybit
    historic_data = get_data(symbol=symbol, quote="USDT", timeframe="5", limit=limit)

    # calculate if and when the entry price was hit
    if prio_trading_setup != "{}":
        entry_price = json.loads(prio_trading_setup).get("entry_zone").get("optimal_entry")
        direction = json.loads(prio_trading_setup).get("direction")

        # look in python dataframe if entry price was hit
        if direction == "long":
            mask = (historic_data['high'] <= entry_price) & (historic_data['low'] > entry_price)
        else:
            mask = (historic_data['high'] >= entry_price) & (historic_data['low'] < entry_price)

        hits = historic_data[mask].sort_values('time')
        first_entry_hit = hits.iloc[0] if not hits.empty else None

        if first_entry_hit is not None:
            entry_level = {
                "entry_price": entry_price,
                "direction": direction,
                "timestamp": first_entry_hit['time'],
                "description": json.loads(prio_trading_setup).get("entry_zone").get("description")
            }
        else:
            entry_level = {
                "entry_price": entry_price,
                "direction": direction,
                "timestamp": None,
                "description": json.loads(prio_trading_setup).get("entry_zone").get("description")
            }

        # check if take profit levels were hit after entry
        take_profit_levels = json.loads(prio_trading_setup).get("take_profit_targets", [])
        profit_levels = []

        if direction == "long" and first_entry_hit is not None:
            for tp in take_profit_levels:
                tp_price = tp.get("price")
                tp_mask = (historic_data['time'] > first_entry_hit['time']) & (historic_data['high'] >= tp_price)
                tp_hits = historic_data[tp_mask]
                if not tp_hits.empty:
                    first_tp_hit = tp_hits.iloc[0]
                    profit_row = {
                        "level": tp.get("level"),
                        "take_profit_price": tp_price,
                        "reason": tp.get("reasoning"),
                        "timestamp": first_tp_hit['time']
                    }
                    profit_levels.append(profit_row)
                else:
                    profit_row = {
                        "level": tp.get("level"),
                        "take_profit_price": tp_price,
                        "reason": tp.get("reasoning"),
                        "timestamp": None
                    }
                    profit_levels.append(profit_row)

        elif direction == "short" and first_entry_hit is not None:
            for tp in take_profit_levels:
                tp_price = tp.get("price")
                tp_mask = (historic_data['time'] > first_entry_hit['time']) & (historic_data['low'] <= tp_price)
                tp_hits = historic_data[tp_mask]
                if not tp_hits.empty:
                    first_tp_hit = tp_hits.iloc[0]
                    profit_row = {
                        "level": tp.get("level"),
                        "take_profit_price": tp_price,
                        "reason": tp.get("reasoning"),
                        "timestamp": first_tp_hit['time']
                    }
                    profit_levels.append(profit_row)
                else:
                    profit_row = {
                        "level": tp.get("level"),
                        "take_profit_price": tp_price,
                        "reason": tp.get("reasoning"),
                        "timestamp": None
                    }
                    profit_levels.append(profit_row)
        else:
            for tp in take_profit_levels:
                profit_row = {
                    "level": tp.get("level"),
                    "take_profit_price": tp.get("price"),
                    "reason": tp.get("reasoning"),
                    "timestamp": None
                }
                profit_levels.append(profit_row)
        
        # check if stop loss was hit after entry
        stop_loss = json.loads(prio_trading_setup).get("stop_loss")
        stop_loss_level = {
            "stop_loss_price": stop_loss,
            "timestamp": None,
            "description": json.loads(prio_trading_setup).get("stop_loss_reasoning")
        }
        
        if first_entry_hit is not None:
            if direction == "long":
                sl_mask = (historic_data['low'] <= stop_loss)
            else:
                sl_mask = (historic_data['high'] >= stop_loss)

            sl_hits = historic_data[sl_mask]
            if not sl_hits.empty:
                first_sl_hit = sl_hits.iloc[0]
                stop_loss_level = {
                    "stop_loss_price": stop_loss,
                    "timestamp": first_sl_hit['time'],
                    "description": json.loads(prio_trading_setup).get("stop_loss_reasoning")
                }

        # check if stop loss was hit before take profit levels
        if first_entry_hit is not None and 'stop_loss_level' in locals():
            sl_timestamp = stop_loss_level['timestamp']
            for profit in profit_levels:
                tp_timestamp = profit['timestamp']
                if sl_timestamp is not None and tp_timestamp is not None and sl_timestamp < tp_timestamp:
                    profit['timestamp'] = None

        # check if all take profit levels were hit before stop loss
        all_tp_hit = all(profit['timestamp'] is not None for profit in profit_levels)
        if 'stop_loss_level' in locals() and all_tp_hit:
            stop_loss_level['timestamp'] = None

        result = {
            "entry_level": entry_level,
            "take_profit_levels": profit_levels,
            "stop_loss_level": stop_loss_level
        }

        return result
