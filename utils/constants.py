import typing
import discord

from collections import namedtuple

TOP_GG = '<:topgg:918280202398875758>'
BOTS_GG = '<:botsgg:895395445608697967>'
GITHUB = '<:github:895395664383598633>'
INVITE = '<:CreateInvite:928388724746780723>'
WEBSITE = '<:open_site:895395700249075813>'

VALID_EDIT_KWARGS: typing.Dict[str, typing.Any] = {
    'content': None,
    'embed': None,
    'attachments': [],
    'delete_after': None,
    'allowed_mentions': None,
    'view': None,
}