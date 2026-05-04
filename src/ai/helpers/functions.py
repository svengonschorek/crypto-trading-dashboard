import os, sys, json

from anthropic import Anthropic
from anthropic.types import Message

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
model = "claude-haiku-4-5"

# Add the project root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, "..", "..", "..")
sys.path.append(os.path.abspath(project_root))

from src.ai.tools.klines_csv import get_klines_csv, get_klines_csv_schema

# Helper functions for managing messages and interactions with the model, as well as tool functions that can be called by the model.
def add_user_message(messages: list[Message], content: str) -> list[Message]:
    """Add a user message to the conversation history."""
    messages.append(
        {
            "role": "user",
            "content": content.content if isinstance(content, Message) else content,
        }
    )
    return messages

def add_assistant_message(messages: list[Message], content: str) -> list[Message]:
    """Add an assistant message to the conversation history."""
    messages.append(
        {
            "role": "assistant",
            "content": content.content if isinstance(content, Message) else content,
        }
    )
    return messages

def chat(messages: list[Message], system=None, temperature=1.0, stop_sequences=[],  tools=None) -> Message:
    """Send a chat message to the model and receive a response."""
    params = {
        "model": model,
        "max_tokens": 8000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if tools:
        params["tools"] = tools
    
    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message


def text_from_message(message: Message) -> str:
    """Extract text content from a model message."""
    return "\n".join([block.text for block in message.content if block.type == "text"])

# Run tool calls in a loop to allow for multiple interactions with the model, such as fetching data, analyzing it, and then fetching more data based on the analysis.
def run_tool(tool_name, tool_input):
    """Run a tool function by name with the given input."""
    if tool_name == "get_klines_csv":
        return get_klines_csv(**tool_input)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
    
def run_tools(message):
    """Run all tool calls found in the model's message and return their results."""
    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": json.dumps(tool_output),
                    "is_error": False,
                }
            )
        except Exception as e:
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,
                    "content": f"Error: {str(e)}",
                    "is_error": True,
                }
            )
    
    return tool_result_blocks

def run_conversation(messages, system=None):
    while True:
        response = chat(messages, system=system, tools=[get_klines_csv_schema])
        add_assistant_message(messages, response)
        print(text_from_message(response))

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages

if __name__ == "__main__":
    # Navigate to prompts directory
    prompts_dir = os.path.join(script_dir, "..", "prompts")
    
    with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as file:
        system_prompt = file.read()
    
    with open(os.path.join(prompts_dir, "user_prompt.txt"), "r") as file:
        user_prompt = file.read()
    
    messages = []

    add_user_message(
        messages,
        user_prompt + "You are going to fetch klines data for SOL/USDT and analyze it."
     )
    
    run_conversation(messages, system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}])
