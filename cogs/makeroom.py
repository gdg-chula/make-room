import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger('MakeRoom')

class MakeRoom(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.category_name = "MakeRoom"

    # This method ensures the "Create Category" button works even after the bot restarts
    async def cog_load(self):
        self.bot.add_view(CreateCategoryView(self))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info(f"Joined a new guild: {guild.name} (ID: {guild.id})")

        join_embed = discord.Embed(
            title="Greeting! 🤩",
            description=(
                "Thanks for adding me! A moderator can use the button below to create my working category."
            ),
            color=discord.Color.orange()
        )
        
        if self.bot.user.avatar:
            join_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        else:
            join_embed.set_author(name=self.bot.user.name)

        view = CreateCategoryView(self)

        mod_channel = discord.utils.get(guild.text_channels, name="moderator-only")
        if mod_channel:
            await mod_channel.send(embed=join_embed, view=view)
        elif guild.system_channel:
            await guild.system_channel.send(embed=join_embed, view=view)
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

        # 1. User joins the "+ Create Room" channel
        if after.channel and after.channel.name == "+ Create Room":
            await self.create_new_room(member, after)
            return # We stop here because the creation logic handles everything else
        
        # 2. User joins an existing custom room (e.g., gets dragged in by an admin)
        if after.channel and after.channel.category and after.channel.category.name == self.category_name:
            # If the room is private, grant them text chat access automatically
            if not after.channel.permissions_for(member.guild.default_role).view_channel:
                await after.channel.set_permissions(member, view_channel=True)

        # 3. User leaves a custom room
        if before.channel and before.channel.category and before.channel.category.name == self.category_name and before.channel.name != "+ Create Room":
            
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                    logger.info(f"{member.guild.name}: Deleted empty room: {before.channel.name}")
                except discord.DiscordException:
                    pass
            else:
                # If the room isn't empty but it IS private, revoke text access for the person who just left
                if not before.channel.permissions_for(member.guild.default_role).view_channel:
                    # We only want to remove their permission if they aren't the room creator
                    # (You can check the channel name to loosely verify, or just let it reset since the creator 
                    # usually leaves last anyway)
                    await before.channel.set_permissions(member, overwrite=None)

    @app_commands.command(name="init_category", description="Create the MakeRoom temporary voice category.")
    @app_commands.checks.has_permissions(administrator=True)
    async def init_category(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=self.category_name)

        if category:
            try:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
            except discord.Forbidden:
                await interaction.followup.send("I do not have permission to delete channels.", ephemeral=True)
                return

        try:
            new_category = await guild.create_category(self.category_name)
            channel = await guild.create_voice_channel("+ Create Room", category=new_category)
            await channel.set_permissions(guild.default_role, view_channel=True, connect=True)
            
            embed = discord.Embed(
                title="Category Ready",
                description=(
                    f"Category '{self.category_name}' is set up.\n"
                    f"Join <#{channel.id}> to create rooms!"
                ),
                color=discord.Color.green()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to create categories or channels.", ephemeral=True)

    async def create_new_room(self, member: discord.Member, after: discord.VoiceState):
        guild = member.guild
        category = after.channel.category
        channel_name = f"🏠 {member.nick if member.nick else member.name}'s Room"

        existing_channel = discord.utils.get(guild.voice_channels, name=channel_name, category=category)
        if existing_channel:
            await member.move_to(existing_channel)
            return

        try:
            new_channel = await guild.create_voice_channel(name=channel_name, category=category)
            await member.move_to(new_channel)
            
            control_embed = discord.Embed(
                title="🪄 Room Control",
                description="Toggle the visibility of this voice channel.",
                color=discord.Color.og_blurple()
            )

            await new_channel.send(embed=control_embed, view=RoomControlView(member.id))
            logger.info(f"Created new room: {channel_name} in {guild.name}")
        except Exception as e:
            logger.error(f"Error creating room: {e}")

class RoomControlView(discord.ui.View):
    def __init__(self, creator_id: int):
        super().__init__(timeout=None)
        self.creator_id = creator_id

    @discord.ui.button(label="Toggle Visibility", style=discord.ButtonStyle.primary, custom_id="toggle_visibility")
    async def toggle_visibility(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel

        warning_embed = discord.Embed(
            title="⚠️ Permission Denied",
            description="You can only manage the room you created.",
            color=discord.Color.red()
        )
        
        private_embed = discord.Embed(
            title="😶‍🌫️ Room Privacy",
            description="This room is now private.",
            color=discord.Color.red()
        )

        public_embed = discord.Embed(
            title="🥳 Room Privacy",
            description="This room is now public.",
            color=discord.Color.green()
        )

        # Check if the person clicking the button is the room creator
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message(
                embed=warning_embed,
                ephemeral=True
            )
            return
        
        if isinstance(channel, discord.VoiceChannel):
            # IF IT IS CURRENTLY PUBLIC -> MAKE IT PRIVATE
            if channel.permissions_for(interaction.guild.default_role).view_channel:
                
                # 1. Deny the @everyone role from seeing the channel
                await channel.set_permissions(interaction.guild.default_role, view_channel=False)
                
                # 2. Grant explicit view access to everyone currently inside the voice channel
                # This prevents the "Message could not be delivered" error!
                for member in channel.members:
                    await channel.set_permissions(member, view_channel=True)
                    
                await interaction.response.send_message(
                    embed=private_embed,
                    view=RoomControlView(self.creator_id),
                    ephemeral=True
                )
                
            # IF IT IS CURRENTLY PRIVATE -> MAKE IT PUBLIC
            else:
                # 1. Allow the @everyone role to see the channel again
                await channel.set_permissions(interaction.guild.default_role, view_channel=True)
                
                # 2. Clean up the explicit member overrides to keep server permissions tidy
                for member in channel.members:
                    # Setting overwrite to None removes the user-specific override
                    await channel.set_permissions(member, overwrite=None)
                    
                await interaction.response.send_message(
                    embed=public_embed,
                    view=RoomControlView(self.creator_id), 
                    ephemeral=True
                )

class CreateCategoryView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="✨ Create Category", style=discord.ButtonStyle.primary, custom_id="create_category_btn")
    async def create_category_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.init_category(interaction)

async def setup(bot: commands.Bot):
    await bot.add_cog(MakeRoom(bot))