from __future__ import annotations
from io import BytesIO
from typing import Dict, List, Optional, Union
import asyncpg

import discord
from discord.ext import commands
from discord import app_commands

from core.bot import SkyeBot
from utils.context import Context


class TagAddModal(discord.ui.Modal):
    def __init__(self, client: SkyeBot):
        self.bot = client
        super().__init__(title="Add Tag")
    
    name = discord.ui.TextInput(
                label="Name", placeholder="The name of your tag", style=discord.TextStyle.short
    )
    content = discord.ui.TextInput(
            label="Content", placeholder="The content of your tag", style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value.strip().lower() # type: ignore
        content = self.content.value.strip() # type: ignore

        if name.isdigit(): # type: ignore
            return await interaction.response.send_message("Invalid tag name", ephemeral=True)

        content = discord.utils.escape_mentions(content)

        query = "SELECT createTag($1, $2, $3, $4)"
        try:
            await self.bot.pool.execute(query, name, content, interaction.user.id, interaction.guild.id) # type: ignore
        except asyncpg.UniqueViolationError:
            return await interaction.response.send_message("Tag already exists", ephemeral=True)

        return await interaction.response.send_message(f"Tag: {name} succesfully created!", ephemeral=True)

class EditModal(discord.ui.Modal):
    def __init__(self, tag_id: int, bot: SkyeBot):
        self.tag = tag_id
        self.bot = bot

        super().__init__(title="Tag Edit Modal")

    content = discord.ui.TextInput(label="Edit Content", placeholder="Edit The Content Of Your Tag", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        query = """
        UPDATE tags_new
        SET
            content = $1
        WHERE
            id = $2
        

        """

        await self.bot.pool.execute(query, self.content.value, self.tag)
        tag = """
        SELECT
            tl.name
        FROM tag_lookup tl
        INNER JOIN tags_new tn ON tn.name = tl.name
        WHERE tl.tagId = $1
        """

        lookup = await self.bot.pool.fetchval(tag, self.tag)
        tag_name = lookup
        await interaction.response.send_message(f"Updated Tag: **{tag_name}** Succesfully", ephemeral=True)


class Tags(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        self.options: Dict[str, Union[int, float, str]]

    tags = app_commands.Group(name="tags", description="Tag commands")
    
    @tags.command()
    async def add(self, interaction: discord.Interaction, name: Optional[str], content: Optional[str]):

        """Adds a tag with specified name and content"""

        if name is None:
            return await interaction.response.send_modal(TagAddModal(self.bot))
            
        name = name.strip()
        
        
        if not name or 3 > len(name) > 32 or name.isdigit():
            return await interaction.response.send_message("Invalid tag name", ephemeral=True)


        content = discord.utils.escape_mentions(content.strip())
        if len(content) > 2000:
            return await interaction.response.send_message("Content must be 2000 characters or less")

        try:
            await self.bot.pool.execute(
                "SELECT createTag($1, $2, $3)",
                name, content, interaction.user.id
            )
        except asyncpg.UniqueViolationError:
            await interaction.response.send_message("Tag already exists", ephemeral=True)
        else:
            await interaction.response.send_message(f"Created tag {name}", ephemeral=True)

<<<<<<< HEAD
=======
    @commands.command()
    async def osu_showcase(self, ctx: Context):
        embed = discord.Embed(title="Osu Command Showcase", description="I made an osu command that shows info about a osu profile")
        embed.set_author(name="Made By Sawsha#0598", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
>>>>>>> c57e8ae748fd320ceaefb4a0c756110dbe396dc1

    async def tags_autocomplete(self, interaction: discord.Interaction, current: Dict[str, Union[int, float, str]]) -> List[app_commands.Choice[str]]:
        if current == '':
            query = """
            SELECT
                name
            FROM
                tag_lookup
            WHERE
             guildid = $1

            """
            tags = await self.bot.pool.fetch(query, interaction.guild.id)


            return [
                app_commands.Choice(name=n["name"], value=n["name"])
                for n in tags 
            ]
        
        query = """
        SELECT
            name
        FROM
            tag_lookup
        WHERE
            SIMILARITY(name, $1) > 0.10 AND guildid = $2
        ORDER BY
            similarity(name, $1) 
            DESC
            LIMIT 10
        """

        tags = await self.bot.pool.fetch(query, current, interaction.guild.id)


        return [
            app_commands.Choice(name=n["name"], value=n["name"])
             for n in tags if current.lower()
        ]


    

    @tags.command()
    @app_commands.autocomplete(tag=tags_autocomplete)
    async def info(self, interaction: discord.Interaction, tag: str):
        """Gets info about specified tag"""
        name = tag.strip().lower()
        query = """
        SELECT
            tl.tagId, tl.isAlias, tn.name, tn.owner, tn.uses, tn.created
        FROM tag_lookup tl
        INNER JOIN tags_new tn ON tn.id = tl.tagId
        WHERE tl.name = $1
        """

        lookup = await self.bot.pool.fetchrow(query, name)
        if not lookup:
            return await interaction.response.send_message("Tag not found", ephemeral=True)

        tag_id, is_alias, tag_name, owner_id, uses, created_timestamp = lookup
        e = discord.Embed()

        if is_alias:
            e.title = f"Tag {name} -> {tag_name}"
        else:
            e.title = f"Tag {tag_name}"

        owner = self.bot.get_user(owner_id)
        if owner:
            e.set_author(name=str(owner), icon_url=owner.display_avatar.url)

        e.description = \
            f"ID: {tag_id}\n" \
            f"Owned by <@{owner_id}> ({owner or 'Owner not found'} {(owner and owner.id) or ''})\n" \
            f"Used {uses} time{'s' if uses != 1 else ''}\n" \
            f"Created <t:{round(created_timestamp.timestamp())}:F>\n"

        await interaction.response.send_message(embed=e)

    @tags.command()
    @app_commands.autocomplete(tag=tags_autocomplete)
    async def alias(self, interaction: discord.Interaction, tag: str, alias: str):
        """Creates an alias for an tag"""

        alias = alias.strip().lower()
        if not alias or len(alias) > 32 or alias.isdigit():
            return await interaction.response.send_message("Invalid alias name", ephemeral=True)

        try:
            resp = await self.bot.pool.fetchrow("SELECT createAlias($1, $2)", tag, alias)
            await interaction.response.send_message(resp['createalias'])
        except asyncpg.UniqueViolationError:
            await interaction.response.send_message("A tag/alias with that name already exists")
        

    @tags.command()
    @app_commands.autocomplete(name=tags_autocomplete)
    async def edit(self, interaction: discord.Interaction, name: str, content: Optional[str]=None):

        """Allows user to edit a specified tag"""

        name = name.strip().lower()
        query = """
                SELECT
                    tl.tagId, tn.owner
                FROM tag_lookup tl
                INNER JOIN tags_new tn ON tn.id = tl.tagId
                WHERE tl.name = $1
                """

        lookup = await self.bot.pool.fetchrow(query, name)
        if not lookup:
            return await interaction.response.send_message("Tag not found", ephemeral=True)

        if lookup['owner'] != interaction.user.id:
            return await interaction.response.send_message("You do not own this tag", ephemeral=True)

        if not content:
            return await interaction.response.send_modal(EditModal(lookup['tagid'], self.bot))

        query = """
        UPDATE tags_new
        SET
            content = $1
        WHERE
            id = $2
        """
        await self.bot.pool.execute(query, self.content, lookup['tagid']) # type: ignore
        await interaction.response.send_message("Updated tag", ephemeral=True)



    @app_commands.command()
    @app_commands.autocomplete(name=tags_autocomplete)
    async def tag(self, interaction: discord.Interaction, name: str):
        """Shows specified tag"""

        data = await self.bot.pool.fetchrow("SELECT findTag($1, $2)", name, interaction.guild.id)
        
        print(data)

        if not data['findtag']:
            return await interaction.response.send_message("That tag does not exist", ephemeral=True)

        await interaction.response.send_message(data['findtag'][1])
