import itertools
import os
from typing import List, Optional, Union
import discord

from discord.ext import commands

from discord import app_commands

import datetime

import logging
import pkg_resources
import psutil
import inspect


#local imports
from utils.context import Context
from utils import default, time
from utils import constants


start_time = datetime.datetime.utcnow().timestamp()


class InfoSelect(discord.ui.Select):
    def __init__(self, og_embed: discord.Embed):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='avatar', description='Avatar of the user'),
            discord.SelectOption(label='Bot info', value=f"info",description="Actual Bot Info"),

        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(min_values=1, max_values=1, options=options)
        self.og_embed = og_embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.values[0] == "info":
            return await interaction.edit_original_response(embed=self.og_embed)
            
        
        if self.values[0] == "avatar":
            embed = discord.Embed(description="Here's my current avatar!")
            embed.set_image(url=interaction.client.user.display_avatar.url)
            return await interaction.message.edit(embed=embed)


class InfoView(discord.ui.View):
    def __init__(self, og_embed):
        super().__init__(timeout=180)
        self.add_item(InfoSelect(og_embed))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.link,label="Website", url="https://skyebot.dev/", emoji=constants.WEBSITE))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Support Server", url="https://discord.gg/Zwn7D78pDw", emoji=constants.INVITE))



class bot_info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bot_uptime(self, *, brief: bool = False) -> str:
        return time.human_timedelta(self.bot.uptime, accuracy=None, brief=brief, suffix=False)

    @app_commands.command()
    async def uptime(self,interaction: discord.Interaction):
        """Tells you how long the bot has been up for."""
        await interaction.response.send_message(f'I have been running since: **{self.get_bot_uptime()}** ago')

            

    @app_commands.command()
    async def botinfo(self, itr: discord.Interaction):
        """Provides info about the bot"""
        await itr.response.defer()
        process = psutil.Process(os.getpid())
        ramUsage = process.memory_full_info().rss / 1024**2    
    
        version = pkg_resources.get_distribution("discord.py").version

        embed = discord.Embed(title="Hey there, im Skye! An multipurpose open-source discord bot!",
            description=f"Source Code: {constants.GITHUB} [source](https://github.com/SkyeBot/Skye/tree/rewrite) | "
            f"Invite Link: {constants.INVITE} [invite me](https://discord.com/api/oauth2/authorize?client_id=932462085516968027&permissions=8&scope=bot%20applications.commands) | "
            f"Top.gg Link: {constants.TOP_GG} [top.gg](https://top.gg/bot/932462085516968027) | ", 
 
            color=self.bot.color

        )
        

        embed.set_author(name="I was made by: Sawsha#0598!", icon_url=(await itr.client.application_info()).owner.display_avatar.url)

                # statistics
        total_members = 0

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
            value=f"**servers:** {guilds}\n**avg bot/human:** {round(sum(avg) / len(avg), 2)}%\n**Currently serving over {total_members} People!**",
        )
    
        embed.add_field(name="Channels", value=f"{total:,} total\n{text:,} text\n{voice:,} voice")
        embed.add_field(name="Cogs loaded", value=len([x for x in self.bot.cogs]),)
        embed.add_field(name="RAM Usage", value=f"{ramUsage:.2f} MB")



    
        embed.set_footer(
            text=f"Made with love ❤️ by Sawsha#0598 :))",
        )
        embed.timestamp = discord.utils.utcnow()

        await itr.followup.send(embed=embed, view=InfoView(embed))


