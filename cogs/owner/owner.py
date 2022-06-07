
# -*- coding: utf-8 -*-

from typing import Optional
import discord

from discord.ext import commands

from discord import Interaction, app_commands

from core.bot import SkyeBot

from utils.context import Context
from utils import default

# This example requires the 'message_content' privileged intent to function.

from discord.ext import commands

import discord
from urllib.parse import quote_plus
# Define a simple View that gives us a google link button.
# We take in `query` as the query that the command author requests for
class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f'https://www.google.com/search?q={query}'

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))



class owner(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    async def is_nsfw(interaction: discord.Interaction) -> bool:
        
        if interaction.user.id == 894794517079793704:
            return True
        
        await interaction.response.send_message("You Cannot Use This Command!", ephemeral=True)
        return False

    @app_commands.command(name="shards")
    @app_commands.check(is_nsfw)
    async def get_shards(self, itr: discord.Interaction):
        """Checks all """
        shard_id = itr.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = shard.latency
        shard_servers = ", ".join(guild.name for guild in self.bot.guilds if guild.shard_id == shard_id)

        await itr.response.send_message(f"All shard servers on the shard *{shard.id}*: **{shard_servers}**")

    @app_commands.command(name="test1")
    @app_commands.check(is_nsfw)
    async def error_1(self, itr: discord.Interaction):
        """Checks all """
        shard_id = itr.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = shard.latency
        shard_servers = ", ".join(guild.name for guild in self.bot.guilds if guild.shard_id == shard_id)

        return self.bot.dispatch('error', itr.command.qualified_name)

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

    @commands.command()
    @commands.is_owner()
    async def logs(self,ctx: Context):
        with open('./discord.log')as f:
            em = discord.Embed(
                description=f"{self.bot.tick(True)} Here's the logs! ```css\n{''.join(f.readlines())}\n```",
                color=0x2f3136
            )
        await ctx.send(embed=em)

    @commands.command()
    async def google(self, ctx: Context, *, query: str):
        """Returns a google link for a query"""
        await ctx.send(f'Google Result for: `{query}`', view=Google(query))



        