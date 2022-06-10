import discord
from discord.ext import commands


from core.bot import SkyeBot
from utils.context import Context
from roblox import Client
import roblox
from utils import default



class roblx(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot


    @commands.command()
    async def robloxui(self, ctx: Context, username: str):
        
        async with ctx.session.get(url = f"https://api.roblox.com/users/get-by-username?username={username}") as r:
            res = await r.json()
            isOnline = res['IsOnline']
        
        user = await self.bot.roblox.get_user_by_username(username, expand=True)

        friends = ', '.join(x.name for x in await user.get_friends())

        badges = ', '.join(x.name for x in await user.get_roblox_badges())
        
        user_thumbnails = await self.bot.roblox.thumbnails.get_user_avatar_thumbnails(
            users=[user],
            type=roblox.thumbnails.AvatarThumbnailType.full_body,
            size=(420, 420)
        )

        if len(user_thumbnails) > 0:
            user_thumbnail = user_thumbnails[0]
            print(user_thumbnail.image_url)

        description = user.description

        if len(description) < 1:
            description = "None"

        embed = discord.Embed(description=f"**Info About: [{user.name}](https://www.roblox.com/users/{user.id}/profile)**")

        embed.set_thumbnail(url=user_thumbnail.image_url)
        
        embed.add_field(name="Information", value=f"Display Name: {user.display_name}\nID: {user.id}\nBanned: {user.is_banned}\nIs Online: {isOnline}")
        embed.add_field(name="Social", value=f"Followers: {await user.get_follower_count()}\nFollowing: {await user.get_following_count()}\nFriends: {await user.get_friend_count()}\nGroups: {len(await user.get_group_roles())}")
        embed.add_field(name="Creation Date", value=f"{default.date(user.created, ago=True)}", inline=False)
        embed.add_field(name="Badges", value=f"{badges}", inline=False)
        embed.add_field(name="Description", value=f"**{description!r}**", inline=False)


        await ctx.send(embed=embed)