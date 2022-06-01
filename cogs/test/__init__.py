import discord
from discord.ext import commands
from discord import app_commands
import googletrans

class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.trans = googletrans.Translator()
        self.ban_menu = app_commands.ContextMenu(
            name='ban',
            callback=self.ban,
            # guild_ids=[...],
        )
        self.translate_menu = app_commands.ContextMenu(
            name="Translate",
            callback=self.translate
        )
        self.bot.tree.add_command(self.ban_menu)
        self.bot.tree.add_command(self.translate_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    # You can add checks too
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self,interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(f'Should I actually ban {user}...', ephemeral=True)
        
    async def translate(self, interaction: discord.Interaction, message: discord.Message):

        loop = self.bot.loop

        
        ret = await loop.run_in_executor(None, self.trans.translate, message.content)

    
        og_lang = googletrans.LANGUAGES.get(ret.src, '(auto-detected)').title()
        translated = googletrans.LANGUAGES.get(ret.dest, 'Unknown').title()
        embed = discord.Embed(title=f'Translated {og_lang} To {translated}', colour=self.bot.color)
        embed.add_field(name=f'Original Language: {og_lang}', value=ret.origin, inline=False)
        embed.add_field(name=f'Translated: {translated}', value=ret.text, inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(MyCog(bot))