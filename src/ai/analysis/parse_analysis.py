import os, sys, json

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

def load_latest_analysis():
    data_dir = os.path.join(project_root, "data", "analysis_results")
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"analysis results directory not found: {data_dir}")

    files = [os.path.join(data_dir, fn) for fn in os.listdir(data_dir) if fn.lower().endswith(".json")]
    if not files:
        raise FileNotFoundError(f"No analysis result files found in {data_dir}")

    # pick the most recently modified file
    latest_file = max(files, key=os.path.getmtime)
    with open(latest_file, "r") as f:
        last_analysis = json.load(f)
    return last_analysis

def get_analysis_metadata():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['analysis_metadata']

def get_market_structure():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['market_structure']

def get_liquidity_zones():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['liquidity']

def get_order_blocks():
    last_analysis = load_latest_analysis()  
    return json.loads(last_analysis)['order_blocks']

def get_fair_value_gaps():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['fair_value_gaps']

def get_chart_patterns():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['chart_patterns']

def get_trading_setups():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['trading_setups']

def get_summary():
    last_analysis = load_latest_analysis()
    return json.loads(last_analysis)['summary']
