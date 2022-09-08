import discord
import asyncio
import aiohttp
import dotenv
import os
import thino
from core.bot import SkyeBot
import asyncpg
from utils import blacklist
from utils.osu_utils import Osu
import asyncpraw
import asyncio

dotenv.load_dotenv() 
discord.utils.setup_logging()


async def main():
    async with aiohttp.ClientSession() as session, asyncpraw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'], client_secret=os.environ['REDDIT_CLIENT_SECRET'], user_agent=os.environ['REDDIT_USER_AGENT']) as reddit ,asyncpg.create_pool(os.environ["POSTGRES_URI"]) as pool,SkyeBot(session=session, thino_session=thino.Client(), pool=pool, osu= Osu(client_id = os.environ['OSU_CLIENT_ID'], client_secret=os.environ['OSU_CLIENT_SECRET'], session=session), reddit=reddit, top_gg=os.environ['TOPGG_AUTH']) as bot:
        async def blacklist_check(interaction: discord.Interaction  ):
            if interaction.user.id in bot.owner_ids:
                return True

            if await blacklist.check(bot, interaction.user):
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="You are blacklisted from using this bot!", value="If you think this is a mistake, go ahead and make an appeal at discord.gg/fp9HwavUQz")
                await interaction.response.send_message(embed=embed)
                return False
            else:
                return True

        exts = ["jishaku"] + [
            f"cogs.{ext if not ext.endswith('.py') else ext[:-3]}"
            for ext in os.listdir("cogs")
            if not ext.startswith("_")
        ]
        for ext in exts:
            await bot.load_extension(ext)

        
        

        bot.tree.interaction_check = blacklist_check
        await bot.start(os.environ["TOKEN"])
    

if __name__ == "__main__":
    asyncio.run(main())