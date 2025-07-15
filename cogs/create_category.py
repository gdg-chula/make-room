import discord
from discord.ext import commands

class createCategory(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def _create_category(self, guild: discord.Guild, category_name: str) -> tuple[discord.CategoryChannel, str]:
        """Creates a new category in the server."""
        try:
            category = await guild.create_category(category_name)
            return category, f"Category '{category.name}' created!"
        except discord.Forbidden:
            return None, "No permission to create categories."
        except Exception as e:
            return None, f"Error creating category: {e}"

    async def _delete_category(self, ctx: commands.Context, category: discord.CategoryChannel, category_name: str):
         """Deletes an existing category and its contents, then recreates it."""
         if category:
            # Delete all channels in the category
            for channel in category.channels:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    print(f"No permission to delete channel '{channel.name}'.")
                except Exception as e:
                    print(f"Error deleting channel '{channel.name}': {e}")

            # Delete the category itself
            try:
                await category.delete()
                print(f"Category '{category_name}' and contents deleted. Recreating...")
            except discord.Forbidden:
                print(f"No permission to delete category '{category_name}'.")
            except Exception as e:
                print(f"Error deleting category: {e}")

    @commands.command(name="create-category")
    @commands.has_permissions(administrator=True)
    async def create_category(self, ctx: commands.Context, category_name: str = "Individual Channels"):
        """Creates a new category in the server. If it exists, deletes it and its contents, then recreates it."""
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name=category_name)

        recreate = bool(category)
        if recreate:
            await self._delete_category(ctx, category, category_name)

        category, status = await self._create_category(guild, category_name)
        print(status)

        # Create a voice channel called "+ Create Room" under the new category
        try:
            voice_channel = await guild.create_voice_channel("+ Create Room", category=category)
            print(f"Voice channel '{voice_channel.name}' created under '{category.name}'.")
        except discord.Forbidden:
            print("No permission to create voice channels.")
        except Exception as e:
            print(f"Error creating voice channel: {e}")

        embed_color = discord.Color.blue() if recreate else discord.Color.green()
        embed_title = "Category Recreated" if recreate else "Category Created"
        embed_description = f"Category '{category_name}' created successfully."

        embed = discord.Embed(title=embed_title, description=embed_description, color=embed_color)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(createCategory(client))
    print("✅ createCategory cog setup complete")