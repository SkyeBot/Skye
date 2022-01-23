import discord

import random

from io import BytesIO
from discord.ext import commands
from utils import http, default

import asyncio
import aiohttp

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
        embed.add_field(name="**Website**:", value="\n*Tip: you can find more info at our [Command List](https://hacked-my.email/commands)*")
        embed.add_field(name="**<:malding:929627018474176542> __Skye__**", value="``work``, ``mood``, ``invite``, ``website``", inline=False)
        embed.add_field(name="**<:admin:933871693687062588> __Administrator__**", value="``setprefix``")
        embed.add_field(name="**:tools: __Moderation__**", value="``Ban``, ``Unban``, ``Purge``, ``Mute``, ``Unmute``, ``kick``, ``warn``", inline=False)
        embed.add_field(name="**🎵__Music__**", value="``join``, ``playfile``,``play``, ``yt``, ``stop``", inline=False)
        embed.add_field(name="**:video_game: __Fun__**", value="``duck``, ``nick``, ``howgay``, ``howsus``, ``facts``, ``memes``, ``osugame``, ``8ball``, ``banf``, ``snipe``, ``mood``. ``kys``, ``urban``, ``beer``🍻")
        embed.add_field(name="**📦 __Misc__**", value="``covid``, ``uptime``, ``ping``", inline=False)
   
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
            await ctx.send("Come back hourly to see skyes mood!")
        
    async def randomimageapi(self, ctx, url: str, endpoint: str, token: str = None):
        try:
            r = await http.get(
                url, res_method="json", no_cache=True,
                headers={"Authorization": token} if token else None
            )
        except aiohttp.ClientConnectorError:
            return await ctx.send("The API seems to be down...")
        except aiohttp.ContentTypeError:
            return await ctx.send("The API returned an error or didn't return JSON...")

        await ctx.send(r[endpoint])

    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None):
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req)
            bio.seek(0)
            await ctx.send(content=content, file=discord.File(bio, filename=filename))

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title="You Can Find Skye's current invite here", description=f"[**oauth link**](https://discord.com/api/oauth2/authorize?client_id=932462085516968027&permissions=1375936309318&scope=bot)")
        await ctx.send(embed=embed)

    @commands.command()
    async def website(self, ctx):
        embed = discord.Embed(title=f"You can find the website for skye here:", description=f"[**Website**](https://hacked-my.email)")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(stupidshit(bot))            