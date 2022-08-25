"""
I forgot what to write to abide with the Mozilla Public License That duckbot-hideout-manager-bot uses but 
any code taken from there goes to credit of LeoCx1000 as they're the owner of any code ive might have taken


"""


from __future__ import annotations
import io
from core.bot import SkyeBot
from utils import UntilFlag
import io

import time
from tabulate import tabulate
from typing import List

from import_expression import eval
from discord import File
from discord.ext.commands import FlagConverter, Flag, Converter
from discord.ext import commands
from utils import Context


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, _, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        return f"{v} {plural}" if abs(v) != 1 else f"{v} {singular}"


def cleanup_code(content: str):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    # remove `foo`
    return content.strip("` \n")


class EvaluatedArg(Converter):
    async def convert(self, ctx: Context, argument: str) -> str:
        return eval(cleanup_code(argument), {"bot": ctx.bot, "ctx": ctx})


class SqlCommandFlags(FlagConverter, prefix="--", delimiter=" ", case_insensitive=True):
    args: List[str] = Flag(name="argument", aliases=["a", "arg"], annotation=List[EvaluatedArg], default=[])  # type: ignore


class SQLCommands(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx: Context, *, query: UntilFlag[SqlCommandFlags]):
        """|coro|
        Executes an SQL query
        Parameters
        ----------
        query: str
            The query to execute.
        """
        query.value = cleanup_code(query.value)
        is_multistatement = query.value.count(";") > 1
        strategy = ctx.bot.pool.execute if is_multistatement else ctx.bot.pool.fetch
        try:
            start = time.perf_counter()
            results = await strategy(query.value, *query.flags.args)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception as e:
            return await ctx.send(f"{type(e).__name__}: {e}")
        rows = len(results)
        if rows == 0 or isinstance(results, str):
            result = "Query returned o rows\n" if rows == 0 else str(results)
            await ctx.send(f"{result}*Ran in {dt:.2f}ms*")
        else:
            try:
                table = tabulate(results, headers="keys", tablefmt="orgtbl")
                fmt = f"```\n{table}\n```*Returned {plural(rows):row} in {dt:.2f}ms :D!*"
                if len(fmt) > 2000:
                    fp = io.BytesIO(table.encode("utf-8"))
                    await ctx.send(f"*Too many results...\nReturned {plural(rows):row} in {dt:.2f}ms*", file=File(fp, "output.txt"))

                else:
                    await ctx.send(fmt)
            except Exception as e:
                return await ctx.send(f"{type(e).__name__}: ```py\n{e}```")
