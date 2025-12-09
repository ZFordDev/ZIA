# bot/slack/zia.py
import os, json, sys, datetime
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Base and root directories for project structure.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of this file.
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # Project root.

# Paths to configuration and secret files. These are used throughout the script.
SLACK_SECRETS_PATH = os.path.join(ROOT_DIR, "secrets", "connects", "slack.json")  # Slack credentials (bot token, signing secret, app token).
ROUTE_PATH = os.path.join(ROOT_DIR, "secrets", "config", "route.json")  # AI endpoint URLs and model.
PERSONA_PATH = os.path.join(ROOT_DIR, "config", "persona.json")  # Persona definitions for the bot.
MEMORY_DIR = os.path.join(ROOT_DIR, "secrets", "db")  # Directory where conversation history will be stored.
APP_PATH = os.path.join(ROOT_DIR, "config", "app.json")  # Application configuration file (memory limits, token limits).

# Create the memory directory if it doesn't exist. This ensures that the bot can store conversation history.
os.makedirs(MEMORY_DIR, exist_ok=True)

# Load app.json limits
try:
    with open(APP_PATH, "r") as f:
        app_config = json.load(f)
except Exception as e:
    # If the file fails to load, print a warning and use default values. This prevents crashes.
    print(f"⚠️ Failed to load app.json, using defaults: {e}")
    app_config = {
        "memory": {"log_limit": 100, "load_limit": 10},
        "tokens": {"max_tokens": 100}
    }

# Extract configuration values from the loaded app_config.
LOG_LIMIT = app_config["memory"]["log_limit"]  # Maximum number of messages to keep in memory per channel.
LOAD_LIMIT = app_config["memory"]["load_limit"]  # Number of recent messages to load for context.
MAX_TOKENS = app_config["tokens"]["max_tokens"]  # Maximum tokens allowed in AI responses.

# Load Slack secrets
try:
    with open(SLACK_SECRETS_PATH, "r") as f:
        slack_secrets = json.load(f)
except Exception as e:
    print(f"❌ Failed to load Slack secrets: {e}")
    sys.exit(1)

SLACK_BOT_TOKEN = slack_secrets.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = slack_secrets.get("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = slack_secrets.get("SLACK_APP_TOKEN")

# Validate the loaded tokens. The bot requires all three to function.
if not SLACK_BOT_TOKEN or not SLACK_SIGNING_SECRET or not SLACK_APP_TOKEN:
    print("❌ Missing Slack tokens or signing secret in slack.json")
    sys.exit(1)

# Initialize the Slack app using Bolt. It will handle events and commands.
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# Load route config
try:
    with open(ROUTE_PATH, "r") as f:
        route_config = json.load(f)
except Exception as e:
    print(f"❌ Failed to load route config: {e}")
    sys.exit(1)

ENDPOINTS = route_config.get("endpoints", [])  # List of AI endpoint URLs.
MODEL = route_config.get("model", "qwen3-v1-4b")  # Name of the AI model.

# Validate that at least one endpoint is configured.
if not ENDPOINTS:
    print("❌ No endpoints configured in route.json")
    sys.exit(1)

# Load personas
try:
    with open(PERSONA_PATH, "r") as f:
        persona_config = json.load(f)
except Exception as e:
    # If the file fails to load, use a built‑in default persona.
    print(f"⚠️ Persona config not found or invalid, using built-in default: {e}")
    persona_config = {
        "default": {
            "role": "system",
            "content": "You are ZIA, a friendly indie dev lounge AI. Keep replies short and casual."
        }
    }

def load_memory(channel_id):
    # Build path to memory file for this channel.
    path = os.path.join(MEMORY_DIR, f"{channel_id}.json")
    if not os.path.exists(path):
        return []  # Return an empty list if the file does not exist.
    with open(path, "r") as f:
        history = json.load(f)
    return history[-LOAD_LIMIT:]  # Return the last LOAD_LIMIT messages.

def save_memory(channel_id, role, content):
    # Build path to memory file for this channel.
    path = os.path.join(MEMORY_DIR, f"{channel_id}.json")
    history = []
    if os.path.exists(path):
        with open(path, "r") as f:
            history = json.load(f)
    # Append the new message to the history.
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat()
    })
    # Keep only the last LOG_LIMIT messages.
    history = history[-LOG_LIMIT:]
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def get_persona_for_channel(channel_id: str):
    # Channel‑specific personas are defined in slack.json with keys like SLACK_PERSONA_<channel>.
    persona_name = slack_secrets.get(f"SLACK_PERSONA_{channel_id}", "default")
    return persona_config.get(persona_name, persona_config["default"])

def call_ai(message_content, channel_id):
    # Retrieve the persona for this channel.
    persona = get_persona_for_channel(channel_id)
    # Load conversation history from memory.
    memory = load_memory(channel_id)
    # Construct the message list to send to the AI endpoint.
    messages = [persona] + memory + [{"role": "user", "content": message_content}]

    for endpoint in ENDPOINTS:
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

# Slack message handler
@app.message(".*")
def handle_message(message, say):
    # Handle any incoming text message in channels the bot is present in.
    channel_id = message["channel"]
    user_message = message.get("text", "")

    reply = call_ai(user_message, channel_id)
    say(reply)

if __name__ == "__main__":
    # Start the Slack bot using Socket Mode. This allows it to run without exposing a public HTTP endpoint.
    print("✅ Slack bot is running in Socket Mode...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
