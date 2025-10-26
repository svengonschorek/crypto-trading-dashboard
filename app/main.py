import os, sys
import streamlit as st

from st_screen_stats import ScreenData

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..")
sys.path.append(os.path.abspath(project_root))

from src.components.charts.candlestick_chart import candlestick_chart
from src.ai.analysis.parse_analysis import get_analysis_metadata, get_market_structure, get_chart_patterns, get_summary, get_trading_setups

screenD = ScreenData(setTimeout=1000)
screen_stats = screenD.st_screen_data()

width = screen_stats['innerWidth'] * 0.88 - screen_stats['innerWidth'] * 0.2
height = screen_stats['innerHeight'] * 0.8

# Dashboard styling
with open("./.streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(layout="wide")

st.title("Crypto Trading Analysis Dashboard")
st.write("")

candlestick_chart(
    height=screen_stats['innerHeight'] * 0.65,
    width=screen_stats['innerWidth'] * 0.95
)

analysis_metadata = get_analysis_metadata()
market_structure = get_market_structure()
chart_patterns = get_chart_patterns()
trading_setups = get_trading_setups()
summary = get_summary()

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
