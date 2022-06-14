import discord
from discord.ext import commands

from core.bot import SkyeBot
from discord import app_commands

from utils.context import Context

class Admin(commands.Cog):
    
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx: commands.Context):
        prefix = await self.bot.pool.fetchval("SELECT prefix FROM PREFIX WHERE guild_id = $1", (ctx.guild.id))

        embed = discord.Embed(description=f"The prefix for this guild is ``{prefix}``!")

        await ctx.send(embed=embed)

    @commands.command()
    async def setprefix(self, ctx: commands.Context, *, prefix: str):
        if prefix is None:
            await ctx.send("Please insert an prefix!")

        await self.bot.pool.execute('UPDATE prefix SET prefix = $1 WHERE guild_id = $2', prefix, ctx.guild.id)

        embed = discord.Embed(description=f"<a:BosnianWarcrimes:880998885844213790> Succesfully updated this servers prefix to ``{prefix}``", color=0x4365ab)

        await ctx.send(embed=embed)

    @commands.command()
    async def hi(self, ctx: Context):
        async for entry in ctx.guild.audit_logs(limit=100):
            await ctx.send(f'{entry.user} did {entry.action} to {entry.target}')
