from discord.ext import commands
from core.bot import SkyeBot


class Anime(commands.GroupCog, name="anime"):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
