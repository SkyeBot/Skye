
# -*- coding: utf-8 -*-

import io
import logging
import random
import textwrap
import traceback
from typing import Optional, Union
import typing
import discord

from discord.ext import commands

from discord import Interaction, app_commands

from core.bot import SkyeBot
from utils.context import Context
from utils import default
from contextlib import redirect_stdout

from discord.ext import commands, tasks

import discord

logger = logging.getLogger(__name__)
class owner(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        self.ch_pr.start()
        self._last_result: Optional[typing.Any] = None

    @commands.command()
    async def claim(self, ctx: Context):
        top_gg = await (await ctx.bot.session.get("https://top.gg/api/bots/932462085516968027/votes", headers={"Authorization": ctx.bot.top_gg})).json()
        logger.info(top_gg[0]['username'])
        if top_gg[0]['username'] == ctx.author.name:
            return await ctx.send("Boom baby!!!")
        await ctx.send("You didn't vote smh")
    
    @tasks.loop(minutes=5)
    async def ch_pr(self):
        choices = [f'on {len(self.bot.guilds)} servers', f"Serving over {len(self.bot.users)} Users!", "/botinfo for more info on me!"]
        prescense  = random.choice(choices)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=prescense))

    async def is_owner(interaction: discord.Interaction) -> bool:
        
        if interaction.user.id in [894794517079793704, ]:
            return True
        
        await interaction.response.send_message("You Cannot Use This Command!", ephemeral=True)
        return False

    
    @commands.command()
    @commands.is_owner()
    async def status(self, ctx: Context, *, status: str):

        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))

        await ctx.reply(f"Succesfully changed Status to {status}!", mention_author=False)

    
    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx: Context, user: Union[discord.Member, discord.User, str], *, reason: Optional[str]):
        query = "INSERT INTO blacklist(user_id, reason, time_blacklisted) VALUES ($1, $2, $3)"
        await self.bot.pool.execute(query, user.id, reason, discord.utils.utcnow())

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

    def cleanup_code(self, content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: Context,*, body: str):
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass


            if ret is None:
                if value:
                    embed = discord.Embed(title="Outputted Code", description=f'```py\n{value}\n```')

                    await ctx.send(embed=embed)
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

