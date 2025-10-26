import os, sys
import streamlit as st

from st_screen_stats import ScreenData

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.append(os.path.abspath(project_root))

from src.components.charts.candlestick_chart import candlestick_chart
from src.ai.analysis.parse_analysis import get_analysis_metadata, get_market_structure, get_chart_patterns, get_summary, get_trading_setups
from src.ai.analysis.smc_analysis import perform_smc_analysis

screenD = ScreenData(setTimeout=1000)
screen_stats = screenD.st_screen_data()

# Dashboard styling
with open("./.streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.sidebar.title("Crypto Trading Analysis")
coins = ['BTC', 'ETH', 'SOL', 'ADA', 'XRP', 'LTC', 'DOT', 'DOGE', 'AVAX', 'MATIC', 'HYPE']
selected_coin = st.sidebar.selectbox('Coin', coins, index=0, label_visibility="hidden")

if st.sidebar.button("Refresh Analysis Data"):
    with st.spinner("Performing SMC Analysis..."):
        perform_smc_analysis(symbol=selected_coin)
    st.sidebar.success("Analysis Data Refreshed!")

candlestick_chart(
    symbol=selected_coin,
    height=screen_stats['innerHeight'] * 0.75,
    width=screen_stats['innerWidth']
)

analysis_metadata = get_analysis_metadata(symbol=selected_coin)
market_structure = get_market_structure(symbol=selected_coin)
chart_patterns = get_chart_patterns(symbol=selected_coin)
trading_setups = get_trading_setups(symbol=selected_coin)
summary = get_summary(symbol=selected_coin)

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
