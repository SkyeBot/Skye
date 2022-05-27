import discord
from discord.ext import commands

from core.bot import SkyeBot
from discord import app_commands

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

        await self.bot.pool.execute('UPDATE prefix SET prefix = $1 WHERE guild_id = $2', (prefix, ctx.guild.id))

        embed = discord.Embed(description=f"<a:BosnianWarcrimes:880998885844213790> Succesfully updated this servers prefix to ``{prefix}``", color=0x4365ab)

        await ctx.send(embed=embed)

    @app_commands.command()
    async def test(self, interaction: discord.Interaction):
        await self.bot.db.execute("UPDATE prefix SET prefix = NULL, guild_id = NULL where guild_id= $1", interaction.guild.id)


async def setup(bot: SkyeBot):
    await bot.add_cog(Admin(bot))