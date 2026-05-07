import pandas as pd
import os, json, sys

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.ai.helpers.functions import add_user_message, run_conversation

def perform_candle_analysis(symbol="SOL"):
    '''Perform SMC analysis for a given symbol by fetching klines data and analyzing it with the model.'''
    # Navigate to prompts directory
    prompts_dir = os.path.join(script_dir, "..", "prompts")
    with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read()
    
    with open(os.path.join(prompts_dir, "user_prompt.txt"), "r") as file:
        user_prompt = file.read()
    
    # Initialize conversation messages and add initial user message with the symbol to analyze
    messages = []
    add_user_message(
        messages,
        f'''You are going to fetch klines data for {symbol}/USDT and analyze it.''' + user_prompt
    )

    messages = run_conversation(
        messages,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
    )

    # Extract the final response content and parse it as JSON
    try:
        final_response = json.loads(messages[-1]["content"])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {str(e)}")
        final_response = {"error": "Failed to parse JSON response", "details": str(e)}

    # Save response to JSON file
    now = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    # Save to project root data directory
    project_root = os.path.join(script_dir, "..", "..", "..")
    data_dir = os.path.join(project_root, "data", "analysis_results")
    file_name = os.path.join(data_dir, f"analysis_{symbol}_USDT_{now}.json")

    with open(file_name, "w") as file:
        json.dump(final_response, file)

if __name__ == "__main__":
    perform_candle_analysis(symbol="SOL")
