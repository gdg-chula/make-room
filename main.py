import discord
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready() -> str:
    print(f"logged in as {client.user}")

@client.event
async def on_message(message) -> None:
    # ignore self message
    if message.author == client.user:
        return
    else:
        print(f"{message.author}: {message.content}")

    if message.content.startswith("hello"):
        await message.channel.send(f"Hello! {message.author}")

client.run(token)
