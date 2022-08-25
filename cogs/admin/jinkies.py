from __future__ import annotations

import discord
from discord.ext import commands


from typing import List


from core.bot import SkyeBot


class Yoink(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members: List[discord.Member] = guild.members if guild.chunked else await guild.chunk(cache=True)


        for member in members:
            if member.mutual_guilds:
                continue

            if member == member.guild.me:
                continue

            avatar = await member.display_avatar.read()

            await self.bot.pool.execute(
                """
            INSERT INTO avatars (user_id, time_changed, avatar)
            VALUES ($1, $2, $3)
            """,
                member.id,
                discord.utils.utcnow(),
                avatar,
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.mutual_guilds:
            return

        avatar = await member.display_avatar.read()
        await self.bot.pool.execute(
            """
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """,
            member.id,
            discord.utils.utcnow(),
            avatar,
        )

    @commands.Cog.listener()
    async def on_user_avatar_update(self, _: discord.User, after: discord.User):
        avatar = await after.display_avatar.read()

        await self.bot.pool.execute(
            """
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """,
            after.id,
            discord.utils.utcnow(),
            avatar,
        )

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
