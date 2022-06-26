import discord
from discord.ext import commands

# Discord Imports

from typing import Generic

# Regular Imports

from core.bot import SkyeBot, EB


class Interaction(discord.Interaction, Generic[EB]):
    client: EB  # type: ignore


class KnownInteraction(Interaction[EB]):
    guild: discord.Guild  # type: ignore