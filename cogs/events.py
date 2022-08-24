from core.bot import SkyeBot
from utils.base_cog import base_cog


class Events(base_cog):
    pass


async def setup(bot: SkyeBot):
    await bot.add_cog(Events(bot))
