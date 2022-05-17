import datetime
import io
import discord
from discord import app_commands
import random

from io import BytesIO
from discord.ext import commands
from utils import http, default

import asyncio
import aiohttp

from discord.ext import commands

class Random_Stuff(commands.Cog):
    """All Fun commands"""
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

    async def api_img_creator(self, ctx, url: str, filename: str, content: str = None, link: str = None):
        async with ctx.channel.typing():
            req = await http.get(url, res_method="read")

            if not req:
                return await ctx.send("I couldn't create the image ;-;")

            bio = BytesIO(req)
            bio.seek(0)
            await ctx.send(content=content, file=discord.File(bio, filename=filename))

    
    @app_commands.command()
    async def duck(self, interaction: discord.Interaction):
        """ Posts a random duck """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random-d.uk/api/v1/random") as request:
                if request.status != 200:
                    return await interaction.response.send_message(f"Oh no! The api returned an error of {request.status}!")

                data = await request.json()
                duck_img = data["url"]

                embed = discord.Embed(title="quack quack (translation: here's duck)")
                embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
                embed.set_image(url=duck_img)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text=f"Powered by random-d.uk!", icon_url="https://cdn.discordapp.com/attachments/945457044922728452/947288533582880848/favicon.png")

                await interaction.response.send_message(embed=embed)


    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def birb(self, ctx):
        """ Posts a random duck """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/img/birb") as request:
                if request.status != 200:
                    return await ctx.send("Error")


                data = await request.json()
                gif = data["link"]

                embed = discord.Embed(title=f"Here's your free birb image:)")
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                embed.set_image(url=gif)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
                
                await ctx.send(embed=embed)


    @commands.command()
    async def horny(self,ctx, member: discord.Member = None):
        '''Horny license just for u'''
        member = member or ctx.author
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as session:
            async with session.get(
            f'https://some-random-api.ml/canvas/horny?avatar={member.avatar.url}'
            ) as af:
                if 300 > af.status == 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "horny.png")
                    em = discord.Embed(
                        title="<:BONK:941696818209775667> **BONK** bad horny >:(",
                        color=0xf1f1f1,
                    )
                    em.set_image(url="attachment://horny.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()


    @commands.command()
    async def triggered(self,ctx, member: discord.Member=None):
        member = member or ctx.author
        
        async with aiohttp.ClientSession() as trigSession:
            async with trigSession.get(f'https://some-random-api.ml/canvas/triggered?avatar={member.avatar.url}?size=1024') as trigImg: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await trigImg.read()) # read the image/bytes
                file = discord.File(imageData, "triggered.gif")
            
                em = discord.Embed(
                        title="L + ratio + triggered"
                    )
                em.set_image(url="attachment://triggered.gif")
                await ctx.send(embed=em, file=file)
            
                await trigSession.close() # closing the session and;


    @commands.command()
    async def simp(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://some-random-api.ml/canvas/simpcard?avatar={member.avatar.url}') as simpcard:

                imageData = io.BytesIO(await simpcard.read())
                file = discord.File(imageData, 'Simp.png')

                em = discord.Embed(
                        title="<:jinkies:941703480727465984> bro's a simp!!!!!"
                    )
                em.set_image(url="attachment://Simp.png")
                await ctx.send(embed=em, file=file)
            
                await session.close() # closing the session and;


    @commands.command()
    async def mc(self, ctx, *, username = None):
        if username == None:
            return await ctx.send("Please give a username!")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/mc?username={username}") as mc_username:
                res = await mc_username.json()

                await ctx.send(f'Oldest username: {res["name_history"][0]["name"]} \nDate of username change/creation: {res["name_history"][0]["changedToAt"]} \n\nCurrent Username: {res["username"]}\n\nUUID: {res["uuid"]}')

    @commands.command()
    async def token(self, ctx, channel: discord.TextChannel):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/bottoken") as token:
                res = await token.json()

                await channel.send(
                    f'token: {res["token"]}')


    @commands.command()
    async def mes(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.callimarie.net/bot/servers?id=837018898142330961") as request:
                if request.status != 200:
                    return await ctx.send(f"Oh no! The api returned an error of {request.status}!")
                try:
                    data = await request.json()


                    await ctx.send(data)
                except Exception as e:
                    return await ctx.send(default.traceback_maker(e))
                

    @commands.command()
    async def hex(self, ctx, *, hex_code=None):
        if hex_code == None: 
            return await ctx.send("Please give me a hex code!")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/canvas/colorviewer?hex={hex_code}") as hex_image:

                imageData = io.BytesIO(await hex_image.read())

                file = discord.File(imageData, "hex.png")

                embed = discord.Embed(title="Here's your hex code visualized!", description=f"**hex code requested is {hex_code}**")

                embed.set_image(url="attachment://hex.png")
                await ctx.send(embed=embed, file=file)

                await session.close()


    @commands.command()
    async def pixelate(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/canvas/pixelate?avatar={member.avatar.url}") as pxiels:
                imageData = io.BytesIO(await pxiels.read())
                file = discord.File(imageData, 'pixels.png')

                em = discord.Embed(
                    title="mmmm saturated pixels"
                )
                

                em.set_image(url="attachment://pixels.png")
                await ctx.send(embed=em, file=file)

                await session.close()  # closing the session and;

    @commands.command()
    async def jail(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/canvas/jail?avatar={member.avatar.url}") as jailedmf:
                imageData = io.BytesIO(await jailedmf.read())
                file = discord.File(imageData, 'jailed.png')

                em = discord.Embed(
                    title="L + ratio + Jailed"
                )
                

                em.set_image(url="attachment://jailed.png")
                await ctx.send(embed=em, file=file)

                await session.close()  # closing the session and;


    @commands.command()
    async def polish(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://147.182.173.16:4503/api/v1/poland/") as token:
                res = await token.json()

                await ctx.send(
                    f'{res["link"]}')





    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title="You Can Find Skye's current invite here", description=f"[**oauth link**](https://discord.com/api/oauth2/authorize?client_id=932462085516968027&permissions=1375936309318&scope=bot)")
        await ctx.send(embed=embed)

    @commands.command()
    async def website(self, ctx):
        embed = discord.Embed(title=f"You can find the website for skye here:", description=f"**https://skyebot.dev/**")

        await ctx.send(embed=embed)

    @commands.command(aliases=['avatar'])
    async def av(self,ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author

        if member == self.bot:
            embed = discord.Embed(description=f"**[Avatar Link]({ctx.bot.user.avatar.url})**")      
            embed.set_author(name=f"{member}", icon_url=ctx.bot.user.avatar)
            embed.set_image(url=member.avatar.url)
            embed.set_footer(text="Yes i know this is exactly like dyno's avatar command.")
        else:
            embed = discord.Embed(description=f"**[Avatar Link]({member.avatar.url})**")      
            embed.set_author(name=f"{member}", icon_url=member.avatar.url)
            embed.set_image(url=member.avatar.url)
            embed.set_footer(text="Yes i know this is exactly like dyno's avatar command.")
        
            await ctx.send(embed=embed)

    @commands.command(aliases=['whois'])
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.author

        show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else "None"

        embed = discord.Embed(title=f"ℹ About **{user.id}**")
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Username", value=f"{user}", inline=False)
        embed.add_field(name="Nickname", value=user.nick if hasattr(user, "nick") else "None", inline=False)
        embed.add_field(name="Account created", value=default.date(user.created_at, ago=True), inline=False)
        embed.add_field(name="Joined this server", value=default.date(user.joined_at, ago=True), inline=False)
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self,ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"Server Info For {guild}", description="----------------------------------", timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name="Number Of Channels", value=len(ctx.guild.channels), inline=False)
        embed.add_field(name="Number Of Roles", value=len(ctx.guild.roles), inline=False)
        embed.add_field(name="Number of Boosters:", value=guild.premium_subscription_count, inline=False)
        embed.add_field(name="Member Count", value=guild.member_count, inline=False)
        embed.add_field(name="Date Of Creation", value=default.date(guild.created_at, ago=True), inline=False)
        embed.add_field(name="Owner Of Server", value=guild.owner, inline=False)
        embed.add_field(name="Server ID", value=guild.id)
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command()
    async def banner(self,ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        banner_url = user.banner.url

        embed = discord.Embed(title=f"Here's ``{member}``'s Banner")
        embed.set_image(url=f"{banner_url}")
        embed.set_footer(text= f'Requested By {ctx.author}', icon_url=ctx.author.avatar)
    
        await ctx.send(embed=embed)

    @commands.command()
    async def vanityurl(self, ctx):
        if ctx.guild.vanity_invite == None:
            await ctx.send("This server does not have an vanity url!")
        else:
            await ctx.send(ctx.guild.vanity_invite)

    @commands.command()
    async def poll(self,ctx, *, content:str):
        embed=discord.Embed(title=f"Question: {content}", description="React to this message with ✅ for yes, ❌ for no.",  color=0xd10a07)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar) 

        message = await ctx.channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        


        


async def setup(bot):
    await bot.add_cog(Random_Stuff(bot))            
