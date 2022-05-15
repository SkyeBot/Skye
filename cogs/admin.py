import discord

from discord.ext import commands

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx):
        prefix = await self.bot.db.fetchrow("SELECT prefix FROM PREFIX WHERE guild_id = $1", ctx.guild.id)

        a = prefix.get("prefix")

        embed = discord.Embed(description=f"<a:tcd_wiggle:908558672475586580> This servers prefix is ``{a}``", color=0x4365ab)

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix=None):
        if new_prefix is None:
            return ctx.send("Please pick out a prefix!")  
        else:
            await self.bot.db.execute('UPDATE prefix SET prefix = $1 WHERE guild_id = $2', new_prefix, ctx.guild.id)

            embed = discord.Embed(description=f"<a:BosnianWarcrimes:880998885844213790> Succesfully updated this servers prefix to ``{new_prefix}``", color=0x4365ab)

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(admin(bot))