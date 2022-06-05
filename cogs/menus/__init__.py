import calendar
import discord
from discord.ext import commands
from discord import app_commands
import googletrans
import datetime

class ban_modal(discord.ui.Modal):
    def __init__(self, member):
        self.member: discord.Member = member
        super().__init__(title='Ban Modal')

    reason = discord.ui.TextInput(label="Reason", placeholder="Whats the reason you're banning this user")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.guild.ban(self.member)
        
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        
        embed = discord.Embed(
            title=f"*{self.member} was banned!*", description=f"**Reason: {self.reason} \n Member banned at <t:{utc_time}:F>**",
            color = 0x3867a8,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=self.member, icon_url=self.member.display_avatar.url)
        await interaction.response.send_message(embed=embed)




class context_menus(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.trans = googletrans.Translator()
        self.ctx_menu = app_commands.ContextMenu(
            name='ban',
            callback=self.ban,
            # guild_ids=[...],
        )
        self.ctx_menu2 = app_commands.ContextMenu(
            name="Translate",
            callback=self.translate
        )
        self.bot.tree.add_command(self.ctx_menu)
        self.bot.tree.add_command(self.ctx_menu2)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        self.bot.tree.remove_command(self.ctx_menu2.name, type=self.ctx_menu2.type)

    # You can add checks too
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self,interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_modal(ban_modal(member))
        
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
    await bot.add_cog(context_menus(bot))