import discord
from discord.ext import commands

class Onboarding(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._send_setup_message(guild)

    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def manual_setup(self, ctx: commands.Context):
        await self._send_setup_message(ctx.guild)

    async def _send_setup_message(self, guild: discord.Guild):
        print(f"Attempting to run setup for server: {guild.name}")
        
        # on guild join embed
        join_embed = discord.Embed(
            title="🥳 Greeting!",
            description=(
                "Thanks for adding me to your server! I'm here to help you manage things.\n\n"
                "To get started, a moderator can use the `button` below "
                "to create a deficate category for me to work in."
            ),
            color=discord.Color.orange()
        )
        join_embed.set_footer(text="Let's get this server organized!")
        join_embed.set_author(name="MakeRoom")

        # Define a button
        create_category_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="✨ Create Category",
            custom_id="create_category"
        )

        async def create_category_callback(interaction: discord.Interaction):
            # Check if the user has administrator permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You must be an administrator to perform this action.", ephemeral=True)
                return

            # Acknowledge the interaction
            await interaction.response.defer()

            # Simulate calling the create-main-category command
            ctx = await self.client.get_context(interaction.message)
            ctx.author = interaction.user
            ctx.guild = interaction.guild
            
            try:
                command = self.client.get_command('create-category')
                if command:
                    await ctx.invoke(command)
                else:
                    await interaction.followup.send("The `create-category` command was not found.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

        create_category_button.callback = create_category_callback

        # Create a view and add the button to it
        view = discord.ui.View()
        view.add_item(create_category_button)

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
                await target_channel.send(embed=join_embed, view=view)
                print(f"Sent setup message to #{target_channel.name} in {guild.name} (system_channel: {target_channel == guild.system_channel})")
            except discord.Forbidden:
                print(f"Could not send message to #{target_channel.name} in {guild.name}: Missing Permissions")
        else:
            print(f"Could not find a suitable channel in {guild.name} to send setup message.")

async def setup(client: commands.Bot):
    await client.add_cog(Onboarding(client))
    print("✅ Onboarding cog setup complete")