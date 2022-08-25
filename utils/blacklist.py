import discord
import asyncpg

from core.bot import SkyeBot

async def check(bot: SkyeBot,   user):
    """Basic check for blacklisted users"""

    query = """
    SELECT 
        *
    FROM
        blacklist
    WHERE user_id = $1

    """
    

    blacklist = await bot.pool.fetchrow(query, user.id)
    
    if blacklist is None:
        return False
    else:
        return True




    