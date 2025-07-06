import discord
from discord.ext import commands


class Onboarding(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._send_setup_message(guild)

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def manual_setup(self, ctx: commands.Context):
        await self._send_setup_message(ctx.guild)

    async def _send_setup_message(self, guild: discord.Guild):
        print(f"Attempting to run setup for server: {guild.name}")
        
        # The embed to be sent
        join_embed = discord.Embed(
            title="🥳 Greeting!",
            description=(
                "Thanks for adding me to your server! I'm here to help you manage things.\n\n"
                "To get started, a moderator can use the `button` below "
                "to create a deficate category for me to work in."
            ),
            color=discord.Color.orange() # Use discord's built-in colors
        )
        join_embed.set_footer(text="Let's get this server organized!")
        join_embed.set_author(name="MakeRoom")

        target_channel = None

        # find the best channel to post in
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            target_channel = guild.system_channel
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break

        # Send the message if a channel was found
        if target_channel:
            try:
                await target_channel.send(embed=join_embed)
                print(f"Sent setup message to #{target_channel.name} in {guild.name}")
            except discord.Forbidden:
                print(f"Could not send message to #{target_channel.name} in {guild.name}: Missing Permissions")
        else:
            print(f"Could not find a suitable channel in {guild.name} to send setup message.")

async def setup(bot):
    await bot.add_cog(Onboarding(bot))
    print("✅ Omboarding cog setup complete")
