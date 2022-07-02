import discord
import asyncio
import aiohttp
import dotenv
import os
import thino
from core.bot import SkyeBot
import asyncpg
from utils import blacklist
dotenv.load_dotenv()





async def main():
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(os.environ["POSTGRES_URI"]) as pool, SkyeBot(session=session, thino_session=thino.Client(), pool=pool) as bot:
        
        @bot.check
        async def blacklist_check(interaction):
            if interaction.user.id == 894794517079793704:
                return True

            if await blacklist.check(bot, interaction.user):
                

                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="You are blacklisted.", value="You have been blacklisted and cannot use this bot.")
                await interaction.response.send_message(embed=embed)
                return False
            else:
                return True

        await bot.start(os.environ["TOKEN"])

    
if __name__ == "__main__":
    asyncio.run(main())