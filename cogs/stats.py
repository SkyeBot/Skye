from __future__ import annotations
import asyncio
import json
import logging
from discord.ext import tasks, commands
import datetime
import textwrap
import discord
from core.bot import SkyeBot
from utils import date

log = logging.getLogger(__name__)


class GatewayHandler(logging.Handler):
    def __init__(self, cog: Stats):
        self.cog: Stats = cog
        super().__init__(logging.INFO)

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.name == "discord.gateway"
            or "Shard ID" in record.msg
            or "Websocket closed " in record.msg
            or "Ignoring exception in " in record.msg
        )

    def emit(self, record: logging.LogRecord) -> None:
        self.cog.add_record(record)


class Stats(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        self._gateway_queue: asyncio.Queue = asyncio.Queue()
        self.gateway_worker.start()

    def _clear_gateway_data(self):
        one_week_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)

        to_remove = [
            index for index, dt in enumerate(self._resumes) if dt < one_week_ago
        ]
        for index in reversed(to_remove):
            del self._resumes[index]

        for _, dates in self._identifies.items():
            to_remove = [index for index, dt in enumerate(dates) if dt < one_week_ago]
            for index in reversed(to_remove):
                del dates[index]

    @property
    def webhook(self) -> discord.Webhook:
        wh_url = self.bot.config.get("LOGGING_WEBHOOK")
        self.bot.logger.info(wh_url)
        return discord.Webhook.from_url(wh_url, session=self.bot.session)

    def cog_unload(self):
        self.gateway_worker.cancel()

    @commands.Cog.listener()
    async def on_socket_raw_send(self, data: str) -> None:
        if '"op":2' not in data and '"op":6' not in data:
            return
        back_to_json = json.loads(data)
        if back_to_json["op"] == 2:
            payload = back_to_json["d"]
            inner_shard = payload.get("shard", [0])
            self._identifies[inner_shard[0]].append(datetime.datetime.now(datetime.timezone.utc))

        else:
            self._resumes.append(datetime.datetime.now(datetime.timezone.utc))
        self._clear_gateway_data()

    @tasks.loop(seconds=10)
    async def gateway_worker(self):
        record = await self._gateway_queue.get()
        await self.notify_gateway_status(record)

    def add_record(self, record: logging.LogRecord) -> None:
        self._gateway_queue.put_nowait(record)

    async def notify_gateway_status(self, record: logging.LogRecord) -> None:
        attributes = {"INFO": "\N{INFORMATION SOURCE}", "WARNING": "\N{WARNING SIGN}"}

        emoji = attributes.get(record.levelname, "\N{CROSS MARK}")
        dt = datetime.datetime.utcfromtimestamp(record.created)
        msg = textwrap.shorten(f"{emoji} [{date(dt)}] `{record.message}`", width=1990)
        await self.webhook.send(
            msg, username="Gateway Health", avatar_url="https://i.imgur.com/4PnCKB3.png"
        )


async def setup(bot: SkyeBot) -> None:
    cog = Stats(bot)
    await bot.add_cog(cog)
    bot._stats_cog_gateway_handler = handler = GatewayHandler(cog)
    logging.getLogger().addHandler(handler)


async def teardown(bot: SkyeBot) -> None:
    logging.getLogger().removeHandler(bot._stats_cog_gateway_handler)
    del bot._stats_cog_gateway_handler
