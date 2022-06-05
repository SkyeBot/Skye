import io
import os
import re
import zlib
import logging

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands


class SphinxObjectFileReader:
   
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


class Docs(commands.Cog, name="Documentation"):
    """RTFM commands"""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

        self.page_types = {
            "discord.py": "https://discordpy.readthedocs.io/en/stable",
            "levelling": "https://discord-ext-levelling.readthedocs.io/en/latest/",
            'master': 'https://discordpy.readthedocs.io/en/latest',
            'python': 'https://docs.python.org/3',
        }

    def finder(self, text, collection, *, key=None, lazy=True):
        suggestions = []
        text = str(text)
        pat = ".*?".join(map(re.escape, text))
        regex = re.compile(pat, flags=re.IGNORECASE)
        for item in collection:
            to_search = key(item) if key else item
            r = regex.search(to_search)
            if r:
                suggestions.append((len(r.group()), r.start(), item))

        def sort_key(tup):
            if key:
                return tup[0], tup[1], key(tup[2])
            return tup

        if lazy:
            return (z for _, _, z in sorted(suggestions, key=sort_key))
        else:
            return [z for _, _, z in sorted(suggestions, key=sort_key)]

    def parse_object_inv(self, stream, url):
    
        result = {}

     
        inv_version = stream.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        stream.readline().rstrip()[11:]
        stream.readline().rstrip()[11:]


        line = stream.readline()
        if "zlib" not in line:
            raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:

                continue

            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            result[f"{prefix}{key}"] = os.path.join(url, location)

        return result

    def transform_rtfm_language_key(self, ctx, prefix):
        if ctx.guild is not None:
            #                             日本語 category
            if ctx.channel.category_id == 490287576670928914:
                return prefix + '-jp'
            #                    d.py unofficial JP   Discord Bot Portal JP
            elif ctx.guild.id in (463986890190749698, 494911447420108820):
                return prefix + '-jp'
        return prefix

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
                async with self.bot.session.get(page + "/objects.inv") as resp:
                    if resp.status != 200:
                        raise RuntimeError(
                            "Cannot build rtfm lookup table, try again later."
                        )

                    stream = SphinxObjectFileReader(await resp.read())
                    cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(self, interaction, key, obj):
        page_types = self.page_types

        if obj is None:
            await interaction.response.send_message(page_types[key])
            return


        if not hasattr(self, "_rtfm_cache"):
            await self.build_rtfm_lookup_table(page_types)

        cache = list(self._rtfm_cache[key].items())

        self.matches = self.finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(title=f"Make sure to read the fucking docs! (hence the name)")
        e.set_footer(text=f'Requested By {interaction.user}', icon_url=f'{interaction.user.avatar.url}')
        e.set_thumbnail(url=interaction.user.avatar.url)
        if len(self.matches) == 0:
            embed = discord.Embed(description=f"**Could not find anything. Sorry.!**")
            embed.set_footer(text=f"Read The Fucking Manual :)", icon_url=interaction.user.avatar.url)



        e.description = "\n".join(f"[`{key}`]({url})" for key, url in self.matches)
        await interaction.response.send_message(embed=e)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("I'm ready!")
    MY_GUILD = discord.Object(id=875423509768204288)
    
    rtfm = app_commands.Group(name="rtfm", description="all RTFM commands")
    

    @rtfm.command(name='master')
    async def rtfm_master(self, interaction: discord.Interaction, *, query:str):
        """Gives you a documentation link for a discord.py entity (master branch)"""
        await self.do_rtfm(interaction, 'master', query)

    @rtfm.command(name="stable")
    async def rtfm_stable(self, interaction: discord.Interaction, query: str):
        """Giveds you a documentation link for a discord.py entity (stable/1.7.3)"""
        await self.do_rtfm(interaction, 'discord.py', query)
    
    @rtfm.command(name='python')
    async def rtfm_py(self, interaction: discord.Interaction, *, query: str):
        """Gives you a documentation link for a python entity """
        key = self.transform_rtfm_language_key(interaction, 'python')
        await self.do_rtfm(interaction, key, query)

