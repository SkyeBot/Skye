import discord

from discord.ext import commands

from discord import app_commands

import time

import datetime

import logging

#local imports
from core.bot import SkyeBot
from utils.context import Context


start_time = datetime.datetime.utcnow().timestamp()


class bot_info(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx: Context):
        current_time = datetime.datetime.utcnow().timestamp()
        difference = datetime.datetime.fromtimestamp(current_time - start_time)
        text = discord.utils.format_dt(difference.utcnow(), style="F")
        self.bot.logger.info(difference)
        self.bot.logger.info(text)
        embed = discord.Embed(description=f"**I have been running since: {text}**",colour=self.bot.color, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=self.bot.user,icon_url=self.bot.user.display_avatar.url)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)