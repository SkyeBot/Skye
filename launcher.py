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
dotenv.load_dotenv()





async def main():
    async with aiohttp.ClientSession() as session, asyncpraw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'], client_secret=os.environ['REDDIT_CLIENT_SECRET'], user_agent=os.environ['REDDIT_USER_AGENT']) as reddit ,asyncpg.create_pool(os.environ["POSTGRES_URI"]) as pool,SkyeBot(session=session, thino_session=thino.Client(), pool=pool, osu= Osu(client_id = os.environ['OSU_CLIENT_ID'], client_secret=os.environ['OSU_CLIENT_SECRET'], session=session), reddit=reddit) as bot:
        


        async def blacklist_check(interaction):
            if interaction.user.id == 894794517079793704:
                return True

            if await blacklist.check(bot, interaction.user):
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="You are blacklisted from using this bot!", value="If you think this is a mistake, go ahead and make an appeal at discord.gg/fp9HwavUQz")
                await interaction.response.send_message(embed=embed)
                return False
            else:
                return True
        
        bot.tree.interaction_check = blacklist_check
        await bot.start(os.environ["TOKEN"])

    
if __name__ == "__main__":
    asyncio.run(main())