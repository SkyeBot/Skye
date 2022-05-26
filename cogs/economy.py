import discord
import random
from discord.ext import commands 



class Economy(commands.Cog):
    """Economy commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(aliases=["bal"])
    async def balance(self, ctx: commands.Context):
        try:
            bank = await self.bot.db.fetchrow("SELECT money FROM ECONOMY WHERE userid = $1", ctx.author.id)
            if (bank == None):
                await self.bot.db.execute('INSERT INTO economy(money, userid) VALUES ($1, $2)',1, ctx.author.id)
                print(bank)
                money = 1
                em = discord.Embed(title=f"You currently have {money} dollar in your bank!", color=discord.Color(0x32ff00))
                em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=em)
            else:
                money = bank.get("money")
                if money == 1:
                    em = discord.Embed(title=f"You currently have {money} dollar in your bank!", color=discord.Color(0x32ff00))
                    em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=em)
                else:
                    em = discord.Embed(title=f"You currently have {money} dollars in your bank!", color=discord.Color(0x32ff00))
                    em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                    await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)


    @commands.command()
    async def beg(self, ctx: commands.Context):
        try:
            bank = await self.bot.db.fetchrow("SELECT money FROM ECONOMY WHERE userid = $1", ctx.author.id)

            if (bank == None):
                await self.bot.db.execute('INSERT INTO economy(money, userid) VALUES ($1, $2)',1, ctx.author.id)
                new_bank = await self.bot.db.fetchrow("SELECT money FROM ECONOMY WHERE userid = $1", ctx.author.id)
                earnings = random.randrange(101)
                print(bank)
                money = new_bank.get("money")
                new_bal = money + earnings
                await self.bot.db.execute('UPDATE ECONOMY SET money = $1 WHERE userid = $2', new_bal, ctx.author.id)
                em = discord.Embed(title=f"Someone gave you {earnings} coins", description=f"You now have {new_bal} on your bank!",color=discord.Color(0x32ff00))
                em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=em)
            else:
                earnings = random.randrange(101)
                print(bank)
                money = bank.get("money")
                new_bal = money + earnings
                await self.bot.db.execute('UPDATE ECONOMY SET money = $1 WHERE userid = $2', new_bal, ctx.author.id)

                em = discord.Embed(title=f"Someone gave you {earnings} coins",description=f"You now have {new_bal} on your bank!",color=discord.Color(0x32ff00))
                em.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
                await ctx.send(embed=em)
        except (Exception) as e:
            await ctx.send(e)


                


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))