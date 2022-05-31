import datetime
from io import BytesIO
import pathlib
import secrets
import discord
from discord.ext import commands
from typing import Union, List
from core.bot import SkyeBot
from discord import app_commands
from discord.app_commands import Choice

class NSFW(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        self.ENDPOINTS = ["tomboy", "neko", "femboy", "porn", "hentai", "thighs", "helltaker"]

    async def fruit_autocomplete(self, interaction: discord.Interaction,current: str,) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=endpoints, value=endpoints)
            for endpoints in self.ENDPOINTS if current.lower() in endpoints.lower()
        ]

    @app_commands.command(description="An NSFW command",nsfw=True)
    @app_commands.autocomplete(endpoints=fruit_autocomplete)
    async def nsfw(self, interaction: discord.Interaction, *, endpoints: str):
        if endpoints not in self.ENDPOINTS:
            endpoints = ", ".join(x for x in self.ENDPOINTS)
            return await interaction.response.send_message(f"Invalid Endpoint!\nPlease choose from one of these: **{endpoints}**")
    
        data = await self.bot.thino.get(endpoints.lower())
        async with self.bot.session.get(f"https://i.thino.pics/{data.filename}") as resp:
            if resp.status == 404:
                return await interaction.response.send_message("No image was found in this endpoint!")

            bio = BytesIO(await resp.read())
            bio.seek(0)
    
            embed = discord.Embed(description=f"File Name: [{data.raw['filename']}]({data.raw['url']}) \nEndpoint: [{endpoints}](https://thino.pics{data.raw['endpoint']})", color=0xc98cbf )
            embed.set_image(url=f"attachment://{data.filename}")
            embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Powered by thino.pics!")

            await interaction.response.send_message(embed=embed, file=discord.File(bio, filename=data.filename))

    @app_commands.command(description=f"Search for an NSFW image from the thino.pics API", nsfw=True)
    async def search(self, interaction:discord.Interaction, image: str):
        finished_url = f"https://i.thino.pics/{str(image)}"
        async with self.bot.session.get(f"https://thino.pics/search/{image}") as request:
            data = await request.json()
            url = data['url']
    
        async with self.bot.session.get(f"https://i.thino.pics/{image}") as req:
            if req.status == 404:
                return await interaction.response.send_message("No image was found!")
  
            bio = BytesIO(await req.read())
            bio.seek(0)

        if url == "https://thino.pics/api/v1/hentai":
            url_endpoint = "hentai"

        if url == "https://thino.pics/api/v1/helltaker":
            url_endpoint = "Helltaker"

        if url == "https://thino.pics/api/v1/neko":
            url_endpoint = "neko"

        if url == "https://thino.pics/api/v1/tomboy":
            url_endpoint = "tomboy"

        if url == "https://thino.pics/api/v1/femboy":
            url_endpoint = "femboy"

        if url == "https://thino.pics/api/v1/thighs":
            url_endpoint = "thighs"

        if url == "https://thino.pics/api/v1/dildo":
            url_endpoint = "dildo"

        if url == "https://thino.pics/api/v1/porn":
            url_endpoint = "porn"

        print(url_endpoint)
        print(url)
        print(finished_url)
        embed = discord.Embed(description=f"Found the file name: [{image}]({finished_url}) on the endpoint: [{url_endpoint}]({url})", timestamp=datetime.datetime.utcnow(), color=self.bot.color)
        embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        embed.set_image(url=finished_url)
        embed.set_footer(text="Powered by thino.pics!")

        await interaction.response.send_message(embed=embed)
