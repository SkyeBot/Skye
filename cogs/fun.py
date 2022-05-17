import io
import discord

from discord.ext import commands

import random

import praw





from utils import http

import randfacts
import json

import aiohttp
from lxml import etree


import asyncio

reddit = praw.Reddit(client_id='pua14mlzkyv5_ZfQ2WmqpQ',
                     client_secret='T5loHbaVD7m-RNMpFf0z24iOJsInwg',
                     user_agent='Oxygen',
                     check_for_async= False)


class Fun(commands.Cog):
    """Fun Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def howgay(self,ctx, member:discord.Member = None):    
        IMG_CHOICES = ['https://raw.githubusercontent.com/callimarieYT/CalliWebsite/main/unnamed_1.png', 'https://cdn.discordapp.com/attachments/917008192892977232/923233802074095616/pony.gif', 'https://cdn.discordapp.com/attachments/917008192892977232/923233331750006804/F35A8FAE-91D4-4C56-A77F-C8770349D386.jpg', 'https://cdn.discordapp.com/attachments/904887116381700147/923585698743848960/1639974673621.jpg', 'https://cdn.discordapp.com/attachments/904887116381700147/923585702858489876/IMG_7525.png', 'https://cdn.discordapp.com/attachments/904887116381700147/923585713612685312/IMG_7515.jpg', 'https://cdn.discordapp.com/attachments/904887116381700147/923585864708272138/IMG_7508.gif', 'https://cdn.discordapp.com/attachments/904887116381700147/923585885075804190/FFTEwb5XoAEUYzm.jpg','https://cdn.discordapp.com/attachments/904887116381700147/923585946207793262/565758E6-3785-47F0-8DC7-CB4A6C9E11D1.gif', 'https://media.discordapp.net/attachments/907282095221665835/918919536886030406/caption.gif']
        if member == None:
            member = ctx.author

        embed=discord.Embed(title="how gay are you!!!", description=f"**{member.mention} is {random.randint(0,100)}% homosexual🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈🏳️‍🌈**")
        embed.set_image(url=random.choice(IMG_CHOICES))
        await ctx.send(embed=embed)   

    @howgay.error
    async def urban_error(self,ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You are on a cooldown for 5 seconds!")

    @commands.command(aliases=['howsussy', 'howsussybaka'])
    async def howsus(self,ctx, member:discord.Member = None):
        if member == None:
            member = ctx.author

        IMG_CHOICES = ['https://raw.githubusercontent.com/callimarieYT/CalliWebsite/main/unnamed_1.png', 'https://cdn.discordapp.com/attachments/917008192892977232/923233802074095616/pony.gif', 'https://cdn.discordapp.com/attachments/917008192892977232/923233331750006804/F35A8FAE-91D4-4C56-A77F-C8770349D386.jpg', 'https://cdn.discordapp.com/attachments/904887116381700147/923585698743848960/1639974673621.jpg', 'https://cdn.discordapp.com/attachments/904887116381700147/923585702858489876/IMG_7525.png', 'https://cdn.discordapp.com/attachments/904887116381700147/923585713612685312/IMG_7515.jpg','https://cdn.discordapp.com/attachments/904887116381700147/923585864708272138/IMG_7508.gif', 'https://cdn.discordapp.com/attachments/904887116381700147/923585885075804190/FFTEwb5XoAEUYzm.jpg', 'https://media.discordapp.net/attachments/839929143512137758/918655740716134400/A2C66C28-91A6-4802-978A-FB4B2ECF2414.gif', 'https://cdn.discordapp.com/attachments/904887116381700147/923585946207793262/565758E6-3785-47F0-8DC7-CB4A6C9E11D1.gif', 'https://media.discordapp.net/attachments/907282095221665835/918919536886030406/caption.gif']
        CHOICES = ['``yeah`` <a:noooo:910736617529036830>', '``no ``<:gary:913247181106995271>', '``maybe ``<:maybe:923015512630382623>']

        embed=discord.Embed(title=f"**Is The User {member} Sussy???**", description=f"\u200b")
        embed.add_field(name=f"**The Answer Is:** \u200b", value=f"**\u200b {random.choice(CHOICES)}** ")
        embed.set_image(url=f"{random.choice(IMG_CHOICES)}")
        embed.set_footer(text=f"Requested By {member}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command(aliases=['nickname', 'changenick', 'changenickname'])
    async def nick(self,ctx, member:discord.Member=None):
        nick_file = open("/root/skye/bot/nick.json", "r") # opens the nick file in "read" mode
        nicks = json.loads(nick_file.read()) # loads the json
        nick_file.close() # closes the nick file
    
        nick_choice = random.choice(nicks['nicks'])

        if member == None:
            member = ctx.author
    
        embed = discord.Embed(title=f"Changed Nickname for {member} to", description=f"``{nick_choice}``")
    
   
        if member == self.bot.user:
            await ctx.send('You cannot change my nickname!')
        else:
            if ctx.author == member:
        
                await member.edit(nick=nick_choice)
                await ctx.send(embed=embed)
            else:
                if  ctx.author.guild_permissions.manage_nicknames == False:
                    await ctx.send("``You cant change other's nicknames!``")
                else:
                    try:
                        await member.edit(nick=nick_choice)
                        await ctx.send(embed=embed)
                    except discord.Forbidden():
                        return await ctx.send("skye does not have the sufficent perms to do this!")

                


    @commands.command(aliases=['fact', 'randomfact'])
    async def facts(self,ctx):
        facts = randfacts.get_fact()

        embed = discord.Embed(title="Random Fact Generator!", description=f"``{facts}``")
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command(aliases=['meme'])
    async def memes(self,ctx):
        meme_submissions = reddit.subreddit('meme').hot()
        post_to_pick = random.randint(1,50)
        for i in range(0, post_to_pick):
            Submission = next(x for x in meme_submissions if not x.stickied)

        embed = discord.Embed(title="Random Memes:", description=f"**[{Submission.title}]({Submission.url})**")
        embed.set_image(url=Submission.url)    
        await ctx.send(embed=embed)

    @commands.command()
    async def osugame(self,ctx):
        osu_submission = reddit.subreddit('osugame').hot()
        post_to_pick = random.randint(1,30)
        for i in range(0, post_to_pick):
            submission = next(x for x in osu_submission if not x.stickied)

        embed = discord.Embed(title="top osu posts:", description=f"**[{submission.title}](https://reddit.com{submission.permalink})**")
        embed.set_image(url=submission.url)    
        await ctx.send(embed=embed)

    @commands.command(aliases=["8ball"])
    async def _8ball(self,ctx, *, question: commands.clean_content):
        if question == None:
            await ctx.send("You Need To Give Me A Question!")
        else:
            _8ball_file = open("responses.json", "r")
            responses = json.loads(_8ball_file.read())
            _8ball_file.close()
            _8ball_choice = random.choice(responses['responses'])
        
            message = f"🎱**Question:** {question}\n**Answer:** {_8ball_choice}"
            await ctx.send(message)
        

    @commands.command()
    async def banf(self,ctx, member:discord.Member=None, *, reason=None):
        if member == self.bot.user:
            await ctx.send("BaNf Me AnD i WiLl ChOp OfF yOuR bAlLs!!!")
        else:
            if member == None:
                await ctx.send("WHo ArE yOu BaNfInG?")
            else: 
                if member == ctx.author:
                    await ctx.send('``YoU cAnNoT bAnF yOuRsElF!!!``')
                else:
                    if reason == None:
                        reason="LmAo GeT bAnFeD!!!"
                    embed = discord.Embed(title=f"BaNfEd {member}", description=f"ReAsOn: {reason}")   
                    await ctx.send(embed=embed)


    snipe_message_content = None
    snipe_message_author = None
    snipe_message_id = None

    @commands.Cog.listener()
    async def on_message_delete(self,message):

        global snipe_message_content
        global snipe_message_author
        global snipe_message_id
        global snipe_message_avatar

        snipe_message_content = message.content
        snipe_message_author = message.author
        snipe_message_avatar = message.author.avatar
        snipe_message_id = message.id
        await asyncio.sleep(60)

        if message.id == snipe_message_id:
            snipe_message_author = None
            snipe_message_content = None
            snipe_message_id = None
            snipe_message_avatar = None

    @commands.command()
    async def snipe(self,message):
        if snipe_message_content == None:
            await message.channel.send("There Isn't Anything I Can Snipe!")
        else:
            embed = discord.Embed(title=f"Snipped {snipe_message_author}'s Message!", description=f"Message Snipped:   ``{snipe_message_content}``")
            embed.set_footer(text=f"Requested By {message.author.name}#{message.author.discriminator}", icon_url=snipe_message_avatar.url)
            await message.channel.send(embed=embed)
            return                 

    @commands.command()
    async def kys(self,ctx):
        choices = ['yes you do!', 'no fucking loser','check your kitchen....', 'stop asking me, no.', 'Maybe...', 'kill yourself.']
        choice = random.choice(choices)
        
        embed = discord.Embed(title=f"Do you own an air frier?", description=f"\n\n\n\n\n\n\n\nAnswer: **{choice}**")
        await ctx.send(embed=embed)



    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: commands.clean_content):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                url = await http.get(f"https://api.urbandictionary.com/v0/define?term={search}", res_method="json")
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down!")

            if not url:
                return await ctx.send("I think the API broke...")

            if not len(url["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(url["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            embed = discord.Embed(title=f"Definitions for **{result['word']}**", description=f"```fix\n{definition}```")
            
            await ctx.send(embed=embed)

    @urban.error
    async def urban_error(self,ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Woah there bud! you're on a cooldown for 2 seconds! ||this is global||")

    @commands.command()
    async def beer(self, ctx, user: discord.Member = None, *, reason: commands.clean_content = ""):
        """ BUR """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: WOOOOO BEER FOR MYSELF <:LETSFUCKINGGOOOOOO:929981421530021938> ")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you*  🍻\nhttps://cdn.discordapp.com/attachments/917008192892977232/929981717396217896/FlushedEmojiYouAreHotGIF.gif")
        if user.bot:
            return await ctx.send(f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a **BEER**🍺<:LETSFUCKINGGOOOOOO:929981421530021938> offer from **{ctx.author.name}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False
            

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** <:cri:929981116130144297>")
        except discord.Forbidden:
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)        
    

    @commands.command()
    async def neko(self, ctx):
        headers = {'content-type': 'image/gif'}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.best/api/v1/nekos", headers=headers) as request:
                api= await request.json()
                if request.status ==200:
                    url=api['url']

                    embed = discord.Embed(title="everyone bully this weeb")
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)

                    await session.close()


        
    @commands.command(name="bite", help="Bite someone")
    async def bite(self, ctx, target: discord.Member = None):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nekos.best/api/v1/bite") as request:
                if request.status != 200:
                    return await ctx.send("Error")


                data = await request.json()
                gif = data["url"]



        if not target:
            em = discord.Embed(title="", description="{} bit himself".format(ctx.author.mention),
            colour=0xff6961)
            em.set_image(url=gif)
            em.set_author(name=ctx.author,icon_url=ctx.author.avatar)

            await ctx.send(embed=em)

    
        else:

            em = discord.Embed(title="", description="{} bit {}! how cruel! ".format(ctx.author.mention, target.mention),
            colour = 0xff6961)
            em.set_image(url=gif)
            em.set_author(name=ctx.author,icon_url=ctx.author.avatar)


            await ctx.send(embed=em) 

    @commands.command()
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/joke") as request:
                if request.status != 200:
                    return await ctx.send("Oh no! There was an error with the API! Sorry :(")

                data = await request.json()
                joke = data["joke"]

                embed = discord.Embed(title="Here's your *probably not funny* Joke!", description=joke)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.send(embed=embed)

    @commands.command()
    async def cpp(self, ctx, *, query: str):
        """Search something on cppreference"""
        async with aiohttp.ClientSession() as session:


            url = 'https://en.cppreference.com/mwiki/index.php'
            params = {
                'title': 'Special:Search',
                'search': query
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
            }

            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    return await ctx.send(f'An error occurred (status code: {resp.status}). Retry later.')

                if resp.url.path != '/mwiki/index.php':
                    return await ctx.send(f'<{resp.url}>')

                e = discord.Embed()
                root = etree.fromstring(await resp.text(), etree.HTMLParser())

                nodes = root.findall(".//div[@class='mw-search-result-heading']/a")

                description = []
                special_pages = []
                for node in nodes:
                    href = node.attrib['href']
                    if not href.startswith('/w/cpp'):
                        continue

                    if href.startswith(('/w/cpp/language', '/w/cpp/concept')):
                        # special page
                        special_pages.append(f'[{node.text}](http://en.cppreference.com/{href})')
                    else:
                        if len(special_pages) > 0:
                            e.add_field(name='Language Results', value='\n'.join(special_pages), inline=False)
                        if len(description):
                            e.add_field(name='Library Results', value='\n'.join(description[:10]), inline=False)
                        else:
                            if not len(description):
                                return await ctx.send('No results found.')

                    e.title = 'Search Results'
                    e.description = '\n'.join(description[:15])

                    e.add_field(name='See More', value=f'[`{discord.utils.escape_markdown(query)}` results]({resp.url})')
            
                    await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(Fun(bot))     
