import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger('Main')

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class MakeRoomBot(commands.Bot):
    def __init__(self):
        # Enable intents that are necessary for bot's functionality
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True

        self.cogs_to_load = (
            "cogs.events",
            "cogs.makeroom",
            "cogs.honeypot",
        )

        # command_prefix is set to when_mentioned, so the bot responds to mentions
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

    async def setup_hook(self):
        self.tree.on_error = self.on_app_command_error
        
        # Load extensions explicitly
        for extension in self.cogs_to_load:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
        logger.info("All extensions loaded successfully.")

        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s) globally.")
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("⛔ You don't have the required permissions.", ephemeral=True)
        else:
            error_msg = "Oops! Something went wrong while running that command."
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
            logger.error(f"Command Error: {error}")

if __name__ == "__main__":
    bot = MakeRoomBot()
    discord.utils.setup_logging() 
    bot.run(DISCORD_TOKEN, log_handler=None)