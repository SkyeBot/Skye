import discord

from discord.ext import commands

from discord import app_commands
from discord.app_commands import Choice

from typing import Union, Optional

#Local imports
from core.bot import SkyeBot
from utils import default


class Misc(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @app_commands.command(name="userinfo")
    async def userinfo_slash(self, itr: discord.Interaction, member: Optional[discord.Member]=None):
        member = member or itr.user

        created_date = default.date(member.created_at, ago=True)
        joined_date = default.date(member.joined_at, ago=True)

        show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(member.roles, key=lambda x: x.position, reverse=True) if x.id != itr.guild.default_role.id]
        ) if len(member.roles) > 1 else "None"

        embed = discord.Embed(description=f"**Info About {member.mention}**", color=self.bot.color)

        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Created At", value=created_date,inline=False)
        embed.add_field(name="Joined At", value=joined_date)
        embed.add_field(name="Roles", value=f"**{show_roles}**",inline=False)

        embed.set_author(name=member, icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await itr.response.send_message(embed=embed)