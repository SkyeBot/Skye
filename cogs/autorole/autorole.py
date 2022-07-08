import discord

from discord.ext import commands

from discord import app_commands

from core.bot import SkyeBot


class autorole(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
    