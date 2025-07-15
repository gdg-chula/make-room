import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

class Client(commands.Bot):
    def __init__(self: commands.Bot):
        # Load environment variables from .env file
        print("🔍 Loading environment variables...")
        load_dotenv()
        self.token = os.getenv("DISCORD_TOKEN")

        # Ensure the token is available
        if not self.token:
            raise ValueError("No DISCORD_TOKEN found in environment variables.")
        else:
            print("✅ DISCORD_TOKEN loaded successfully")
        
        # Define intents and initialize the parent Bot class
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        # A list of cogs to load at startup
        self.cogs_to_load = [
            'cogs.onboarding',
            'cogs.create_category',
        ]

    async def setup_hook(self: commands.Bot):
        """
        This special method is called once after the bot logs in but before
        it connects to the websocket. It's the ideal place to load extensions.
        """
        print("⏳ Loading cogs...")
        for cog in self.cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        print("😆 All cogs are loaded 😆")


    async def on_ready(self: commands.Bot):
        """
        This event is called when the bot has successfully connected to Discord.
        """
        print(f"🔒 Logged in as {self.user} (ID: {self.user.id})")
        print("🍀 Everything looks good!")

    def run_client(self: commands.Bot):
        """
        Starts the bot client with the loaded token.
        """
        try:
            self.run(self.token)
        except Exception as e:
            print(f"Failed to start bot: {e}")

if __name__ == "__main__":
    client = Client()
    client.run_client()