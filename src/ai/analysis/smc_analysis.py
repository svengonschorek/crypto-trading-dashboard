import anthropic
import pandas as pd
import os, json, sys

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.api.bybit.history_data import get_data

def extract_json(text):
    """Extract JSON from markdown code blocks"""
    text = text.strip()
    # Remove code block markers
    if text.startswith('```'):
        lines = text.split('\n')
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line if it's ```
        if lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines)
    return text.strip()

def format_klines_compact(klines):
    """
    Convert klines to compact CSV format
    klines format: [[timestamp, open, high, low, close, volume], ...]
    """
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert to CSV string (most compact)
    return df.to_csv(index=False, float_format='%.2f')

def create_trading_message_with_cache(klines_5m, klines_15m, klines_1h, symbol="SOL"):
    """
    Create message with prompt caching for kline data
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Format klines compactly
    kline_data_5m = format_klines_compact(klines_5m)
    kline_data_15m = format_klines_compact(klines_15m)
    kline_data_1h = format_klines_compact(klines_1h)

    # Navigate to prompts directory
    prompts_dir = os.path.join(script_dir, "..", "prompts")
    
    with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read()
    
    with open(os.path.join(prompts_dir, "user_prompt.txt"), "r") as file:
        user_prompt = file.read()
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8096 ,
        system=[
            {
                "type": "text", 
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"}
            },
            {
                "type": "text",
                "text": f"Here is the kline data in CSV format for 5 min, 15 min and 1h timeframe:\n\n{kline_data_5m}\n\n{kline_data_15m}\n\n{kline_data_1h}",
                "cache_control": {"type": "ephemeral"}
            }
        ],
        messages=[
            {
                "role": "user",
                "content": user_prompt + "You are going to analyse " + symbol
            }
        ]
    )
    
    return response

def perform_smc_analysis(symbol="SOL"):
    """Perform SMC analysis and save results to JSON file"""
    klines_5m = get_data(symbol, "USDT", "5", 200)
    klines_15m = get_data(symbol, "USDT", "15", 200)
    klines_1h = get_data(symbol, "USDT", "60", 200)

    response = create_trading_message_with_cache(klines_5m, klines_15m, klines_1h, symbol)

    # Save response to JSON file
    now = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    # Save to project root data directory
    project_root = os.path.join(script_dir, "..", "..", "..")
    data_dir = os.path.join(project_root, "data", "analysis_results")
    file_name = os.path.join(data_dir, f"analysis_{symbol}_USDT_{now}.json")
    with open(file_name, "w") as file:
        json.dump(extract_json(response.content[0].text), file)

    # Check cache performance
    print(f"\nCache stats:")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")
    print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
