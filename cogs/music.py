import discord
from discord.ext import commands
from core.bot import SkyeBot


class Music(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Teest")
        
        

async def setup(bot):
    await bot.add_cog(Music(bot))