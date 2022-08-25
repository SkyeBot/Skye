

from .logs import Logging


class Logs(Logging):
    """Logs Cog"""


async def setup(bot):
    await bot.add_cog(Logs(bot))
