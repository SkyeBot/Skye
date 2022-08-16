from typing import Optional, Union
import discord
from discord.ext import commands
from discord import app_commands
from core.bot import SkyeBot
from utils.context import Context
from utils.base_cog import base_cog
import re
from utils import default, osu_errors
from utils.osu_utils import Beatmap, User



class UserSelect(discord.ui.Select):
    def __init__(self, ctx: Union[discord.Interaction, Context],user: User):
        self.user = user
        self.ctx = ctx
        options = [
            discord.SelectOption(label='Beatmaps', value="bea",description=f"Beatmaps on {self.user.username}'s plays/has"),
            discord.SelectOption(label='Account Avatar', description=f'Shows the avatar of: {self.user.username}'),
            discord.SelectOption(label='Info', description=f'Info about: {self.user.username}'),
            discord.SelectOption(label="Statistics", description=f"Statistics about {self.user.username}")
        ]

        super().__init__(min_values=1, max_values=1, options=options, custom_id="OsuSelectID")

    async def callback(self, interaction: discord.Interaction):
        if  isinstance(self.ctx, discord.Interaction):
            original = self.ctx.user.id
        else:
            original = self.ctx.author.id

        if interaction.user.id != original:
            pass
      
        await interaction.response.defer()
   
        if self.values[0] == "Account Avatar":
            embed = discord.Embed()
            avatar_url = self.user.avatar_url

            embed.title = f"{self.user.username}'s Osu avatar"
            embed.set_image(url=avatar_url)

            await interaction.message.edit(embed=embed)

        if self.values[0] == "Statistics":
            embed = discord.Embed(title=f"{self.user.username}'s Statistics")
            max_combo = self.user.max_combo
            play_style = ', '.join(self.user.playstyle) if type(self.user.playstyle) is list else f"{self.user.username} has no playstyles selected"
            embed.add_field(name="Total Statistics", value=f"Total Hits: {self.user.total_hits}\nTotal Score: {self.user.total_score}\nMaximum Combo: {max_combo}\nPlay Count: {self.user.play_count}", inline=True)
            embed.add_field(name="Play Styles", value=f"Play Styles: {play_style}\nFavorite Play Mode: {self.user.playmode}", inline=True)
            await interaction.message.edit(embed=embed)    

        if self.values[0] == "bea":
            embed = discord.Embed()
            fav = await interaction.client.osu.fetch_user_beatmaps(self.user.id, "favourite", 5)
            favorite_beatmaps = [Beatmap(a) for a in fav]
            embed.title = f"{self.user.username}'s favourite beatmaps"
            embed.add_field(name="Favorite Beatmaps", value='\n'.join(f"{beatmap.title} - {beatmap.artist}" for beatmap in favorite_beatmaps), inline=True)

            await interaction.message.edit(embed=embed)

        if self.values[0] == "Info":
            embed = discord.Embed()
            view = DropdownView(interaction, self.user)
            

            embed.description = f"**{self.user.country_emoji} | Profile for [{self.user.username}](https://osu.ppy.sh/users/{self.user.id})**\n\n▹ **Bancho Rank**: #{self.user.global_rank} ({self.user.country_code}#{self.user.country_rank})\n▹ **Join Date**: {self.user.joined_at}\n▹ **PP**: {self.user.pp} **Acc**: {self.user.accuracy}%\n▹ **Ranks**: {self.user.ranks}\n▹ **Profile Order**: \n** ​ ​ ​ ​ ​ ​ ​ ​  - {self.user.profile_order}**"
            embed.set_thumbnail(url=self.user.avatar_url)
            await interaction.message.edit(embed=embed, view=view)

class DropdownView(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, user: User):
        super().__init__()
        self.ctx = ctx
        self.user = user
        # Adds the dropdown to our view object.
        self.add_item(UserSelect(self.ctx,self.user))
    

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        
        await self.ctx.edit_original_message(view=self)

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



class osu(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
    osu = app_commands.Group(name="osu", description="All osu commands")
    set = app_commands.Group(name="set", description="allows you to set various things for osu", parent=osu)

    @osu.command()
    async def user(self, interaction: discord.Interaction, username: Optional[str]):
        """Gets info on osu account"""

        try:
            user_query = await self.bot.pool.fetchrow("SELECT osu_username FROM osu_user WHERE user_id = $1", interaction.user.id) 
            
            if user_query is None and username is None:
                user = await self.bot.osu.fetch_user(interaction.user.display_name)
            elif user_query is not None and username is None:
                user = await self.bot.osu.fetch_user(user_query.get("osu_username"))
            else:
                user = await self.bot.osu.fetch_user(username)

            
            self.bot.logger.info(user.username)
            self.bot.logger.info(user.avatar_url)
            view = DropdownView(interaction, user)
        
        
            embed = discord.Embed(description=f"**{user.country_emoji} | Profile for [{user.username}](https://osu.ppy.sh/users/{user.id})**\n\n▹ **Bancho Rank**: #{user.global_rank} ({user.country_code}#{user.country_rank})\n▹ **Join Date**: {user.joined_at}\n▹ **PP**: {user.pp} **Acc**: {user.accuracy}%\n▹ **Ranks**: {user.ranks}\n▹ **Profile Order**: \n** ​ ​ ​ ​ ​ ​ ​ ​  - {user.profile_order}**")
            embed.set_thumbnail(url=user.avatar_url)
            await interaction.response.send_message(embed=embed, view=view)
            
        except osu_errors.NoUserFound:
            await interaction.response.send_message("No User Was Found Sadly!")

    @set.command()
    async def user(self, interaction: discord.Interaction, username: str): 
        """Allows you to set your username""" 
        try:
            query = """
                INSERT INTO osu_user (osu_username, user_id) VALUES($1, $2)
                ON CONFLICT(user_id) DO 
                UPDATE SET osu_username = excluded.osu_username

            """
        
            await self.bot.pool.execute(query, username, interaction.user.id)

            await interaction.response.send_message(f"Sucessfullly set your osu username to: {username}")
        except Exception as e:
            return await interaction.response.send_message(f"Oh No! an error occured!\n\nError Class: **{e.__class__.__name__}**\n{default.traceback_maker(err=e)}If you're a coder and you think this is a fatal error, DM Sawsha#0598!", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        beatmap_regex =  re.compile(r"http[s]?://osu\.ppy\.sh/b/[0-9]{1,12}")

        try:
            if re.match(beatmap_regex, str(message.content)):
                numbers = re.findall(r'\d+', message.content)
                numbers = ''.join(x for x in numbers)
                beatmap = await self.bot.osu.get_beatmap(numbers)
                await message.channel.send(beatmap.artist)
        except Exception as e:
            print(e)

        