import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(guild):
        bot_joined_message = (
            f"🥳 Hello, {guild.name}! Thanks for adding me. I'm here to help.\n"
            "You can start by typing `hello` in any channel."
        )

        # Find a suitable channel to send the welcome message
        target_channel = None

        # 1. Try to find the system channel
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            target_channel = guild.system_channel
        # 2. If no system channel, find the first text channel the bot can write to
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break  # Found a channel, stop looking

        # 3. Send the message if a channel was found
        if target_channel:
            try:
                await target_channel.send(bot_joined_message)
                print(
                    f"Sent welcome message to #{target_channel.name} in {guild.name}")
            except discord.Forbidden:
                print(
                    f"Could not send message to #{target_channel.name} in {guild.name}: Missing Permissions")
        else:
            print(
                f"Could not find a suitable channel in {guild.name} to send welcome message.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        else:
            print(f"{message.author}: {message.content}")

        if message.content.startswith("hello"):
            await message.channel.send(f"Hello! {message.author}")


async def setup(bot):
    await bot.add_cog(General(bot))
    print("✅ General cog setup complete")
