from __future__ import annotations

from typing import (
    Type,
    Tuple,
    TypeVar,
    Generic,
)

import discord
from discord.ext import commands
from discord.ext.commands import FlagConverter

from .context import Context

BET = TypeVar("BET", bound="discord.guild.BanEntry")
FCT = TypeVar("FCT", bound="FlagConverter")
T = TypeVar("T")


__all__: Tuple[str, ...] = ("UntilFlag",)


class UntilFlag(Generic[FCT]):
    """A converter that will convert until a flag is reached.
    **Example**
    .. code-block:: python3
        from typing import Optional
        from discord.ext import commands
        class SendFlags(commands.FlagConverter, prefix='--', delimiter=' '):
            channel: Optional[discord.TextChannel] = None
            reply: Optional[discord.Message] = None
        @commands.command()
        async def send(self, ctx: DuckContext, *, text: UntilFlag[SendFlags]):
            '''Send a message to a channel.'''
            channel = text.flags.channel or ctx.channel
            await channel.send(text.value)
    Attributes
    ----------
    value: :class:`str`
        The value of the converter.
    flags: :class:`FlagConverter`
        The resolved flags.
    """

    def __init__(self, value: str, flags: FCT) -> None:
        self.value = value
        self.flags = flags
        self._regex = self.flags.__commands_flag_regex__  # type: ignore
        self._start = self.flags.__commands_flag_prefix__  # type: ignore

    def __class_getitem__(cls, item: Type[FlagConverter]) -> UntilFlag:
        return cls(value="...", flags=item())

    def validate_value(self, argument: str) -> bool:
        """Used to validate the parsed value without flags.
        Defaults to checking if the argument is a valid string.
        If overridden, this method should return a boolean or raise an error.
        Can be a coroutine
        Parameters
        ----------
        argument: :class:`str`
            The argument to validate.
        Returns
        -------
        :class:`str`
            Whether or not the argument is valid.
        Raises
        ------
        :class:`commands.BadArgument`
            No value was given
        """
        stripped = argument.strip()
        if not stripped or stripped.startswith(self._start):
            raise commands.BadArgument(f"No body has been specified before the flags.")
        return True

    async def convert(self, ctx: Context, argument: str) -> UntilFlag:
        """|coro|
        The main convert method of the converter. This will take the given flag converter and
        use it to delimit the flags from the value.
        Parameters
        ----------
        ctx: :class:`DuckContext`
            The context of the command.
        argument: :class:`str`
            The argument to convert.
        Returns
        -------
        :class:`UntilFlag`
            The converted argument.
        """
        value = self._regex.split(argument, maxsplit=1)[0]
        if not await discord.utils.maybe_coroutine(self.validate_value, argument):
            raise commands.BadArgument("Failed to validate argument preceding flags.")
        flags = await self.flags.convert(ctx, argument=argument[len(value) :])
        return UntilFlag(value=value, flags=flags)
