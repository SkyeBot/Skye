
from .osu_cog import osu


class osu_cog(osu):
    """All osu commands"""


async def setup(bot):
    await bot.add_cog(osu_cog(bot))
