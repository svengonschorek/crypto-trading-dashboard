# Crypto LLM Analysis Dashboard

A web-based cryptocurrency trading analysis platform that performs AI-powered Smart Money Concepts (SMC) technical analysis on real-time K-line (candlestick) data from cryptocurrency exchanges.

## Features

- **Real-time Cryptocurrency Analysis**: Monitor 11+ cryptocurrencies (BTC, ETH, SOL, ADA, XRP, LTC, DOT, DOGE, AVAX, MATIC, HYPE)
- **AI-Driven SMC Analysis**: Leverage Claude (with Anthropic tool use) to identify high-probability trading setups
- **Interactive Candlestick Charts**: Visualize trading signals, order blocks, liquidity zones, and fair value gaps
- **Multi-Timeframe Analysis**: Analyze across 5m, 15m, 1h, 4h, and daily timeframes
- **Smart Trading Setups**: Get aggressive, conservative, and breakout trading recommendations with risk/reward ratios

## Technologies

- **Frontend**: Streamlit, Lightweight Charts
- **Backend**: Python 3.12
- **AI Models**: Anthropic Claude (`claude-haiku-4-5`) with tool use + prompt caching
- **Data Sources**: Bybit API, Binance API
- **Deployment**: Docker, Docker Compose

## Project Structure

```
realtime-kline-dashboard/
├── app/                          # Streamlit application
│   └── main.py                   # Main dashboard UI
├── src/                          # Core application code
│   ├── api/                      # Exchange API integrations
│   │   ├── binance/             # Binance API handlers
│   │   │   ├── history_data_binance.py
│   │   │   ├── reatime_data_binance.py
│   │   │   └── dashboard_binance.py
│   │   └── bybit/               # Bybit API handlers
│   │       ├── history_data.py
│   │       └── reatime_data.py
│   ├── ai/                       # AI analysis modules
│   │   ├── analysis/            # Analysis engine
│   │   │   ├── candle_analysis.py     # Orchestrates SMC analysis runs
│   │   │   └── parse_analysis.py      # Parses analysis JSON for the UI
│   │   ├── helpers/             # Claude API conversation helpers
│   │   │   └── functions.py           # Message handling, chat loop, tool dispatch
│   │   ├── tools/               # Anthropic tool-use definitions
│   │   │   └── klines_csv.py          # `get_klines_csv` tool + schema
│   │   └── prompts/             # LLM prompts
│   │       ├── system_prompt.txt
│   │       └── user_prompt.txt
│   └── components/              # UI components
│       └── charts/              # Chart visualizations
│           ├── candlestick_chart.py
│           └── realtime_chart.py
├── data/                         # Analysis results storage
│   └── analysis_results/        # JSON analysis files
├── .streamlit/                   # Streamlit configuration
│   ├── config.toml              # Server and theme settings
│   └── styles.css               # Custom styling
├── Dockerfile                    # Docker image definition
├── docker-compose.yml           # Service orchestration
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project metadata
└── .env                         # Environment variables
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Anthropic API key (for Claude AI)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crypto-trading-dashboard
   ```

2. **Create environment file**

   Create a `.env` file in the project root:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard**

   Open your browser and navigate to:
   ```
   http://localhost:8502
   ```

### Local Development (without Docker)

1. **Create uv environment**
   ```bash
   uv sync
   ```

2. **Run the Streamlit app**
   ```bash
   uv run streamlit run app/main.py --server.port=8502
   ```

## Usage

### Creating an Analysis

1. Select a cryptocurrency from the sidebar (e.g., BTC, ETH, SOL)
2. Click **"Create New Analysis"** to generate AI-powered SMC analysis
3. Wait for the analysis to complete (typically 30-60 seconds)
4. The analysis will be saved in `data/analysis_results/`

### Viewing Analysis Results

1. Select a coin from the dropdown
2. Choose an analysis from the available timestamps
3. Select a trading setup (Aggressive, Conservative, or Breakout)
4. Explore the interactive chart with:
   - **Liquidity Zones**: Swing high/low markers
   - **Order Blocks**: Supply/demand zones
   - **Fair Value Gaps**: Price inefficiencies
   - **Trading Setups**: Entry, take profit, and stop loss levels

### Chart Controls

- **Timeframe Selector**: Switch between 1m, 5m, 15m, 1h, 4h, 1d
- **Element Toggles**: Show/hide liquidity zones, order blocks, FVGs, and trading setups
- **Interactive Navigation**: Zoom and pan through historical data

