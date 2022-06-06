import itertools
import os
from typing import Union
import discord

from discord.ext import commands

from discord import app_commands

import time

import datetime

import logging
import pkg_resources
import psutil

import pygit2


#local imports
from core.bot import SkyeBot
from utils.context import Context
from utils import default
from utils import constants


start_time = datetime.datetime.utcnow().timestamp()


def format_commit(commit):
    short, _, _ = commit.message.partition("\n")
    short = short[0:40] + "..." if len(short) > 40 else short
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)
    offset = discord.utils.format_dt(commit_time, style="R")
    return f"[`{short_sha2}`](https://github.com/SkyeBot/Skye/commit/{commit.hex}) {short} ({offset})"


def get_latest_commits(limit: int = 5):
    repo = pygit2.Repository("./.git")
    commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), limit))
    return "\n".join(format_commit(c) for c in commits)



class bot_info(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx: Context):
        current_time = datetime.datetime.utcnow().timestamp()
        difference = datetime.datetime.fromtimestamp(current_time - start_time)
        text = discord.utils.format_dt(difference.utcnow(), style="R")
        self.bot.logger.info(difference)
        self.bot.logger.info(text)
        embed = discord.Embed(description=f"**I have been running since: {text}**",colour=self.bot.color, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=self.bot.user,icon_url=self.bot.user.display_avatar.url)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    @app_commands.command()
    async def botinfo(self, itr: discord.Interaction):
        """Provides info about the bot"""

        process = psutil.Process(os.getpid())
        ramUsage = process.memory_full_info().rss / 1024**2

        version = pkg_resources.get_distribution("discord.py").version

        embed = discord.Embed(title="Hi! im Skye! I'm a multipurpose open source Discord Bot!",
            description=f"Source Code: {constants.GITHUB} [source](https://github.com/SkyeBot/Skye/tree/rewrite) | "
            f"Invite Link: {constants.INVITE} [invite me](https://discord.com/api/oauth2/authorize?client_id=932462085516968027&permissions=8&scope=bot%20applications.commands) | "
            f"Top.gg Link: {constants.TOP_GG} [top.gg](https://top.gg/bot/932462085516968027) | ",
            color=self.bot.color

        )

        embed.add_field(name="Latest updates:", value=get_latest_commits(limit=5), inline=False)

        embed.set_author(name="I was made by: Sawsha#0598!", icon_url="https://cdn.discordapp.com/avatars/894794517079793704/02fc9ee15032b33756ba9829f00449d9.png?size=1024")

                # statistics
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        total = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable is True: 
                continue

            total_members += guild.member_count
            for channel in guild.channels:
                total += 1
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1
        
            avg = [(len([m for m in g.members if not m.bot]) / g.member_count) * 100 for g in self.bot.guilds]

        embed.add_field(name="Library", value=f"**discord.py {version}**")
        embed.add_field(name="Date Created", value=default.date(self.bot.user.created_at, ago=True))
        embed.add_field(
            name="Bot servers",
            value=f"**servers:** {guilds}\n**avg bot/human:** {round(sum(avg) / len(avg), 2)}%",
        )
        embed.add_field(name="Channels", value=f"{total:,} total\n{text:,} text\n{voice:,} voice")
        embed.add_field(name="Cogs loaded", value=len([x for x in self.bot.cogs]),)
        embed.add_field(name="RAM Usage", value=f"{ramUsage:.2f} MB")



    
        embed.set_footer(
            text=f"Made with love ❤️ by Sawsha#0598 :))",
        )
        embed.timestamp = discord.utils.utcnow()

        await itr.response.send_message(embed=embed)

    @app_commands.command(name="source", description="Links you to the source codde")
    async def source_slash(self, itr: discord.Interaction):
        embed = discord.Embed(description=f"Here's a link to my [Source Code](https://github.com/SkyeBot/Skye/tree/rewrite)", color=self.bot.color, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.display_avatar.url)
        await itr.response.send_message(embed=embed)
