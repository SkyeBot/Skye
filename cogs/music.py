
"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.
Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re

import discord
import wavelink
from discord.ext import commands

class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='127.0.0.1',
                                            port=2333,
                                            password='youshallnotpass')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.
        """
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        await vc.play(search)

    @commands.command()
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = ctx.voice_client
        await vc.stop()
        await ctx.send("Stopped!")

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx:commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I am not currently in a voice channel!")
        
        await ctx.voice_client.disconnect(force=True)

        await ctx.send("Disconected from current vc!")
        

async def setup(bot):
    await bot.add_cog(Music(bot))


