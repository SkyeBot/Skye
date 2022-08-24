from __future__ import annotations


from core.bot import SkyeBot

from .ping import ping

from .suggest import Suggest


class utilities(ping, Suggest):
    """Utilites Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(utilities(bot))
