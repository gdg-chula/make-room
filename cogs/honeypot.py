import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger('HoneyPot')

class HoneypotCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.honeypot_channel_name = "dusty-locker"

    async def setup_honeypot_channel(self, guild: discord.Guild, existing_channel: discord.TextChannel = None) -> discord.TextChannel:
        """Helper function to create or recreate the honeypot channel."""
        # Save the category and position so the new channel stays in the same place
        category = existing_channel.category if existing_channel else None
        position = existing_channel.position if existing_channel else None

        if existing_channel:
            await existing_channel.delete(reason="Re-initializing honeypot (ID refresh)")
        
        honeypot_channel = await guild.create_text_channel(
            self.honeypot_channel_name,
            category=category,
            position=position
        )
        await honeypot_channel.set_permissions(guild.default_role, send_messages=True)

        honeypot_embed = discord.Embed(
            title="What is this place? This locker is so dusty... 😶‍🌫️",
            description=(
                f"There's a pile of dangerous dust inside, and it's best to leave it alone!\n "
                f"Better not to touch this locker or {self.bot.user.name} will be very upset! 😠\n\n"
                f"Sending a message here will trigger an automatic ban. 🚫"
            ),
        )
        honeypot_embed.set_footer(text=f"with love ^ ^\n{self.bot.user.name}✨")

        await honeypot_channel.send(embed=honeypot_embed)
        return honeypot_channel

    async def refresh_honeypots(self, guild: discord.Guild = None):
        """Refresh honeypot after ban to refresh channel IDs."""
        await self.bot.wait_until_ready()
        
        existing_channel = discord.utils.get(guild.text_channels, name=self.honeypot_channel_name)

        if existing_channel:
            try:
                new_channel = await self.setup_honeypot_channel(guild, existing_channel)
                logger.info(
                    f"Successfully refreshed honeypot in guild: {guild.name} "
                    f"({existing_channel.id} -> {new_channel.id})"
                )
            except Exception as e:
                logger.error(f"Failed to refresh honeypot in {guild.name}: {e}")

    @app_commands.command(name="init_honeypot", description="Initialize the honeypot channel with a warning message.")
    @app_commands.checks.has_permissions(administrator=True) 
    async def init_honeypot(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        try:
            existing_channel = discord.utils.get(guild.text_channels, name=self.honeypot_channel_name)
            honeypot_channel = await self.setup_honeypot_channel(guild, existing_channel)
            
            await interaction.followup.send(f"✅ Honeypot ready in {honeypot_channel.mention}.", ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ Missing `Manage Channels` or `Send Messages` permissions.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.channel.name != self.honeypot_channel_name:
            return

        mod_channel = discord.utils.get(message.guild.text_channels, name="moderator-only")
        is_admin = getattr(message.author, 'guild_permissions', None) and message.author.guild_permissions.administrator

        if is_admin:
            if mod_channel:
                embed = discord.Embed(
                    title="⚠️ Honeypot Triggered - Admin",
                    description="A user with administrator permissions triggered the honeypot, but was not banned.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="User", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
                embed.set_footer(text="No action taken - user is a moderator.")

                if message.author.avatar:
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                else:
                    embed.set_author(name=message.author.name)

                await mod_channel.send(embed=embed)
                
            await message.channel.send("Moderators are not affected by the honeypot.", delete_after=5)
            try:
                await message.delete(delay=5)
            except discord.HTTPException:
                pass
            return

        try:
            await message.author.ban(reason="Honeypot triggered", delete_message_seconds=600)
            logger.info(f"User {message.author} banned via honeypot on {message.guild.name}.")
            
            if mod_channel:
                embed = discord.Embed(
                    title="🚨 Honeypot Activated",
                    description="A user has been automatically banned.",
                    color=discord.Color.brand_red()
                )
                embed.add_field(name="User", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
                embed.add_field(name="Reason", value="Posted a message in the `#dusty-locker` honeypot channel.", inline=False)

                if message.author.avatar:
                    embed.set_author(name=message.author.name, icon_url=message.author.avatar.url)
                else:
                    embed.set_author(name=message.author.name)
                    
                await mod_channel.send(embed=embed)
                await self.refresh_honeypots(message.guild)  # Refresh honeypot after ban to refresh channel IDs

        except Exception as e:
            logger.error(f"Failed to ban user {message.author}: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(HoneypotCog(bot))