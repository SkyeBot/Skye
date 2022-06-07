from __future__ import annotations

from io import BytesIO
import discord
from discord.ext import commands

from datetime import datetime

from typing import Union, List

from utils.context import Context

from core.bot import SkyeBot

from PIL import Image

class TestView(discord.ui.View):
    def __init__(self, ctx: Union[Context, discord.Interaction], member: discord.Member):
        self.member = member
        self.ctx = ctx

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.defer()
        return False

class Yoink(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        members: List[discord.Member] = await guild.chunk(cache=True) if not guild.chunked else guild.members

        for member in members:
            if member.mutual_guilds or member == member.guild.me:
                continue
            
            avatar = await member.display_avatar.read()

            await self.bot.pool.execute("""
            INSERT INTO avatars (user_id, time_changed, avatar)
            VALUES ($1, $2, $3)
            """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.mutual_guilds:
            return
        
        avatar = await member.display_avatar.read()
        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, member.id, discord.utils.utcnow(), avatar)

    @commands.Cog.listener()
    async def on_user_avatar_update(self, _: discord.User, after: discord.User):
        avatar = await after.display_avatar.read()

        await self.bot.pool.execute("""
        INSERT INTO avatars (user_id, time_changed, avatar)
        VALUES ($1, $2, $3)
        """, after.id, discord.utils.utcnow(), avatar)


    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if before.avatar != after.avatar:
            self.bot.dispatch("user_avatar_update", before, after)
    
    @commands.command()
    async def pil_test(self, ctx: Context):
        async with self.bot.session.get(ctx.author.display_avatar.url) as response:
            avatar_bytes = await response.read()

        with Image.open(BytesIO(avatar_bytes)) as my_image:
            user = await self.bot.fetch_user(ctx.author.id)
            
            output_buffer = BytesIO()

            image = Image.new('RGBA',(1000, 500))
            
            my_image = my_image.resize((200, 200))

            image_x, image_y = image.size

            image.paste(await user.banner.read(), (int(500), int(1000)))

            image.paste(my_image, (int(image_x / 2), int(image_y / 4)))

            

            image.save(output_buffer, "png")  # or whatever format
            output_buffer.seek(0)

        await ctx.send(file=discord.File(fp=output_buffer, filename="my_file.png"))


async def setup(bot):
    await bot.add_cog(Yoink(bot))