## Analysis Components

The AI-powered analysis includes:

- **Market Structure**: Trend direction, higher highs/lows identification
- **Liquidity Zones**: Swing highs and lows where stop losses cluster
- **Order Blocks**: Supply and demand zones from institutional activity
- **Fair Value Gaps**: Price inefficiencies requiring rebalancing
- **Chart Patterns**: Technical patterns (head and shoulders, wedges, etc.)
- **Trading Setups**: Multiple entry strategies with:
  - Entry zone price ranges
  - Take profit levels (TP1, TP2)
  - Stop loss levels
  - Risk/reward ratios
  - Confidence scores

## Configuration

### Streamlit Configuration

Edit [.streamlit/config.toml](.streamlit/config.toml) to customize:
- Theme colors
- Server settings
- Browser behavior

### Docker Configuration

Modify [docker-compose.yml](docker-compose.yml) to:
- Change exposed ports
- Adjust volume mounts
- Update environment variables

## API Documentation

### Bybit API

The application uses Bybit's HTTP API to fetch historical K-line data:
- **Endpoint**: Get K-line data for trading pairs
- **Intervals**: 1, 5, 15, 60, 240, 1440 minutes
- **Data**: OHLCV (Open, High, Low, Close, Volume)

### AI Analysis

The SMC analysis is performed using **Claude** (`claude-haiku-4-5`) via the Anthropic Messages API. The analysis pipeline is split across three modules under `src/ai/`:

- **[src/ai/tools/klines_csv.py](src/ai/tools/klines_csv.py)** — Defines the `get_klines_csv` tool (and its schema) that Claude calls to fetch K-line data from Bybit on demand.
- **[src/ai/helpers/functions.py](src/ai/helpers/functions.py)** — Conversation helpers: message accumulation, the `chat` wrapper, the tool-dispatch loop (`run_tools` / `run_conversation`), and assistant-message prefilling to force clean JSON output. The system prompt is sent with `cache_control: ephemeral` to take advantage of prompt caching across turns.
- **[src/ai/analysis/candle_analysis.py](src/ai/analysis/candle_analysis.py)** — Orchestrates a full analysis run for a given symbol and persists the parsed JSON to `data/analysis_results/`.

Analysis results are returned in structured JSON format containing market structure, liquidity zones, order blocks, fair value gaps, and trading setups.

## Data Storage

Analysis results are stored as JSON files in the `data/analysis_results/` directory with the naming convention:
```
analysis_{SYMBOL}_{TIMESTAMP}.json
```

Each file contains:
- Analysis metadata (symbol, timeframes, timestamp)
- Market structure breakdown
- Liquidity levels
- Order blocks
- Fair value gaps
- Chart patterns
- Trading setups with detailed parameters

## Dependencies

### Core Dependencies

- `streamlit>=1.50.0` - Web application framework
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `anthropic>=0.71.0` - Claude AI API
- `google-genai>=1.45.0` - Gemini AI API
- `pybit>=5.12.0` - Bybit exchange API
- `requests>=2.32.5` - HTTP client
- `websocket-client>=1.8.0` - WebSocket streaming

### UI Dependencies

- `lightweight-charts>=2.1` - Financial charts
- `streamlit-browser-session-storage>=0.0.12`
- `streamlit-local-storage>=0.0.25`
- `streamlit-screen-stats>=0.0.82`

See [requirements.txt](requirements.txt) for the complete list.

## Architecture

```
User Interface (Streamlit)
    ↓
Dashboard & Controls
    ↓
    ├─→ Coin Selection
    ├─→ Analysis Selection
    ├─→ Create New Analysis
    │       ↓
    │   candle_analysis.perform_candle_analysis(symbol)
    │       ↓
    │   helpers/functions.run_conversation  ──┐
    │       ↓                                  │ tool-use loop
    │   Claude (claude-haiku-4-5)              │ (cached system prompt)
    │       ↓                                  │
    │   tool_use → get_klines_csv ─→ Bybit ───┘
    │       ↓
    │   Assistant prefill "{" → final JSON
    │       ↓
    │   Save to data/analysis_results/
    │
    └─→ Chart Rendering
        ├─→ analysis/parse_analysis.py
        ├─→ components/charts/* (lightweight-charts)
        └─→ Display Metadata
```

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies carries a high level of risk and may not be suitable for all investors. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite. Never trade with money you cannot afford to lose.
