from io import BytesIO
import discord
from discord.ext import commands
from typing import Union
from core.bot import SkyeBot
import secrets


class NSFW(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    async def nsfw(self, ctx: commands.Context, *, choices: str):
        data = await self.bot.thino.get(choices.lower())
        
        async with self.bot.session.get(f"https://i.thino.pics/{data.filename}") as resp:
            print(data.url)
            print(resp.content)
            print(resp.url)
            if resp.status == 404:
                return await ctx.send("No image was found!")
            else:
                bio = BytesIO(await resp.read())
                bio.seek(0)
        
                filename = secrets.token_urlsafe(5)
                embed = discord.Embed(description=f"Here's your free porn image from the endpoint: {choices}")
                embed.set_image(url=f"attachment://{data.filename}")
                embed.set_footer(text="Powered By thino.pics!")

                await ctx.send(embed=embed, file=discord.File(bio, filename=data.filename))