
from .welcomer import welcomer


class Welcomer(welcomer):
    """Welcomer Cog"""


async def setup(bot):
    await bot.add_cog(Welcomer(bot))
