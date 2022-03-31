import datetime
import discord

from discord.ext  import commands
from discord.embeds import Embed

import praw
import random

from praw.reddit import Submission

import aiohttp




class hmmmm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """You will not ask. you will not ask/"""

    @commands.command()
    @commands.is_nsfw()
    async def nsfw(self,ctx):
        nsfw_submission = reddit.subreddit('nsfw').hot()
        post_to_pick = random.randint(1,30)
        for i in range(0, post_to_pick):
            submission = next(x for x in nsfw_submission if not x.stickied)

        embed = discord.Embed(title="Dirty Fucker", description=f"**[{submission.title}](https://reddit.com{submission.permalink})**",timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        embed.set_image(url=submission.url)    
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @nsfw.error
    async def nsfw_error(ctx, error):
        if isinstance(error, commands.NSFWChannelRequired):
            pass

    @commands.command()
    @commands.is_nsfw()
    async def trap(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.callimarie.net/api/v1/femboy") as request:
                if request.status != 200:
                    return await ctx.send("Error")


                data = await request.json()
                trap_image = data["link"]

                embed = discord.Embed(title=f"Here's your free birb image:)")
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                embed.set_image(url=trap_image)
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
                
                await ctx.send(embed=embed)




    @commands.command()
    @commands.is_nsfw()
    async def rule34(self, ctx):
        rule34_submission = reddit.subreddit('rule34').hot()
        post_to_pick = random.randint(1,30)
        for i in range(0, post_to_pick):
            submission = next(x for x in rule34_submission if not x.stickied)

        embed = discord.Embed(title="Dirty Fucker", description=f"**[{submission.title}](https://reddit.com{submission.permalink})**",timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        embed.set_image(url=submission.url)    
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    
    @rule34.error
    async def rule34_error(ctx, error):
        if isinstance(error, commands.NSFWChannelRequired):
            pass


    @commands.command(alias=['thigh', 'Thighs'])
    @commands.is_nsfw()
    async def thighs(self, ctx):
        thighs_submissions = reddit.subreddit('thighs').hot()
        post_to_pick = random.randint(1,30)

        for i in range(0, post_to_pick):
            submissions = next(x for x in thighs_submissions if not x.stickied)

        embed = discord.Embed(title="Here's your thighs, you loser.", description=f"Title/link: [{submissions.title}](https://reddit.com{submissions.permalink})")
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        embed.set_image(url=submissions.url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
    
    
    @thighs.error
    async def nsfw_error(ctx, error):
        if isinstance(error, commands.NSFWChannelRequired):
            pass


async def setup(bot):
    await bot.add_cog(hmmmm(bot))              