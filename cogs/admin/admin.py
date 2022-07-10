from typing import Optional, Union
import discord
from discord.ext import commands

from core.bot import SkyeBot
from discord import app_commands

from utils.context import Context

class Admin(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx: Context, user: Union[discord.Member, discord.User, str], *, reason: Optional[str]):
        query = "INSERT INTO blacklist(user_id, reason) VALUES ($1, $2)"
        await self.bot.pool.execute(query, user.id, reason)

        await ctx.send(f"Succesfully blacklisted: {user.mention}")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx: Context, user: Union[discord.Member, discord.User, str, int]):
        query = "DELETE FROM blacklist WHERE user_id = $1"
        await self.bot.pool.execute(query, user.id)  

        await ctx.send(f"Unblacklisted {user.mention} from the bot")

