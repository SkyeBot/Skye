import sys
import logging
import discord

from discord.ext import commands, ipc
from discord.ext.ipc.server import route
from discord.ext.ipc.errors import IPCError

from core.bot import SkyeBot    


class Routes(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(
                self.bot, host="172.18.0.2", port=2300, secret_key="your_secret_key_here"
            )

            bot.ipc.start()

        

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        logging.info("Ipc is ready")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint: str, error: IPCError):
        print(error)

    @route()
    async def get_user_data(self, data):
        user = await self.bot.fetch_user(data.user_id)
    
        data = {    
            'username': user.name,
            'id': user.id,
            'avatar': user.display_avatar.url,
            'discriminator': user.discriminator,
            'bot': user.bot,
        }

        return data

    @route()
    async def get_guild_count(self,data):
        data = {
            "count":len(self.bot.guilds)
        }
        return data  # returns the len of the guilds to the client

    @route()
    async def get_guild_ids(self,data):
        final = {"data": [g.id for g in self.bot.guilds]}
        return final # returns the guild ids to the client


    
    @route()
    async def get_guild(self,data):
        guild = self.bot.get_guild(data.guild_id)
        if guild is None:
            return None

        guild_data = {
            "name": guild.name,
            "id": guild.id,
            "owner_id": guild.owner_id,
            "prefix": "?"
        }

        return guild_data




async def setup(bot):
    await bot.add_cog(Routes(bot))
