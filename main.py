import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    await load_cogs()
    print("🤯 All cogs are loaded 🤯")


async def load_cogs():
    """Load all cog extensions"""
    cogs_to_load = [
        'cogs.onboarding'
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

if __name__ == "__main__":
    try:
        bot.run(token)
    except Exception as e:
        print(f"Failed to start bot: {e}")
