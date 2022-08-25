

from .rtfm import Docs


class rtfm(Docs):
    """RTFM cog"""


async def setup(bot):
    await bot.add_cog(rtfm(bot))
