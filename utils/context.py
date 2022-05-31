import discord
from discord.ext import commands

from typing import TYPE_CHECKING,Union, Any, Optional

if TYPE_CHECKING:
    from core.bot import SkyeBot
    from asyncpg import Pool, Connection
    from aiohttp import ClientSession
    from thino import Client
    
class Context(commands.Context):

    """An custom context class that might not be used much since rewrite is for slash commands (it's good to have though) ;-;"""
    
    channel: Union[discord.VoiceChannel, discord.TextChannel, discord.Thread, discord.DMChannel]
    prefix: str
    command: commands.Command[Any, ..., Any]
    bot: SkyeBot

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pool = self.bot.pool
        self._db: Optional[Union[Pool, Connection]]
        self.thino: Optional[Client]

    def __repr__(self) -> str:
        return '<Context>'

    @property
    def session(self) -> ClientSession:
        return self.bot.session

    @property
    def db(self) -> Union[Pool, Connection]:
        return self._db if self._db else self.pool

    @property
    def thino(self) -> Client:
        return self.thino if self.thino else self.bot.thino