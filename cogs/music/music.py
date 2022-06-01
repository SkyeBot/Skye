import asyncio
import typing
import discord
from sqlalchemy import desc
import wavelink
from discord.ext import commands
from core.bot import SkyeBot

from discord import app_commands    

from typing import Union

import re

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
        self.bot.logger.info(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track , reason):
        ctx = player.channel
        vc = wavelink.Player
        if not player.queue.is_empty:
            await asyncio.sleep(2)
            new = player.queue.get()
            await ctx.send(f"Now playing: **{new}**")
            await player.play(new)
        
    @app_commands.command()
    async def play(self, interaction: discord.Interaction, *, track: str):
        """Play a song with the given tracl query.

        If not connected, connect to our voice channel.
        """
        
        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

        ctx = await commands.Context.from_interaction(interaction)
        
        if re.match(url_regex, track):
            node = wavelink.NodePool.get_node()
            song = (await node.get_tracks(wavelink.YouTubeTrack, track))[0]
        else:
            song = await wavelink.YouTubeTrack.search(query=track, return_first=True)
        
        if not interaction.guild.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(song)
            embed = discord.Embed(description=f"Now playing: **[{song.title}]({song.uri}) By {song.author}**")
            embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            embed.set_image(url=song.thumbnail)
            await interaction.response.send_message(embed=embed)
        else:
            await vc.queue.put_wait(song)
            await interaction.response.send_message(f'Added `{song.title}` to the queue...')

    @app_commands.command()
    async def cp(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not in a voice channel!")

        vc: wavelink.Player = interaction.guild.voice_client

        await interaction.response.send_message(f"Currently playing: {vc.source.uri}\n{vc.source.title}")


    @app_commands.command()
    async def skip(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        try:
            next = vc.queue.get()
            await asyncio.sleep(3)
            await vc.play(next)
            await interaction.response.send_message(f"Skipped Song!\nNow Playing **{next}**")
        except wavelink.errors.QueueEmpty:
            await interaction.response.send_message("No song to skip too in the queue!")

    @app_commands.command()
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.stop()
        await interaction.response.send_message("Stopped!")

    @app_commands.command()
    async def disconnect(self, interaction:discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        
        ctx = await commands.Context.from_interaction(interaction)
        
        await ctx.guild.voice_client.disconnect(force=True)
        

        await interaction.response.send_message("Disconected from current vc!")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
    
            
        if voice_state is None:
                # Exiting if the bot it's not connected to a voice channel
            return 

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()

    @commands.group()
    async def queue(self, interaction: discord.Interaction):
        
        
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message('No queue as we are not connected', delete_after=5)
        if interaction.invoked_subcommand is None:
            if not vc.queue:
                return await interaction.response.send_message(f"There is no songs in the queue!\nAdd one using the command ``skye queue add insertsongtitlehereorurl`` or by playing one!")
            else:
                embed = discord.Embed(title="Current queue")
                embed.description = "\n".join(str(song) for song in vc.queue)
                await interaction.response.send_message(embed=embed)
    
    


    @queue.command()
    async def clear(self, interaction: discord.Interaction):
        vc : wavelink.Player = interaction.guild.voice_client

        await interaction.response.send_message(f"Cleared {len(vc.queue)} songs from the queue.")
        vc.queue.clear()

    @queue.command()
    async def add(self, interaction: discord.Interaction, *, search: wavelink.YouTubeTrack):
        vc: wavelink.Player = interaction.guild.voice_client

        await vc.queue.put_wait(search)

        await interaction.response.send_message(f"Added **{search.title}** To The Queue")
        
    @app_commands.command()
    async def volume(self, interaction: discord.Interaction, volume: int):
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message("I am not connected to a voice channel.")
        

        elif volume > 100:
            return await interaction.response.send_message("You cannot put the volume over 100!")
        else:
            await vc.set_volume(volume=volume)
            await interaction.response.send_message(f"The volume is now {volume}%")

    @app_commands.command()
    async def pause(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message("I am not connected to a voice channel.")

        await vc.pause()
        await interaction.response.send_message("Paused.")

    @app_commands.command()
    async def resume(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if not vc: 
            return await interaction.response.send_message("I am not connected to a voice channel.")

        await vc.resume()
        await interaction.response.send_message("Resumed.")

    @app_commands.command()
    async def join(self, interaction:discord.Interaction):

        if not interaction.guild.voice_client:
            ctx = await commands.Context.from_interaction(interaction)
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            ctx = await commands.Context.from_interaction(interaction)
            vc: wavelink.Player = ctx.voice_client
        
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        

async def setup(bot):
    await bot.add_cog(Music(bot))


