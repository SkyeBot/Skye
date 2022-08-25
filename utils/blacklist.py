
from core.bot import SkyeBot


async def check(bot: SkyeBot, user):
    """Basic check for blacklisted users"""
    query = """
    SELECT 
        *
    FROM
        blacklist
    WHERE user_id = $1

    """

    blacklist = await bot.pool.fetchrow(query, user.id)
    return blacklist is not None
