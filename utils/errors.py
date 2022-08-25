import datetime
import discord
from discord.ext.commands import CommandError, CheckFailure
from typing import (
    Tuple,
)


class cooldown_unum(discord.Enum):
    WORK = 0
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3


class BotExceptions(discord.ClientException):
    """The base exception class. All other exceptions should inherit from this."""

    __slots__: Tuple[str, ...] = ()


class BotCommandError(CommandError, BotExceptions):
    """The base exception class for all command errors."""

    __slots__: Tuple[str, ...] = ()


class SilentCommandError(BotCommandError):
    """
    This exception will be purposely ignored by the error handler
    and will not be logged. Handy for stopping something that can't
    be stopped with a simple ``return`` statement.
    """

    __slots__: Tuple[str, ...] = ()


class NoEmojisFound(CheckFailure):
    pass


class HigherRole(CheckFailure):
    pass


class NoQuotedMessage(CheckFailure):
    pass


class WaitForCancelled(CheckFailure):
    pass


class UserBlacklisted(CheckFailure):
    pass


class ChannelBlacklisted(CheckFailure):
    pass


class DisabledCommand(CheckFailure):
    pass


class BotUnderMaintenance(CheckFailure):
    pass


class EconomyOnCooldown(CheckFailure):
    def __init__(self, cooldown_type: cooldown_unum, next_run: datetime.datetime):
        self.cooldown_type = cooldown_type
        self.next_run = next_run


class BadHttpRequest(BotCommandError):
    """Something went wrong while handing your HTTP request"""



class UserError(BotCommandError):
    def __init__(self, error: str):
        super().__init__(error)
