import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
