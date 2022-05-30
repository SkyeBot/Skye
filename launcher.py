import discord
import asyncio
import aiohttp
import dotenv
import os
from discord.ext import commands
import thino
from core.bot import SkyeBot
import asyncpg

dotenv.load_dotenv()

async def main():
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(os.environ["POSTGRES_URI"]) as pool, SkyeBot(session=session, thino_session=thino.Client(), pool=pool) as bot:
        await bot.start(os.environ["TOKEN"])

asyncio.run(main())