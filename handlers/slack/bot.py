from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from gateway.gateway import chat_with_model
from memory.memory import init_db, add_message, get_history

app = Flask(__name__)

# Load secrets
load_dotenv("secrets/.env")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
BOT_USER_ID = os.getenv("BOT_USER_ID")

# Initialize the database once at startup
init_db()

# Simple in-memory store for processed events to avoid double replies
processed_events = set()

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    
    # Slack URL verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    if "event" in data:
        event = data["event"]
        event_id = data.get("event_id")
        
        # Skip duplicates
        if event_id in processed_events:
            return jsonify({"status": "duplicate skipped"})
        processed_events.add(event_id)
        
        # Ignore bot’s own messages
        if event.get("user") == BOT_USER_ID:
            return jsonify({"status": "ignored self message"})
        
        # Handle user messages
        if event.get("type") == "message" and "bot_id" not in event:
            user_text = event.get("text")
            channel = event.get("channel")

            # Log user message into SQLite
            add_message("slack", channel, "user", event.get("user"), user_text)

            # Retrieve history for this channel
            history = get_history("slack", channel)

            # Call gateway with full history
            reply = chat_with_model(history, persona="balanced")

            # Log bot reply into SQLite
            add_message("slack", channel, "assistant", "ZIA", reply)

            # Send reply back to Slack
            resp = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
                json={"channel": channel, "text": reply}
            )
            print(resp.json())
    
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)