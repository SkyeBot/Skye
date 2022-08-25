


# Local Imports
from core.bot import SkyeBot

from .mods import Mods
from .mute import Mute
from .warn import Warns


class Moderation(Mods, Mute, Warns):
    """Moderation Cog"""


async def setup(bot: SkyeBot):
    await bot.add_cog(Moderation(bot))
