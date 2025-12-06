import discord
import os
from dotenv import load_dotenv
from gateway.gateway import chat_with_model
from memory.memory import init_db, add_message, get_history

# Load secrets
load_dotenv("secrets/.env")
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize the database once at startup
init_db()

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID or message.author == client.user:
        return

    channel = str(message.channel.id)

    # Log user message into SQLite
    add_message("discord", channel, "user", str(message.author), message.content)

    # Retrieve history for this channel (system prompt + last N turns)
    history = get_history("discord", channel)

    # Call gateway with full history
    reply = chat_with_model(history, persona="default")

    # Log bot reply into SQLite
    add_message("discord", channel, "assistant", "ZIA", reply)

    await message.channel.send(reply)

client.run(TOKEN)