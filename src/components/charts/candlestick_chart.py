import os, sys
import streamlit as st
import pandas as pd

from lightweight_charts.widgets import StreamlitChart

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.api.bybit.history_data import get_data
from src.ai.analysis.parse_analysis import get_liquidity_zones, get_order_blocks, get_fair_value_gaps

def candlestick_chart(symbol,height, width):
    interval = "5"

    # Data Preparation
    def map_timeframe_to_interval(timeframe: str) -> str:
        mapping = {
            '1m': '1',
            '5m': '5',
            '15m': '15',
            '1h': '60',
            '4h': '240',
            '1d': 'D'
        }
        return mapping.get(timeframe, '5')


    with st.container(horizontal_alignment="left"):

        option_map = {
            0: "1m",
            1: "5m",
            2: "15m",
            3: "1h",
            4: "4h",
            5: "1d"
        }

        timeframe_switch = st.segmented_control(
            default=1,
            label="Timeframe",
            label_visibility="collapsed",
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single",
        )

    # Update interval based on selection
    if timeframe_switch is not None:
        interval = map_timeframe_to_interval(option_map[timeframe_switch])

    def data_loader():
        # load base data
        base_data = pd.DataFrame(get_data(symbol, "USDT", interval)).sort_values(by='time')

        # extend time series into the future
        max_time = pd.to_datetime(base_data['time'].max())
        start_time = max_time + pd.Timedelta(minutes=int(interval) if interval not in ['D'] else 1440)
        future_time_series = pd.date_range(
            start=start_time,
            periods=100,
            freq=f"{interval}min" if interval not in ['D'] else 'D')
        extend_time = pd.DataFrame({'time': future_time_series}).sort_values(by='time')

        # combine base data with extended time series
        combined = pd.concat([base_data, extend_time], ignore_index=False)
        return combined

    with st.container(horizontal_alignment="center"):
        chart = StreamlitChart(
            height=height,
            width=width
        )

        chart.layout(background_color="#0a0a0a", text_color="#ffffff")
        chart.grid(vert_enabled=False, horz_enabled=False)
        chart.set(data_loader())

        # Add liquidity zones as markers
        liquidity_zones = get_liquidity_zones(symbol, int(interval) if interval not in ['D'] else 1440)

        if liquidity_zones["nearest_swing_high"] != {}:
            chart.marker(
                time=pd.to_datetime(liquidity_zones["nearest_swing_high"]["timestamp"]),
                text=f"{liquidity_zones['nearest_swing_high']['significance']} | {liquidity_zones['nearest_swing_high']['swept']}",
                color="#e91e1ea6",
                shape="arrowDown",
                position="above"
            )

        if liquidity_zones["nearest_swing_low"] != {}:
            chart.marker(
                time=pd.to_datetime(liquidity_zones["nearest_swing_low"]["timestamp"]),
                text=f"{liquidity_zones['nearest_swing_low']['significance']} | {liquidity_zones['nearest_swing_low']['swept']}",
                color="#2195F3B2",
                shape="arrowUp",
                position="below"
            )
        
        # Add order blocks as boxes
        order_blocks = get_order_blocks(symbol)

        if order_blocks:
            supply = order_blocks["nearest_supply"]
            chart.box(
                start_time=pd.to_datetime(supply["timestamp"]),
                end_time=pd.Timestamp.now(),
                start_value=supply["price_high"],
                end_value=supply["price_low"],
                fill_color="#FF00001F",
                color="#FF000000"
            )

            demand = order_blocks["nearest_demand"]
            chart.box(
                start_time=pd.to_datetime(demand["timestamp"]),
                end_time=pd.Timestamp.now(),
                start_value=demand["price_low"],
                end_value=demand["price_high"],
                fill_color="#04520446",
                color="#00FF0000"
            )
        
        # Add fair value gaps as boxes
        fair_value_gaps = get_fair_value_gaps(symbol)

        for fvg in fair_value_gaps:
            if fvg["timeframe"] == option_map[timeframe_switch]:
                if fvg["type"] == "bullish":
                    chart.box(
                        start_time=pd.to_datetime(fvg["timestamp"]),
                        end_time=pd.to_datetime(fvg["timestamp"]) + pd.Timedelta(minutes=int(interval) if interval not in ['D'] else 1440),
                        start_value=fvg["price_low"],
                        end_value=fvg["price_high"],
                        fill_color="#054D127C",
                        color="#054D12FF"
                    )
                else:
                    chart.box(
                        start_time=pd.to_datetime(fvg["timestamp"]),
                        end_time=pd.to_datetime(fvg["timestamp"]) + pd.Timedelta(minutes=int(interval) if interval not in ['D'] else 1440),
                        start_value=fvg["price_low"],
                        end_value=fvg["price_high"],
                        fill_color="#FF22007D",
                        color="#560000FF"
                    )

        chart.load()
