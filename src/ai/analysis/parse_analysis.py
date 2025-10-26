import os, sys, json

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

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
