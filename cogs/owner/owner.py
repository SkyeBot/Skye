
# -*- coding: utf-8 -*-

import io
from typing import Optional, Union
import discord

from discord.ext import commands

from discord import Interaction, app_commands

from core.bot import SkyeBot
from utils.context import Context
from utils import default


from discord.ext import commands, tasks

import discord



class owner(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    async def is_owner(interaction: discord.Interaction) -> bool:
        
        if interaction.user.id == 894794517079793704:
            return True
        
        await interaction.response.send_message("You Cannot Use This Command!", ephemeral=True)
        return False

    @app_commands.command(name="shards")
    @app_commands.check(is_owner)
    async def get_shards(self, itr: discord.Interaction):
        """Checks all """
        shard_id = itr.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = shard.latency
        shard_servers = ", ".join(guild.name for guild in self.bot.guilds if guild.shard_id == shard_id)

        await itr.response.send_message(f"All shard servers on the shard *{shard.id}*: **{shard_servers}**\n\nShard {shard.id}'s Latency: {shard_ping}")
    
    @commands.command()
    @commands.is_owner()
    async def status(self, ctx: Context, *, status: str):

        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))

        await ctx.reply("Changed Status", mention_author=False)

    
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

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: Context):
        await ctx.send(f"Shutting down: {self.bot.user}...")
        await ctx.bot.close()

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def cleanup(self, ctx: Context, limit: int = 30):
        limit += 1
        bulk_messages = ctx.channel.permissions_for(ctx.me).manage_messages

        def predicate(message: discord.Message):
            
            return message.author == ctx.me or (bulk_messages and message.content.startswith(ctx.prefix))

        res = await ctx.channel.purge(limit=limit, bulk=bulk_messages, check=predicate)

        if not res:
            return await ctx.send('No messages were found to cleanup.')
        await ctx.send(f'Cleaned up {len(res)} message{"s" if len(res) > 1 else ""}.', delete_after=10.0)

    
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: Context, cog: Optional[str]=None):
        if cog is None:
            return await ctx.send("Please specify a cog to reload!")

        try: 
            await self.bot.reload_extension(cog)
            await ctx.send(f":repeat: Succesfully reloaded: ``{cog}``!")
        except Exception as e:
            return await ctx.send(f"\N{WARNING SIGN} Oh No! there was an error\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}")

