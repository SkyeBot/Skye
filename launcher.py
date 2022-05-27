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
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skyetest") as pool ,SkyeBot(session=session, thino=thino.Client(), pool=pool) as bot:
        await bot.start(os.environ["TEST_TOKEN"])

asyncio.run(main())