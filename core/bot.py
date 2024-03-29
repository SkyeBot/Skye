import asyncio
from collections import defaultdict
import random
import re
import sys
import traceback

import discord
from discord.ext import commands
from typing import Optional, TypeVar, Union
import datetime
import logging
import os
import aiohttp
import thino
import asyncpg
import datetime as dt
from discord import app_commands
import roblox
from utils.osu_utils import Osu
import asyncpraw
from cogs.misc.info import DropdownView

import pkg_resources

from typing_extensions import ParamSpec
T = TypeVar("T")
EB = TypeVar("EB", bound="SkyeBot")
P = ParamSpec("P")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True


class SkyeBot(commands.AutoShardedBot):
    bot_app_info: discord.AppInfo

    def __init__(
        self,*,
        session: aiohttp.ClientSession, 
        thino_session: thino.Client,
        pool: asyncpg.Pool,
        osu: Osu,
        reddit: asyncpraw.Reddit,
        top_gg: str,
        **kwargs   
    ):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.logger = logging.getLogger(__name__)
        self.session: aiohttp.ClientSession = session
        self.thino: thino.Client = thino_session
        self.pool: asyncpg.Pool = pool
        self.color = 0x3867a8
        self.error_color = 0xB00020
        self.tick = self.tick

        self.top_gg = top_gg
        self.resumes: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.identifies: defaultdict[int, list[datetime.datetime]] = defaultdict(list)
        self.roblox = roblox.Client()
        self.osu: Osu = osu
        self.reddit: asyncpraw.Reddit  = reddit
        self.config = os.environ
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 

        super().__init__(
            command_prefix=commands.when_mentioned_or("skye "),
            intents=intents,
            owner_ids=[506899611332509697, 894794517079793704, 739219467455823921],
            activity=discord.Activity(type=discord.ActivityType.playing, name="Ultrakill and Osu!")
        )

    def tick(self, opt: Optional[bool], label: Optional[str] = None) -> str:
        lookup = {
            True: '<:greenTick:1014007189368750081>',
            False: '<:redTick:1014007248902688828>',
            None: '<:greyTick:1008947195233443881>',
        }
        emoji = lookup.get(opt, '<:redTick:1014007248902688828>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji



    @property
    def owner(self):
        return self.bot_app_info.owner

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()
        if self._connected:
            msg = f"Bot reconnected at {datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            self.logger.info(msg)       
        else:
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            msg = (
                f"Successfully logged into {self.user}. ({round(self.latency * 1000)}ms)\n"
                f"Discord.py Version: {discord.__version__} | {pkg_resources.get_distribution('discord.py').version}\n"
                f"Python version: {sys.version}\n"
                f"Created Postgresql Pool!\n"
                f"Running {self.shard_count} Shards!\n"
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            )
            self.logger.info(f"{msg}")
            
            for extension in self.cogs:
                self.logger.info(f" - Loaded cogs.{extension.lower()}")


    

    async def on_shard_resumed(self, shard_id: int):
        self.logger.info(f'Shard ID {shard_id} has resumed...')
        self.resumes[shard_id].append(discord.utils.utcnow())
        
    async def setup_hook(self):
        persistent_query = "SELECT * FROM persistent_view"
        
        for row in await self.pool.fetch(persistent_query):
            self.add_view(DropdownView(row['user_id'], row['author_id'],row['guild_id']), message_id=row['message_id'])
    


    async def on_error(self, event: str, *args, **kwargs):
        error = sys.exc_info()[1]
        error_type = type(error)
        trace = error.__traceback__
        error_message = "".join(traceback.format_exception(error_type, error, trace))
        channel = self.get_channel(980538933370830851)
        embed = discord.Embed(
            title="An Error Occurred",
            description=f"**__Event:__** {event.title().replace('_', ' ')}\n"
            f"**__Error:__** {error_type.__name__}\n```py\n{error_message}\n```",
            colour=self.error_color,
            timestamp=discord.utils.utcnow(),
        )
        await channel.send(embed=embed)
        return await super().on_error(event, *args, **kwargs)

    async def on_tree_error(
        self,
        interaction: discord.Interaction,
        command: Optional[Union[app_commands.ContextMenu, app_commands.Command]],
        error: app_commands.AppCommandError,
    ):
        if command and getattr(command, "on_error", None):
            return

        if self.extra_events.get("on_app_command_error"):
            return interaction.client.dispatch(
                "app_command_error", interaction, command, error
            )

        raise error from None

    async def on_app_command_completion(self, interaction: discord.Interaction, command: Union[discord.app_commands.Command, discord.app_commands.ContextMenu]):
        if (interaction.type == discord.InteractionType.application_command):
            await self.pool.execute(
                "INSERT INTO commands (user_id, command_name) VALUES ($1, $2)",
                interaction.user.id,
                interaction.command.name,
            )
            
            try:
                loc = interaction.guild
            except:
                loc = interaction.user
            else:
                loc = interaction.guild

            date = dt.datetime.now()
            waktu = date.strftime("%d/%m/%y %I:%M %p")

            if interaction.namespace:
                self.logger.info(str(interaction.namespace))

            choice = random.choices([234, 675, 1274, 3030, 56589, 2232], cum_weights=[0.9, 5, 11, 14, 8, 13], k=1)
            self.logger.info(choice)

            if choice[0] == 234:
                voteEmbed = discord.Embed(
                    title = f'{self.user.name}:tm:',
                    description = f'If you like using `{self.user}`, please consider voting for the bot!',
                    color = 0xe8718d
                )
                voteEmbed.add_field(name='Top.gg', value="Click **[here](https://top.gg/bot/932462085516968027/vote \"Please vote!\")** to vote on [top.gg](https://top.gg)!", inline=False)
                voteEmbed.add_field(name='Discord Bot List', value="Click **[here](https://discordbotlist.com/bots/skye-7292 \"Please vote!\")** to vote on [discordbotlist.com](https://discordbotlist.com)!", inline=False)
                voteEmbed.set_thumbnail(url=self.user.avatar.url)
                voteEmbed.set_footer(text="Thank you for voting, it's very appreciated!!")
                await interaction.channel.send(embed=voteEmbed)
            try:
                text = f" `{waktu}` | **{interaction.user}** used `/{interaction.command.name}` command on `#{interaction.channel}`, **{loc}**"
                self.logger.info(text.replace('*', '').replace('`', ''))
            except:
                text = f" `{waktu}` | **{interaction.user}** used `/{interaction.command.name}` command on **{loc}**"
                self.logger.info(text.replace('*', '').replace('`', ''))


    async def on_message(self, message: discord.Message):
        if re.fullmatch(rf"<@!?{self.user.id}>", message.content):
            await message.channel.send(f"Hi! im skye! im a multipurpose discord bot!\nI primarily use slash commands, so if you want to see my commands, just do ``/`` \N{HEAVY BLACK HEART}")

        await self.process_commands(message)

    async def on_guild_join(self, guild: discord.Guild):
        channel = self.get_channel(1013028282159091752)
        embed = discord.Embed(title=f"Joined Server", description=f"Name: {guild.name} ({guild.id})\nOwner: {guild.owner} ({guild.owner.id})")
        people = 0
        bots = 0
        total = 0
        for user in guild.members:
            total += 1
            if not user.bot:
                people += 1
            
            if user.bot:
                bots += 1
            

        embed.add_field(name="Members", value=f"\N{PEOPLE HUGGING} {people} / \N{ROBOT FACE} {bots}\nTotal: {total}")
        embed.timestamp = guild.me.joined_at
        embed.color = discord.Color.green()
        await channel.send(embed=embed)
        

        try:
            await self.pool.execute('INSERT INTO guilds(guild_id, guild_name, owner_id) VALUES ($1, $2, $3)',guild.id, guild.name, guild.owner_id)
            self.logger.info(f"! Added {guild.id} To The Database !")
        except asyncpg.exceptions.UniqueViolationError:
            self.logger.info(f"Guild: {guild.id} is already in the database, passing")

    async def on_guild_remove(self, guild: discord.Guild):
        channel = self.get_channel(1013028282159091752)
        embed = discord.Embed(title=f"Left server!", description=f"Name: {guild.name} ({guild.id})\nOwner: {guild.owner} ({guild.owner.id})")
        people = 0
        bots = 0
        total = 0
        for user in guild.members:
            total += 1
            if not user.bot:
                people += 1
            
            if user.bot:
                bots += 1
            

        embed.add_field(name="Members", value=f"\N{PEOPLE HUGGING} {people} / \N{ROBOT FACE} {bots}\nTotal: {total}")
        embed.timestamp = discord.utils.utcnow()
        embed.color = discord.Color.red()
        await channel.send(embed=embed)


        await self.pool.execute('DELETE FROM guilds WHERE guild_id = $1', guild.id)
        self.logger.info(f"! Removed {guild.id} To The Database !")


    async def close(self):
        try:
            await self.pool.close()
            self.logger.info("Closed Database Pool Connection.")
            await self.session.close()
            self.logger.info("Closed Session.")
        finally:
            await super().close()
