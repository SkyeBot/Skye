import discord
from discord.ext import commands

from core.bot import SkyeBot
from utils import default


class antiraid(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
    @commands.Cog.listener("on_member_join")
    async def on_member_join_but_for_raids(self, member: discord.Member):
        if member.created_at.timestamp() > 90901:
            if member.guild.id == 980538933370830848:


                channel = self.bot.get_channel(985734583733612575)

                await member.ban(reason="Too new of an account!")
                await channel.send(f"Member: {member} was banned because they're too new of an account!\ncreated at {default.date(member.created_at,ago=True)}")