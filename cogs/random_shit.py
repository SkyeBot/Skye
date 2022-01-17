import discord

import random


from discord.ext import commands

class stupidshit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "borger":
            await message.channel.send("BORGEER!!!\nhttps://tenor.com/view/hotdog-hotdowg-heart-heart-locket-valentines-gif-20422380")
    
    @commands.command()
    async def work(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/921957596259291166/932458342058704896/ECC6AF8F-F42E-4945-A0F2-F79E7BAB6DBF.jpg")  

    
    @commands.command()
    async def help(self,ctx):
        embed=discord.Embed(title="💡List Of Commands")
        embed.add_field(name="**__stupid shit__**", value="``work``")

   
        await ctx.send(embed=embed)

    
    @commands.command()
    async def help(self,ctx):
        embed=discord.Embed(title="💡List Of Commands")
        embed.add_field(name="**<:malding:929627018474176542> __Skye__**", value="``work``, ``mood``", inline=False)
        embed.add_field(name="**:tools: __Moderation__**", value="``Ban``, ``Unban``, ``Purge``, ``Mute``, ``Unmute``, ``kick``", inline=False)
   
        await ctx.send(embed=embed) 

    @commands.command()
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)
    async def mood(self, ctx):
        choices = ["racist", "anger", "happy", "sad"]
        choice_to_pick = random.choice(choices)

        if choice_to_pick == "anger":
            embed = discord.Embed(title="My current mood Is", description=f"{choice_to_pick} <:malding:929627018474176542>")
            await ctx.send(embed=embed)
        
        if choice_to_pick == "sad":
            embed = discord.Embed(title="My current mood Is", description=f"{choice_to_pick} <:com:932492768280973312>")
            await ctx.send(embed=embed)

        if choice_to_pick == "racist":
            embed = discord.Embed(title="My current mood Is", description=f"{choice_to_pick} <a:saladfunny:922955050450554880>")
            await ctx.send(embed=embed)

        if choice_to_pick == "happy":
            embed = discord.Embed(title="My current mood Is", description=f"{choice_to_pick} <:dumb:905151933185134713>")
            await ctx.send(embed=embed)


    @mood.error
    async def urban_error(self,ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("bro let my qt have a change of mood, come back hourly to see her mood :)")
        



def setup(bot):
    bot.add_cog(stupidshit(bot))            
