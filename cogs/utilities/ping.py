import discord
from discord.ext import commands

from core.bot import SkyeBot

from utils.context import Context
import time

from utils import constants


class ping(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    def format_ping(self, ping: int) -> str:
        p = f"```diff\n{'-' if ping > 150 else '+'} {round(ping)}ms"
        return f"{p.ljust(30)}```"

    @commands.command()
    async def ping(self, ctx: Context):
        """
        Gets the ping of the bot
        this was made from du-cki's ping command (https://github.com/du-cki/Kanapy/blob/main/cogs/Utilities/ping.py#L17-L40)
        thanks for the idea
        """

        start = time.perf_counter()
        message = await ctx.send("🏓 Pong")
        end = time.perf_counter()
        message_ping = self.format_ping((end - start) * 1000)

        websocket = self.format_ping(self.bot.latency * 1000)

        start = time.perf_counter()
        await self.bot.pool.fetch("SELECT 1")
        end = time.perf_counter()

        postgres_ping = self.format_ping((end - start) * 1000)

        start = time.perf_counter()
        async with self.bot.session.get("https://google.com") as resp:
            pass
        end = time.perf_counter()
        aiohttp_ms = self.format_ping((end - start) * 1000)

        em = (
            discord.Embed(color=self.bot.color)
            .add_field(
                name=f"{constants.WEBSOCKET} Websocket", value=websocket, inline=True
            )
            .add_field(
                name=f"{constants.CHAT_BOX} Message", value=message_ping, inline=True
            )
            .add_field(
                name=f"{constants.POSTGRES} Database", value=postgres_ping, inline=True
            )
            .add_field(
                name=f"{constants.AIOHTTP} HTTP request", value=aiohttp_ms, inline=True
            )
            .set_footer(text="Credit to le ducki3#4987 for the original code!")
        )

        await message.edit(content=None, embed=em)
