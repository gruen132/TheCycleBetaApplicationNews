import discord
import requests
from flask import Flask
from threading import Thread
import os

# --- CONFIGURATION ---
TOKEN = 'MTQ2NzY3ODkxODMxOTI4MDIzMA.GmChn1.m1RgkjspkRmLlCfUsUl46mHiTQccwTBY_1x6og'
FEED_CHANNEL_ID = 1467674576212463689  # Replace with your channel ID (integer, no quotes)
NTFY_TOPIC = 'cyclenews'  # Replace with your ntfy topic
# ---------------------

# 1. THE WEB SERVER (Keeps the bot alive)
app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run_http():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_http)
    t.start()


# 2. THE DISCORD BOT
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    # Only listen to the specific feed channel
    if message.channel.id == FEED_CHANNEL_ID:

        # Check if it's a "crosspost" (followed message) or a webhook
        if message.flags.crossposted or message.webhook_id:

            # Prepare the notification content
            msg_content = message.content
            if not msg_content and message.embeds:
                msg_content = "[Image/Embed Content]"
            elif not msg_content and message.attachments:
                msg_content = "[File Attached]"

            print(f"Forwarding message: {msg_content}")

            # Send to ntfy.sh
            try:
                requests.post(
                    f"https://ntfy.sh/{NTFY_TOPIC}",
                    data=msg_content.encode(encoding='utf-8'),
                    headers={
                        "Title": f"New Message from {message.author.name}",
                        "Priority": "high"
                    }
                )
            except Exception as e:
                print(f"Failed to send notification: {e}")


# 3. START EVERYTHING
keep_alive()
client.run(TOKEN)