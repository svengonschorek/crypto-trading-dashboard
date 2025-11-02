import os, sys
import streamlit as st

from st_screen_stats import ScreenData

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.append(os.path.abspath(project_root))

from src.components.charts.candlestick_chart import candlestick_chart
from src.ai.analysis.parse_analysis import get_analysis_metadata, get_market_structure, get_chart_patterns, get_summary, get_trading_setups, load_all_analysis
from src.ai.analysis.smc_analysis import perform_smc_analysis

screenD = ScreenData(setTimeout=1000)
screen_stats = screenD.st_screen_data()

# Dashboard styling an general layout
with open("./.streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="Crypto Trading Ideas and Analysis")

# Add sidebar with controls

# Coin selector
st.sidebar.title("Crypto Trading Analysis")
coins = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'LTC', 'DOT', 'DOGE', 'AVAX', 'MATIC', 'HYPE']
selected_coin = st.sidebar.selectbox('Coin', coins, index=0)

# Analysis selector
analysis = load_all_analysis(symbol=selected_coin)
selected_analysis_timestamp = st.sidebar.selectbox("Analysis", [item['analysis_timestamp'] for item in analysis], index=0)

timestamp_file_map = {item['analysis_timestamp']: item['file_name'] for item in analysis}
analysis_filename = timestamp_file_map.get(selected_analysis_timestamp)

# Trading setup selector
trading_setups = get_trading_setups(file_name=analysis_filename)

setups = []
for setup in trading_setups:
    if setup['setup_priority'] == 1:
        row = {
            "id": setup['id'],
            "style": setup['style'],
            "selector": setup['style'].capitalize() + " (recommended)"
        }
        setups.append(row)
    else:
        row = {
            "id": setup['id'],
            "style": setup['style'],
            "selector": setup['style'].capitalize()
        }
        setups.append(row)

selected_trading_setup = st.sidebar.selectbox("Trading Setups", [item['selector'] for item in setups], index=0)
trading_setups_selector_map = {item['selector']: item['id'] for item in setups}
trading_setup_id = trading_setups_selector_map.get(selected_trading_setup)

# Create New Analysis button
if st.sidebar.button("Create New Analysis"):
    with st.spinner("Performing SMC Analysis..."):
        perform_smc_analysis(symbol=selected_coin)
    st.sidebar.success("Analysis Data Refreshed!")

# Add Chart Elements

# Add main candlestick chart
candlestick_chart(
    symbol=selected_coin,
    file_name=analysis_filename,
    trading_setup_id=trading_setup_id,
    height=screen_stats['innerHeight'] * 0.75,
    width=screen_stats['innerWidth']
)

# Add analysis data below chart
analysis_metadata = get_analysis_metadata(file_name=analysis_filename)
market_structure = get_market_structure(file_name=analysis_filename)
chart_patterns = get_chart_patterns(file_name=analysis_filename)
summary = get_summary(file_name=analysis_filename)

st.subheader("Analysis Metadata:")
st.json(analysis_metadata)

st.subheader("Market Structure:")
st.json(market_structure)

st.subheader("Chart Patterns:")
st.json(chart_patterns)

st.subheader("Trading Setups:")
st.json(trading_setups)

st.subheader("Summary:")
st.json(summary)
