import inspect
from typing import Union
import discord
from discord.ext import commands


from core.bot import SkyeBot
from utils.context import Context
from roblox import Client
import roblox
from utils import default
from robloxpy import User
import asyncio
from discord import app_commands

class Dropdown(discord.ui.Select):
    def __init__(self, ctx: Union[Context, discord.Interaction], bot: SkyeBot, member):
        self.ctx = ctx
        self.bot = bot
        self.member = member


        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Account Information', description=f'Shows information about: {self.member}', emoji='<:information:777129869862633472>'),
            discord.SelectOption(label='Account Avatar', description=f'Shows the avatar of: {self.member}', emoji='<:tpose:816281552576577536>'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.

        if isinstance(self.ctx, discord.Interaction):
            original = self.ctx.user.id
        else:
            original = self.ctx.author.id

        if interaction.user.id != original:
            pass
        else:
            await interaction.response.defer()
   


        if self.values[0] == "Account Avatar":
            user = await self.bot.roblox.get_user_by_username(self.member, expand=True)

    
            user_thumbnails = await self.bot.roblox.thumbnails.get_user_avatar_thumbnails(
                users=[user],
                type=roblox.thumbnails.AvatarThumbnailType.full_body,
                size=(420, 420)
            )

            if len(user_thumbnails) > 0:
                user_thumbnail = user_thumbnails[0]
                print(user_thumbnail.image_url)



            embed = discord.Embed(description=f"{self.member}'s In-Game Avatar",color=0x3867a8)
            embed.set_image(url=user_thumbnail.image_url)
            await interaction.message.edit(embed=embed, view=DropdownView(interaction,self.bot,self.member))


        if self.values[0] == "Account Information":
            user = await self.bot.roblox.get_user_by_username(self.member, expand=True)
            async with self.bot.session.get(url = f"https://api.roblox.com/users/get-by-username?username={self.member}") as r:
                res = await r.json()
                isOnline = res['IsOnline']

                if isOnline is False:
                    isOnline = "Offline"
                else:
                    isOnline = "Online"

            user_thumbnails = await self.bot.roblox.thumbnails.get_user_avatar_thumbnails(
                users=[user],
                type=roblox.thumbnails.AvatarThumbnailType.full_body,
                size=(420, 420)
            )

            if len(user_thumbnails) > 0:
                user_thumbnail = user_thumbnails[0]


            badges = ', '.join(x.name for x in await user.get_roblox_badges())
            description = user.description

            if len(description) < 1:
                description = "None"

            embed = discord.Embed(description=f"**Info About: [{user.name}](https://www.roblox.com/users/{user.id}/profile)**", color=self.bot.color)

            embed.set_thumbnail(url=user_thumbnail.image_url)
            
            embed.add_field(name="Information", value=f"Display Name: {user.display_name}\nID: {user.id}\nBanned: {user.is_banned}\nStatus: {isOnline}")
            embed.add_field(name="Social", value=f"Followers: {await user.get_follower_count()}\nFollowing: {await user.get_following_count()}\nFriends: {await user.get_friend_count()}\nGroups: {len(await user.get_group_roles())}")
            embed.add_field(name="Creation Date", value=f"{default.date(user.created, ago=True)}", inline=False)
            embed.add_field(name="Badges", value=f"{badges}", inline=False)
            embed.add_field(name="Description", value=f"**{description!r}**", inline=False)

            await interaction.message.edit(embed=embed,view=DropdownView(interaction,self.bot,self.member))

class DropdownView(discord.ui.View):
    def __init__(self, ctx: Union[Context, discord.Interaction],bot: SkyeBot, member=None):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.member = member
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(self.ctx,self.bot,self.member))



    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if isinstance(self.ctx, discord.Interaction):
            user = self.ctx.user.id
        else:
            user = self.ctx.author.id

        if interaction.user and interaction.user.id == user:
            return True
        await interaction.response.defer()
        await interaction.followup.send(f"You cant use this as you're not the command invoker, only the author (<@{user}>) Can Do This!", ephemeral=True)
        return False
        


class roblx(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    @app_commands.command()
    async def robloxui(self, interaction: discord.Interaction, username: str):
        """Get info about a roblox user"""
        
        async with self.bot.session.get(f"https://api.roblox.com/users/get-by-username?username={username}") as r:
            res = await r.json()
            isOnline = res['IsOnline']

            if isOnline is False:
                isOnline = "Offline"
            else:
                isOnline = "Online"
        
        user = await self.bot.roblox.get_user_by_username(username, expand=True)

        badges = ', '.join(x.name for x in await user.get_roblox_badges())
        
        user_thumbnails = await self.bot.roblox.thumbnails.get_user_avatar_thumbnails(
            users=[user],
            type=roblox.thumbnails.AvatarThumbnailType.full_body,
            size=(420, 420)
        )

        if len(user_thumbnails) > 0:
            user_thumbnail = user_thumbnails[0]

        description = user.description

        if len(description) < 1:
            description = "None"


        embed = discord.Embed(description=f"**Info About: [{user.name}](https://www.roblox.com/users/{user.id}/profile)**", color=self.bot.color)

        embed.set_thumbnail(url=user_thumbnail.image_url)
        
        embed.add_field(name="Information", value=f"Display Name: {user.display_name}\nID: {user.id}\nBanned: {user.is_banned}\nStatus: {isOnline}")
        embed.add_field(name="Social", value=f"Followers: {await user.get_follower_count()}\nFollowing: {await user.get_following_count()}\nFriends: {await user.get_friend_count()}\nGroups: {len(await user.get_group_roles())}")
        embed.add_field(name="Creation Date", value=f"{default.date(user.created, ago=True)}", inline=False)
        embed.add_field(name="Badges", value=f"{badges}", inline=False)
        embed.add_field(name="Description", value=f"**{description!r}**", inline=False)


        view = DropdownView(interaction,self.bot,user.name)

        await interaction.response.send_message(embed=embed, view=view)
