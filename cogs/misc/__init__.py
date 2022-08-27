import discord
from discord.ext import commands


from .info import Misc
from .bot_info import bot_info


class Misc(Misc, bot_info):
    pass


async def setup(bot):
    await bot.add_cog(Misc(bot))