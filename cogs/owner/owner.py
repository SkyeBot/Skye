import discord

from discord.ext import commands

from discord import app_commands

from core.bot import SkyeBot

class owner(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    async def is_nsfw(interaction: discord.Interaction) -> bool:
        
        if interaction.user.id == 894794517079793704:
            return True
        
        await interaction.response.send_message("You Cannot Use This Command!", ephemeral=True)
        return False

    @app_commands.command(name="shards")
    @app_commands.check(is_nsfw)
    async def get_shards(self, itr: discord.Interaction):
        shard_id = itr.guild.shard_id
        shard = self.bot.get_shard(shard_id)
        shard_ping = shard.latency
        shard_servers = ", ".join(guild.name for guild in self.bot.guilds if guild.shard_id == shard_id)

        await itr.response.send_message(f"All shard servers on the shard *{shard.id}*: **{shard_servers}**")


        