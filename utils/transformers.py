import discord
from discord import app_commands

import itertools
from typing import Any, Generic, List, Tuple, Union, TYPE_CHECKING
from fuzzywuzzy import process

from core.bot import T, SkyeBot
from utils import *
from utils.subclasses import KnownInteraction


class AdaptiveTransformerProxy(Generic[T]):
    def __init__(self, transformed: List[str]) -> None:
        self.transformed: List[str] = transformed

    def name_handler(self, obj: Any) -> str:
        if isinstance(obj, discord.TextChannel):
            name = f"#{obj.name}"
        elif isinstance(obj, (discord.Role, discord.User, discord.Member)):
            name = f"@{obj.name}"
        else:
            name = obj.name
        return name

    def is_bot_role(self, obj: Any) -> bool:
        if isinstance(obj, discord.Role):
            if obj.managed:
                return True
        return False

    def combined(self, guild: discord.Guild) -> List[Any]:
        return [getattr(guild, attr) for attr in self.transformed]

    async def autocomplete(
        self, itr: KnownInteraction[SkyeBot], value: Union[int, float, str]
    ) -> List[app_commands.Choice[Union[int, float, str]]]:
        _combined = self.combined(itr.guild)
        combined = list(itertools.chain(*_combined))
        try:
            combined.remove(itr.guild.default_role)
        except ValueError:
            pass

        results: List[Tuple[str, int]] = await itr.client.wrap(process.extract, value, [o.name for o in combined], limit=25)  # type: ignore
        clean: List[str] = [ob[0] for ob in results]

        return [
            app_commands.Choice(name=self.name_handler(ob), value=str(ob.id))
            for ob in combined
            if ob.name in clean and not self.is_bot_role(ob)
        ]

    async def transform(self, itr: KnownInteraction[SkyeBot], value: str) -> T:
        if not value.isdigit():
            raise Exception("Something Borked!")

        ob_id = int(value)
        _combined = self.combined(itr.guild)
        combined = list(itertools.chain(*_combined))
        target = discord.utils.get(combined, id=ob_id)
        if not target:
            raise Exception("Something Borked!")

        return target


class ProxyTransformer(app_commands.Transformer, Generic[T]):
    if TYPE_CHECKING:
        PROXY: AdaptiveTransformerProxy[T]

    @classmethod
    async def transform(cls, itr: KnownInteraction[SkyeBot], value: Any):
        return await cls.PROXY.transform(itr, value)

    @classmethod
    async def autocomplete(cls, itr: KnownInteraction[SkyeBot], value: Any) -> Any:  # type: ignore
        return await cls.PROXY.autocomplete(itr, value)


class RoleChannelTransformer(
    ProxyTransformer[Union[discord.TextChannel, discord.Role]]
):
    PROXY: AdaptiveTransformerProxy[
        Union[discord.TextChannel, discord.Role]
    ] = AdaptiveTransformerProxy(["text_channels", "roles"])


class CategoryChannelTransformer(ProxyTransformer[discord.CategoryChannel]):
    PROXY: AdaptiveTransformerProxy[discord.CategoryChannel] = AdaptiveTransformerProxy(
        ["categories"]
    )


class NotBotRoleTransformer(ProxyTransformer[discord.Role]):
    PROXY: AdaptiveTransformerProxy[discord.Role] = AdaptiveTransformerProxy(["roles"])