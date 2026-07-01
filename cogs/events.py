import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger('MakeRoomBot')

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Logged in as {self.bot.user.name} (ID: {self.bot.user.id})")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # Text Triggers
        if message.content == str(self.bot.user.name):
            await message.channel.send("は~い!", ephemeral=True)

        if message.content.startswith("何が好き"):
            await message.channel.send("ウォッカ&ビール よりも あ・な・た・♡", ephemeral=True)

    @app_commands.command(name="debug", description="Get info about your current voice channel.")
    @app_commands.checks.has_permissions(administrator=True) 
    async def debug(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You are not connected to a voice channel!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        await interaction.response.send_message(f"🎙️ **Voice channel:** {channel.name} \n🆔 **ID:** `{channel.id}`", ephemeral=True)
        logger.info(f"{interaction.user} requested debug info for channel: {channel.name}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))