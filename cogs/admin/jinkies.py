from __future__ import annotations

from io import BytesIO
import string
import aiohttp
import discord
from discord.ext import commands

from datetime import datetime

from typing import Union, List

from utils.context import Context

from core.bot import SkyeBot


class Yoink(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members: List[discord.Member] = await guild.chunk(cache=True) if not guild.chunked else guild.members

        

        for member in members:
            if member.mutual_guilds or member == member.guild.me:
                continue
            
            avatar = await member.display_avatar.read()

            await self.bot.pool.execute("""
            INSERT INTO avatars (user_id, time_changed, avatar)
            VALUES ($1, $2, $3)
            """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.mutual_guilds:
            return
        
        avatar = await member.display_avatar.read()
        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_user_avatar_update(self, _: discord.User, after: discord.User):
        avatar = await after.display_avatar.read()

        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, after.id, discord.utils.utcnow(), avatar)


    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)
    
    async def get_banner(self, banner_url):
        async with self.bot.session.get(banner_url) as resp:
            bytes = await resp.read()
            
        return bytes

async def setup(bot):
    await bot.add_cog(Yoink(bot))