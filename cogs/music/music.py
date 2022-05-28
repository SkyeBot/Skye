import asyncio
import typing
import discord
import wavelink
from discord.ext import commands
from core.bot import SkyeBot

from typing import Union

class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: SkyeBot):
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

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track , reason):
        ctx = player.channel
        if not player.queue.is_empty:
            await asyncio.sleep(2)
            new = player.queue.get()
            await ctx.send(f"Now playing: **{new}**")
            await player.play(new)
            
    

    @commands.command()
    async def play(self, ctx: commands.Context, *, track: wavelink.YouTubeTrack):
        """Play a song with the given tracl query.

        If not connected, connect to our voice channel.
        """
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(track)
            embed = discord.Embed(title=f"Now playing: **{track.title} By {track.author}**")
            embed.set_author(name=ctx.author, url=ctx.author.display_avatar.url)
            embed.set_image(url=track.thumbnail)
            await ctx.send(embed=embed)
        else:
            await vc.queue.put_wait(track)
            await ctx.send(f'Added `{track.title}` to the queue...')

    @commands.command(aliases=["currentlyplaying"])
    async def cp(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I am not in a voice channel!")

        vc: wavelink.Player = ctx.voice_client

        await ctx.send(f"Currently playing: {vc.source.uri}\n{vc.source.title}")


    @commands.command()
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        next = vc.queue.get()
        await asyncio.sleep(3)
        await vc.play(next)
        await ctx.send(f"Skipped Song!\nNow Playing **{next}**")

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
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
    
            
        if voice_state is None:
                # Exiting if the bot it's not connected to a voice channel
            return 

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()

    @commands.group()
    async def queue(self, ctx: commands.Context):
        
        
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.send('No queue as we are not connected', delete_after=5)
        if ctx.invoked_subcommand is None:
            if not vc.queue:
                return await ctx.send(f"There is no songs in the queue!\nAdd one using the command ``skye queue add insertsongtitlehereorurl`` or by playing one!")
            else:
                embed = discord.Embed(title="Current queue")
                embed.description = "\n".join(str(song) for song in vc.queue)
                await ctx.send(embed=embed)
    
    


    @queue.command()
    async def clear(self, ctx: commands.Context):
        vc : wavelink.Player = ctx.voice_client

        await ctx.send(f"Cleared {len(vc.queue)} songs from the queue.")
        vc.queue.clear()

    @queue.command()
    async def add(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        vc: wavelink.Player = ctx.voice_client

        await vc.queue.put_wait(search)

        await ctx.send(f"Added **{search.title}** To The Queue")
        
    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.send("I am not connected to a voice channel.")

        elif volume > 100:
            return await ctx.send("You cannot put the volume over 100!")
        else:
            await vc.set_volume(volume=volume)
            await ctx.send(f"The volume is now {volume}%")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.send("I am not connected to a voice channel.")

        await vc.pause()
        await ctx.send("Paused.")

    @commands.command()
    async def resume(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client
        if not vc: 
            return await ctx.send("I am not connected to a voice channel.")

        await vc.resume()
        await ctx.send("Resumed.")

    @commands.command()
    async def join(self, ctx:commands.Context):

        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        

async def setup(bot):
    await bot.add_cog(Music(bot))


