import os, sys
import streamlit as st
import pandas as pd

from lightweight_charts.widgets import StreamlitChart

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.api.bybit.history_data import get_data
from src.ai.analysis.parse_analysis import get_liquidity_zones, get_order_blocks, get_fair_value_gaps, get_analysis_metadata, get_trading_setup_timesstamps

def candlestick_chart(symbol, height, width):
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

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(horizontal_alignment="left"):
            option_map_timeframe = {
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
                options=option_map_timeframe.keys(),
                format_func=lambda option: option_map_timeframe[option],
                selection_mode="single",
            )
    
    with col2:
        with st.container(horizontal_alignment="right"):

            options_map_analysis = [
                "Liquidity Zones",
                "Order Blocks",
                "Fair Value Gaps",
                "Trading Setups"
            ]

            analysis_elements = st.segmented_control(
                default=[],
                label="Analysis Elements",
                label_visibility="collapsed",
                options=options_map_analysis,
                selection_mode="multi"
            )

    # Add empty row between controls and chart
    st.write("")
    # Update interval based on selection
    if timeframe_switch is not None:
        interval = map_timeframe_to_interval(option_map_timeframe[timeframe_switch])

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

        # Add time of analysis as a vertical line
        analysis_metadata = get_analysis_metadata(symbol)
        if analysis_metadata and "timestamp" in analysis_metadata:
            chart.vertical_line(
                time=pd.to_datetime(analysis_metadata["timestamp"]),
                width=2,
                color="#FFFFFF64",
                style="dashed",
                text="Analysis Time"
            )

        # Add liquidity zones as markers
        if "Liquidity Zones" in analysis_elements:
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
        if "Order Blocks" in analysis_elements:
            order_blocks = get_order_blocks(symbol)

            if order_blocks:
                supply = order_blocks["nearest_supply"]
                chart.box(
                    start_time=pd.to_datetime(supply["timestamp"]),
                    end_time=pd.Timestamp.now(),
                    start_value=supply["price_high"],
                    end_value=supply["price_low"],
                    fill_color="#ed354453",
                    color="#FF000000"
                )

                demand = order_blocks["nearest_demand"]
                chart.box(
                    start_time=pd.to_datetime(demand["timestamp"]),
                    end_time=pd.Timestamp.now(),
                    start_value=demand["price_low"],
                    end_value=demand["price_high"],
                    fill_color="#08998150",
                    color="#00FF0000"
                )
        
        # Add fair value gaps as boxes
        if "Fair Value Gaps" in analysis_elements:
            fair_value_gaps = get_fair_value_gaps(symbol)

            for fvg in fair_value_gaps:
                if fvg["timeframe"] == option_map_timeframe[timeframe_switch]:
                    if fvg["type"] == "bullish":
                        chart.box(
                            start_time=pd.to_datetime(fvg["timestamp"]),
                            end_time=pd.to_datetime(fvg["timestamp"]) + pd.Timedelta(minutes=int(interval) if interval not in ['D'] else 1440),
                            start_value=fvg["price_low"],
                            end_value=fvg["price_high"],
                            fill_color="#08998182",
                            color="#08998182"
                        )
                    else:
                        chart.box(
                            start_time=pd.to_datetime(fvg["timestamp"]),
                            end_time=pd.to_datetime(fvg["timestamp"]) + pd.Timedelta(minutes=int(interval) if interval not in ['D'] else 1440),
                            start_value=fvg["price_low"],
                            end_value=fvg["price_high"],
                            fill_color="#fb000851",
                            color="#fb000851"
                        )
        
        # Add trading setup as boxes
        if "Trading Setups" in analysis_elements:
            prio_trading_setup = get_trading_setup_timesstamps(symbol=symbol, interval=int(interval) if interval not in ['D'] else 1440)
            if prio_trading_setup:
                
                # calculate start and end times and values for boxes
                if prio_trading_setup["entry_level"]["timestamp"]:
                    start_time = prio_trading_setup["entry_level"]["timestamp"]
                else:
                    start_time = pd.Timestamp.now(tz='UTC') + pd.Timedelta(minutes=int(interval) + (5 * int(interval)) if interval not in ['D'] else 1440)

                if prio_trading_setup["take_profit_levels"] != []:
                    all_tp_hit = all(profit['timestamp'] is not None for profit in prio_trading_setup["take_profit_levels"])
                else :
                    all_tp_hit = False
                
                if prio_trading_setup["stop_loss_level"]["timestamp"]:
                    end_time = prio_trading_setup["stop_loss_level"]["timestamp"]
                elif all_tp_hit:
                    end_time = max(prio_trading_setup["take_profit_levels"], key=lambda x: x['timestamp'])['timestamp']
                else:
                    end_time = pd.Timestamp.now(tz='UTC') + pd.Timedelta(minutes=int(interval) + (20 * int(interval)) if interval not in ['D'] else 1440)

                if prio_trading_setup["entry_level"]["direction"] == "long":
                    end_value_tp = max(prio_trading_setup["take_profit_levels"], key=lambda x: x['take_profit_price'])['take_profit_price']
                else:
                    end_value_tp = min(prio_trading_setup["take_profit_levels"], key=lambda x: x['take_profit_price'])['take_profit_price']

                # draw boxes for take profit and stop loss levels
                chart.box(
                    start_time=start_time,
                    end_time=end_time,
                    start_value=prio_trading_setup["entry_level"]["entry_price"],
                    end_value=end_value_tp,
                    fill_color="#08998157",
                    color="#7D7D7D80",
                    width=1
                )

                chart.box(
                    start_time=start_time,
                    end_time=end_time,
                    start_value=prio_trading_setup["entry_level"]["entry_price"],
                    end_value=prio_trading_setup["stop_loss_level"]["stop_loss_price"],
                    fill_color="#ed35445f",
                    color="#7D7D7D80",
                    width=1
                )

                # draw markers for take profit and stop loss levels
                for tp in prio_trading_setup["take_profit_levels"]:
                    if tp["timestamp"]:
                        chart.marker(
                            time=pd.to_datetime(tp["timestamp"]),
                            text=f"TP @ {tp['level']}",
                            color="#089981",
                            shape="arrowUp" if prio_trading_setup["entry_level"]["direction"] == "long" else "arrowDown",
                            position="above" if prio_trading_setup["entry_level"]["direction"] == "long" else "below"
                        )
                
                if prio_trading_setup["stop_loss_level"]["timestamp"]:
                    chart.marker(
                        time=pd.to_datetime(prio_trading_setup["stop_loss_level"]["timestamp"]),
                        text=f"SL @ {prio_trading_setup['stop_loss_level']['stop_loss_price']}",
                        color="#ED3544",
                        shape="arrowDown" if prio_trading_setup["entry_level"]["direction"] == "long" else "arrowUp",
                        position="below" if prio_trading_setup["entry_level"]["direction"] == "long" else "above"
                    )

                # draw price line for entry level, take profit and stop loss levels
                chart.ray_line(
                    start_time=start_time,
                    value=prio_trading_setup["entry_level"]["entry_price"],
                    color="#4144E2FF",
                    style="dashed",
                    text="Entry Level",
                    width=1
                )

                for tp in prio_trading_setup["take_profit_levels"]:
                    chart.ray_line(
                        start_time=start_time,
                        value=tp["take_profit_price"],
                        color="#089981",
                        style="dashed",
                        text=f"Take Profit Level {tp['level']}",
                        width=1
                    )
                
                chart.ray_line(
                    start_time=start_time,
                    value=prio_trading_setup["stop_loss_level"]["stop_loss_price"],
                    color="#ED3544",
                    style="dashed",
                    text="Stop Loss Level",
                    width=1
                )

        chart.load()
