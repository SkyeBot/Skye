
import discord

from typing import Union, List

from .core import CoreDB


class LevellingDB(CoreDB):
    async def new_config(self, guild: Union[discord.Guild, int]):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO levelling_config (guild_id) VALUES ($1)", guild_id
                )

    async def get_config(self, guild: Union[discord.Guild, int]) -> Union[dict, None]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchrow(
                    "SELECT * FROM levelling_config WHERE guild_id=$1",
                    guild_id,
                )
                if config:
                    return dict(config)
        return None

    async def delete_config(self, guild: Union[discord.Guild, int]) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM levelling_config WHERE guild_id=$1", guild_id
                )
                return True

    async def set_channel(
        self,
        guild: Union[discord.Guild, int],
        channel: Union[discord.TextChannel, int, None],
    ) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        channel_id = channel.id if isinstance(channel, discord.TextChannel) else channel
        config = await self.get_config(guild_id)
        if not config:
            return False
        if config.get("announce_channel") == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET announce_channel=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )
                return True

    async def set_message(
        self, guild: Union[discord.Guild, int], message: Union[str, None]
    ) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        if config.get("levelup_message") == message:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET levelup_message=$1 WHERE guild_id=$2",
                    message,
                    guild_id,
                )
                return True

    async def blacklist_add(
        self,
        guild: Union[discord.Guild, int],
        item: Union[discord.Role, discord.TextChannel, int],
    ) -> bool:
        if isinstance(item, int):
            if isinstance(guild, int):
                guild = self.bot.get_guild(guild)
            combined = guild.text_channels + guild.roles
            item = discord.utils.get(combined, id=item)
            if not item:
                return False
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        if isinstance(item, discord.TextChannel):
            blacklist_type = "blacklisted_channels"
        else:
            blacklist_type = "blacklisted_roles"
        blacklist: list = config.get(blacklist_type) or []
        if item.id in blacklist:
            return False
        blacklist.append(item.id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE levelling_config SET {blacklist_type}=$1 WHERE guild_id=$2",
                    blacklist,
                    guild_id,
                )
                return True

    async def blacklsit_remove(
        self,
        guild: Union[discord.Guild, int],
        item: Union[discord.Role, discord.TextChannel, int],
    ) -> bool:
        if isinstance(item, int):
            if isinstance(guild, int):
                guild = self.bot.get_guild(guild)
            combined = guild.text_channels + guild.roles
            item = discord.utils.get(combined, id=item)
            if not item:
                return False
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        if isinstance(item, discord.Role):
            blacklist_type = "blacklisted_roles"
        else:
            blacklist_type = "blacklisted_channels"
        blacklist: list = config.get(blacklist_type)
        if item.id not in blacklist:
            return False
        blacklist.remove(item.id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE levelling_config SET {blacklist_type}=$1 WHERE guild_id=$2",
                    blacklist,
                    guild_id,
                )
                return True

    async def new_user(
        self,
        guild: Union[discord.Guild, int],
        user: Union[discord.User, discord.Member, int],
        xp: int = 15,
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, (discord.User, discord.Member)) else user
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO levelling_users (user_id, guild_id, xp) VALUES ($1, $2, $3)",
                    user_id,
                    guild_id,
                    xp,
                )

    async def get_users(
        self, guild: Union[discord.Guild, int]
    ) -> Union[List[dict], None]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                users = await conn.fetch(
                    "SELECT * FROM levelling_users WHERE guild_id=$1",
                    guild_id,
                )
                if users:
                    return [dict(profile) for profile in users]
        return None

    async def get_user(
        self,
        guild: Union[discord.Guild, int],
        user: Union[discord.User, discord.Member, int],
    ) -> Union[dict, None]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, (discord.User, discord.Member)) else user
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                profile = await conn.fetchrow(
                    "SELECT * FROM levelling_users WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
                if profile:
                    return dict(profile)
        return None

    async def delete_user(
        self,
        guild: Union[discord.Guild, int],
        user: Union[discord.User, discord.Member, int],
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, (discord.User, discord.Member)) else user
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM levelling_users WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )

    async def add_xp(
        self,
        guild: Union[discord.Guild, int],
        user: Union[discord.User, discord.Member, int],
        xp: int = 15,
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, (discord.User, discord.Member)) else user
        user = await self.get_user(guild_id, user_id)
        if not user:
            await self.new_user(guild_id, user_id)
        else:

            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "UPDATE levelling_users SET xp=xp+$1 WHERE guild_id=$2 AND user_id=$3",
                        xp,
                        guild_id,
                        user_id,
                    )
        user = await self.get_user(guild_id, user_id)
        return user

    async def add_level(
        self,
        guild: Union[discord.Guild, int],
        user: Union[discord.User, discord.Member, int],
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, (discord.User, discord.Member)) else user
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_users SET level=level+1 WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
        profile = await self.get_user(guild_id, user_id)
        return profile

    async def get_rewards(self, guild: Union[discord.Guild, int]):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                rewards = await conn.fetch(
                    "SELECT * FROM levelling_rewards WHERE guild_id=$1", guild_id
                )
                if rewards:
                    return [dict(reward) for reward in rewards]
        return None

    async def get_level_rewards(
        self, guild: Union[discord.Guild, int], level: int
    ) -> Union[list, dict, None]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        _rewards = await self.get_rewards(guild_id)
        if not _rewards:
            return None
        rewards = []
        for reward in _rewards:
            if reward.get("level") == level:
                rewards.append(reward)
        if len(rewards) in [0, 1]:
            try:
                return rewards[0]
            except IndexError:
                return None
        return rewards

    async def add_reward(
        self,
        guild: Union[discord.Guild, int],
        level: int,
        role: Union[discord.Role, int],
    ) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        role_id = role.id if isinstance(guild, discord.Role) else role
        rewards = await self.get_level_rewards(guild_id, level)
        if isinstance(rewards, list):
            for r in rewards:
                if r.get("role") == role_id:
                    return False
        elif isinstance(rewards, dict):
            if rewards.get("role") == role_id:
                return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO levelling_rewards (guild_id, level, role) VALUES ($1, $2, $3)",
                    guild_id,
                    level,
                    role_id,
                )
                return True

    async def remove_reward(
        self,
        guild: Union[discord.Guild, int],
        role: Union[discord.Role, int],
    ) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        role_id = role.id if isinstance(guild, discord.Role) else role
        rewards = await self.get_rewards(guild_id)
        is_existing = False
        if isinstance(rewards, list):
            for r in rewards:
                if r.get("role") == role_id:
                    is_existing = True
        elif isinstance(rewards, dict):
            if rewards.get("role") == role_id:
                is_existing = True
        if not is_existing:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM levelling_rewards WHERE role=$1", role_id
                )
                return True