import discord
from discord.ext import commands
import datetime as dt



class events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    
    @commands.Cog.listener()
    async def on_command_completion(self,ctx: commands.Context):
        self.bot.c = discord.Color.random()
        command = ctx.command.root_parent   
        if not command:
            command = ctx.command

        try:
            loc = ctx.guild
        except:
            loc = ctx.author
        else:
            loc = ctx.guild

        date = dt.datetime.now()
        waktu = date.strftime("%d/%m/%y %I:%M %p")
        
        try:
            text = f"`{waktu}` | **{ctx.author}** used `{command.name}` command on `#{ctx.channel}`, **{loc}**"
            print(text.replace('*', '').replace('`', ''))
        except:
            text = f"`{waktu}` | **{ctx.author}** used `{command.name}` command on **{loc}**"
            print(text.replace('*', '').replace('`', ''))

        if command.hidden:
            return


    

async def setup(bot):
    await bot.add_cog(events(bot))