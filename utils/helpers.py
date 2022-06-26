from typing import Union, Iterable, Any, Dict, List, Optional

import discord

# Regular Imports

from core.bot import SkyeBot

class HexType:
    def __init__(self, x):
        if isinstance(x, str):
            self.val = int(x, 16)
        elif isinstance(x, int):
            self.val = int(str(x), 16)

    def __str__(self):
        return hex(self.val)


def embed_builder(
    *,
    title: str = None,
    description: str = None,
    colour: HexType =  0xB00020,
    timestamp: bool = None,
    author: Union[list, str] = None,
    footer: Union[list, str] = None,
    thumbnail: str = None,
    image: str = None,
    fields: list = None,
    url: str = None,
):
    embed = discord.Embed()
    if title:
        embed.title = title
    if description:
        embed.description = description
    if timestamp:
        embed.timestamp = timestamp
    embed.colour = colour
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if url:
        embed.url = url
    if author:
        if isinstance(author, list):
            embed.set_author(icon_url=author[0], name=author[1])
        elif isinstance(author, str):
            embed.set_author(name=author)
    if footer:
        if isinstance(footer, list):
            embed.set_footer(icon_url=footer[0], text=footer[1])
        elif isinstance(footer, str):
            embed.set_footer(text=footer)
    if fields:
        for field in fields:
            try:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
            except IndexError:
                embed.add_field(name=field[0], value=field[1])
    return embed