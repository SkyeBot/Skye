import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
import praw


reddit = praw.Reddit(client_id='pua14mlzkyv5_ZfQ2WmqpQ',
                     client_secret='T5loHbaVD7m-RNMpFf0z24iOJsInwg',
                     user_agent='Oxygen',
                     check_for_async= False)

class MyCog(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    

  MY_GUILD_ID = discord.Object(id=837018898142330961) 
  
  section = app_commands.Group(name="test", description="Test commands")


  @app_commands.command(name="say")
  @app_commands.guilds(MY_GUILD_ID)
  @commands.has_permissions(ban_members=True)
  async def say(self, interaction:discord.Interaction, *, args: str) -> None:
        await interaction.response.send_message(f"Hello test says: {args}!", ephemeral=False)

  @app_commands.command(name="reddit")
  @app_commands.describe(subreddit='Pick a subreddit to get posts from!')
  async def reddit(self, interaction: discord.Interaction, subreddit: str):
    
    meme_submissions = reddit.subreddit(subreddit).top()
    post_to_pick = random.randint(1,50)
    for i in range(0, post_to_pick):
      submission = next(x for x in meme_submissions if not x.stickied)

    embed = discord.Embed(description=f"**[{submission.title}]({submission.url})**")
    embed.add_field(name="Subreddit", value=f"[r/{submission.subreddit}]({submission.url})", inline=True)
    embed.add_field(name="Author", value=f"[{submission.author}](https://www.reddit.com/user/{submission.author}/)", inline=True)
    embed.add_field(name="Upvotes", value=submission.score, inline=True)
    embed.add_field(name="Upvote Ratio", value=submission.upvote_ratio, inline=True)
    embed.set_image(url=submission.url)    
    
    await interaction.response.send_message(embed=embed)

  @section.command(name="sub-command") # we use the declared group to make a command.
  async def my_sub_command(self, interaction: discord.Interaction) -> None:
    """ /parent sub-command """
    await interaction.response.send_message("Hello from the sub command!", ephemeral=True)

  @commands.is_owner()
  @commands.command()
  async def sync(self, ctx):
        """Sync all commands to this server"""
        progress_msg = await ctx.send("Trying to sync...")
        test = await self.bot.tree.sync()
        await progress_msg.edit(f"Synced on this server: {test}")


async def setup(bot):
  
  await bot.add_cog(MyCog(bot))