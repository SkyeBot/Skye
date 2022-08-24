
from .nsfw import NSFW

from core.bot import SkyeBot


class nsfw(NSFW):
    """Admin Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(nsfw(bot))
