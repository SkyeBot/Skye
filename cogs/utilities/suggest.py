import discord
from discord.ext import commands


from discord import app_commands

from core.bot import SkyeBot

class SuggestModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Suggest A Feature")

    feature = discord.ui.TextInput(label="Suggest the feature here", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        guild = interaction.client.get_guild(980538933370830848)
        channel = guild.get_channel(985734583733612575)
        
        embed = discord.Embed(description=f"New Feature Suggested!\nSuggested By {interaction.user}")
        embed.add_field(name="Feature", value=self.feature.value)
        await channel.send("<@894794517079793704> New Feature Was Suggested",embed=embed)


        await interaction.response.send_message(f"Thank you for suggesting a feature {interaction.user.mention}!",ephemeral=True, allowed_mentions=discord.AllowedMentions(users=False))



class Suggest(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @app_commands.command()
    async def suggest(self, interaction: discord.Interaction):
        """Allows a user to suggest a feature"""
        await interaction.response.send_modal(SuggestModal())
