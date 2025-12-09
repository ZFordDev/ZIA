# bot/Discord/zia.py
import discord  # Import the discord library for interacting with the Discord API.
import requests  # Import the requests library for making HTTP requests to the AI endpoints.
import os  # Import the os library for interacting with the operating system (e.g., file paths).
import json  # Import the json library for working with JSON data.
import sys  # Import the sys library for system-specific parameters and functions.
import datetime  # Import the datetime library for working with dates and times.

# Define paths to configuration and secret files.  These are used throughout the script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file.
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # Get the root directory of the project.
DISCORD_SECRETS_PATH = os.path.join(ROOT_DIR, "secrets", "connects", "discord.json")  # Path to the Discord secrets file (token, channel IDs).
ROUTE_PATH = os.path.join(ROOT_DIR, "secrets", "config", "route.json")  # Path to the route configuration file (AI endpoints, model).
PERSONA_PATH = os.path.join(ROOT_DIR, "config", "persona.json")  # Path to the persona configuration file (AI personality).
MEMORY_DIR = os.path.join(ROOT_DIR, "secrets", "db")  # Path to the directory where conversation memory will be stored.
APP_PATH = os.path.join(ROOT_DIR, "config", "app.json")  # Path to the application configuration file (memory limits, token limits).

# Create the memory directory if it doesn't exist.  This ensures that the bot can store conversation history.
os.makedirs(MEMORY_DIR, exist_ok=True)

# Load application configuration from app.json.  This file contains settings for memory and token limits.
try:
    with open(APP_PATH, "r") as f:
        app_config = json.load(f)
except Exception as e:
    # If the file fails to load, print a warning and use default values. This prevents the bot from crashing.
    print(f"⚠️ Failed to load app.json, using defaults: {e}")
    app_config = {
        "memory": {"log_limit": 100, "load_limit": 10},  # Configure memory log and load limits.
        "tokens": {"max_tokens": 100}  # Configure the maximum number of tokens for AI responses.
    }

# Extract configuration values from the loaded app_config.
LOG_LIMIT = app_config["memory"]["log_limit"]  # Maximum number of messages to store in memory.
LOAD_LIMIT = app_config["memory"]["load_limit"]  # Maximum number of messages to load from memory for context.
MAX_TOKENS = app_config["tokens"]["max_tokens"]  # Maximum number of tokens allowed in the AI response.

# Load Discord secrets from discord.json.  This file contains the bot token and a list of channel IDs.
try:
    with open(DISCORD_SECRETS_PATH, "r") as f:
        discord_secrets = json.load(f)
except Exception as e:
    # If the file fails to load, print an error and exit the program.  The bot requires a valid token to run.
    print(f"❌ Failed to load Discord secrets: {e}")
    sys.exit(1)

# Extract the bot token and channel IDs from the loaded discord_secrets.
TOKEN = discord_secrets.get("DT_01")  # Bot token for authentication.
CHANNEL_IDS = [int(discord_secrets[k]) for k in discord_secrets if k.startswith("DC_ID_")]  # List of channel IDs where the bot should respond.

# Validate the loaded secrets.  The bot requires a valid token and at least one channel ID to run.
if not TOKEN:
    print("❌ Missing DT_01 in discord.json")
    sys.exit(1)
if not CHANNEL_IDS:
    print("❌ No DC_ID_* entries found in discord.json")
    sys.exit(1)

# Load route configuration from route.json.  This file contains the AI endpoint URLs and the model name.
try:
    with open(ROUTE_PATH, "r") as f:
        route_config = json.load(f)
except Exception as e:
    # If the file fails to load, print an error and exit the program. The bot requires a valid route configuration.
    print(f"❌ Failed to load route config: {e}")
    sys.exit(1)

# Extract the AI endpoint URLs and model name from the loaded route_config.
ENDPOINTS = route_config.get("endpoints", [])  # List of AI endpoint URLs.
MODEL = route_config.get("model", "qwen3-v1-4b")  # Name of the AI model.

# Validate the loaded route configuration.  The bot requires at least one endpoint configured.
if not ENDPOINTS:
    print("❌ No endpoints configured in route.json")
    sys.exit(1)

# Load persona configuration from persona.json.  This file defines the AI's personality.
try:
    with open(PERSONA_PATH, "r") as f:
        persona_config = json.load(f)
except Exception as e:
    # If the file fails to load, print a warning and use a built-in default persona.
    print(f"⚠️ Persona config not found or invalid, using built-in default: {e}")
    persona_config = {
        "default": {
            "role": "system",
            "content": "You are ZIA, a friendly indie dev lounge AI. Keep replies short and casual."
        }
    }

