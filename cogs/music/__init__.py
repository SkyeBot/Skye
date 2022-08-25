
from .music import Music

from core.bot import SkyeBot


class Music(Music):
    """Music Related Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(Music(bot))