# Function to load conversation memory from a file.
def load_memory(channel_id):
    """
    Loads conversation history from a JSON file.

    Args:
        channel_id: The ID of the Discord channel.

    Returns:
        A list of message dictionaries.  Returns an empty list if the file does not exist.
    """
    path = os.path.join(MEMORY_DIR, f"{channel_id}.json")  # Path to the memory file for the channel.
    if not os.path.exists(path):
        return []  # Return an empty list if the file does not exist.
    with open(path, "r") as f:
        history = json.load(f)  # Load the conversation history from the file.
    return history[-LOAD_LIMIT:]  # Return the last LOAD_LIMIT messages.

# Function to save conversation memory to a file.
def save_memory(channel_id, role, content):
    """
    Saves a message to the conversation history file.

    Args:
        channel_id: The ID of the Discord channel.
        role: The role of the message sender ("user" or "assistant").
        content: The content of the message.
    """
    path = os.path.join(MEMORY_DIR, f"{channel_id}.json")  # Path to the memory file for the channel.
    history = []  # Initialize an empty list to store the conversation history.
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)  # Load the existing conversation history.
    history.append({  # Append the new message to the history.
        "role": role,  # The role of the message sender.
        "content": content,  # The content of the message.
        "timestamp": datetime.datetime.now().isoformat()  # The timestamp of the message.
    })
    history = history[-LOG_LIMIT:]  # Keep only the last LOG_LIMIT messages.
    with open(path, "w") as f:
        json.dump(history, f, indent=2)  # Save the updated conversation history to the file.

# Function to get the persona for a specific channel.
def get_persona_for_channel(channel_id: int):
    """
    Gets the persona for a specific channel.

    Args:
        channel_id: The ID of the Discord channel.

    Returns:
        A dictionary containing the persona information.
    """
    persona_name = None
    for key, value in discord_secrets.items():
        if key.startswith("DC_ID_"):
            persona_key = key.replace("DC_ID_", "DC_PERSONA_")  # Construct the key for the persona name.
            persona_name = discord_secrets.get(persona_key, "default")  # Get the persona name from the secrets.
            print(f"Channel {value} → Persona: {persona_name}")  # Print the channel ID and persona name.
            break
    if not persona_name:
        persona_name = "default"  # Use the default persona if no channel-specific persona is found.
    return persona_config.get(persona_name, persona_config["default"])  # Return the persona configuration.

# Function to call the AI endpoint.
def call_ai(message_content, channel_id):
    """
    Calls the AI endpoint to get a response.

    Args:
        message_content: The user's message.
        channel_id: The ID of the Discord channel.

    Returns:
        The AI's response.
    """
    persona = get_persona_for_channel(channel_id)  # Get the persona for the channel.
    memory = load_memory(channel_id)  # Load the conversation memory.
    messages = [persona] + memory + [{"role": "user", "content": message_content}]  # Construct the message list.

    for endpoint in ENDPOINTS:  # Iterate over the list of AI endpoints.
        try:
            # First attempt with model
            payload = {
                "model": MODEL,
                "messages": messages,
                "max_tokens": MAX_TOKENS
            }
            response = requests.post(endpoint, json=payload, timeout=10)

            # Retry without model if failed
            if response.status_code != 200:
                print(f"⚠️ Endpoint {endpoint} returned {response.status_code}, retrying without model...")
                payload.pop("model", None)
                response = requests.post(endpoint, json=payload, timeout=10)

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]

                # Persist the conversation to memory.
                save_memory(channel_id, "user", message_content)
                save_memory(channel_id, "assistant", reply)
                return reply
            else:
                print(f"⚠️ Endpoint {endpoint} still failed with {response.status_code}")
                continue

        except Exception as e:
            print(f"⚠️ Failed on {endpoint}: {e}")
            continue

    return "⚠️ All endpoints failed, please try again later."

# Create a Discord client.
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent.
client = discord.Client(intents=intents)

# Define an event handler for the on_ready event.
@client.event
async def on_ready():
    """
    This function is called when the bot is ready.
    """
    print(f"✅ Logged in as {client.user}")  # Print a message indicating that the bot has logged in.
    print(f"Listening on channels: {CHANNEL_IDS}")  # Print a message indicating the channels the bot is listening on.

# Define an event handler for the on_message event.
@client.event
async def on_message(message):
    """
    This function is called when a message is received.
    """
    if message.author == client.user:  # Ignore messages sent by the bot itself.
        return
    if message.content.strip().startswith("!"):  # Ignore messages that start with an exclamation mark.
        return
    if message.channel.id not in CHANNEL_IDS:  # Ignore messages sent in channels that are not in the list of allowed channels.
        return
    reply = call_ai(message.content, message.channel.id)  # Call the AI endpoint to get a response.
    await message.channel.send(reply)  # Send the AI's response to the channel.

# Run the bot.
if __name__ == "__main__":
    try:
        client.run(TOKEN)  # Run the bot using the Discord token.
    except KeyboardInterrupt:
        print("🛑 Shutting down Discord bot...")  # Print a message indicating that the bot is shutting down.
