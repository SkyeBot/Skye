import asyncio
import typing
import discord
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
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track , reason):
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
        
        if not interaction.user.voice:
            return await interaction.response.send_message("You are not connected to a voice channel!")

        else:
            if re.match(url_regex, track):
                node = wavelink.NodePool.get_node()
                song = (await node.get_tracks(wavelink.YouTubeTrack, track))[0]
            else:
                song = await wavelink.YouTubeTrack.search(query=track, return_first=True)
            
            ctx = await commands.Context.from_interaction(interaction)
        
            try: 
                if not ctx.voice_client:
                    vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                else:
                    vc: wavelink.Player = ctx.voice_client
                
                await interaction.guild.change_voice_state(channel=ctx.author.voice.channel,self_deaf=True)
                
                if vc.queue.is_empty and not vc.is_playing():
                    await vc.play(song)
                    embed = discord.Embed(description=f"Now playing: **[{song.title}]({song.uri}) By {song.author}**")
                    embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
                    embed.set_image(url=song.thumbnail)
                    await interaction.response.send_message(embed=embed)
                else:
                    await vc.queue.put_wait(song)
                    await interaction.response.send_message(f'Added `{song.title}` to the queue...')
            except UnboundLocalError: 
                pass
            
            except IndexError:
                print

    @app_commands.command()
    async def cp(self, interaction: discord.Interaction):
        """Returns whats currently playing"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not in a voice channel!")

        vc: wavelink.Player = interaction.guild.voice_client

        await interaction.response.send_message(f"Currently playing: {vc.source.uri}\n{vc.source.title}")


    @app_commands.command()
    async def skip(self, interaction: discord.Interaction):
        """Skips a song"""
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
        """Stops a song"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.stop()
        await interaction.response.send_message("Stopped!")

    @app_commands.command()
    async def disconnect(self, interaction:discord.Interaction):
        """Disconnects client from vc"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        
        ctx = await commands.Context.from_interaction(interaction)
        
        await ctx.guild.voice_client.disconnect(force=True)
        

        await interaction.response.send_message("Disconected from current vc!")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
    
        vc : wavelink.Player = voice_state
        if voice_state is None:
                # Exiting if the bot it's not connected to a voice channel
            return 

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()

    queue = app_commands.Group(name="queue", description="The queue group!")

    @queue.command()
    async def clear(self, interaction: discord.Interaction):
        """Clears queue"""
        vc : wavelink.Player = interaction.guild.voice_client

        await interaction.response.send_message(f"Cleared {len(vc.queue)} songs from the queue.")
        vc.queue.clear()

    @queue.command()
    async def add(self, interaction: discord.Interaction, *, search: str):
        """Adds query to queue"""
        vc: wavelink.Player = interaction.guild.voice_client

        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

        ctx = await commands.Context.from_interaction(interaction)
        
        if re.match(url_regex, search):
            node = wavelink.NodePool.get_node()
            song = (await node.get_tracks(wavelink.YouTubeTrack, search))[0]
        else:
            song = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        await vc.queue.put_wait(song)

        await interaction.response.send_message(f"Added **{song.title}** To The Queue")

    @queue.command()
    async def see(self, itr:discord.Interaction):
        """Allows you to see the queue"""
        vc: wavelink.Player = itr.guild.voice_client

        if not vc:
            return await itr.response.send_message('No queue as we are not connected', delete_after=5)
        if itr is None:
            if not vc.queue:
                return await itr.response.send_message(f"There is no songs in the queue!\nAdd one using the command ``skye queue add insertsongtitlehereorurl`` or by playing one!")
            else:
                embed = discord.Embed(title="Current queue")
                embed.description = "\n".join(str(song) for song in vc.queue)
                await itr.response.send_message(embed=embed)
        
    @app_commands.command()
    async def volume(self, interaction: discord.Interaction, volume: int):
        """Set a volume"""
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
        """Pauses the song currently playing"""
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message("I am not connected to a voice channel.")

        await vc.pause()
        await interaction.response.send_message("Paused.")

    @app_commands.command()
    async def resume(self, interaction: discord.Interaction):
        """Resumes the song currently playing"""
        vc: wavelink.Player = interaction.guild.voice_client
        if not vc: 
            return await interaction.response.send_message("I am not connected to a voice channel.")

        await vc.resume()
        await interaction.response.send_message("Resumed.")

    @app_commands.command()
    async def join(self, interaction:discord.Interaction):
        """Joins a voice channel"""

        if not interaction.guild.voice_client:
            ctx = await commands.Context.from_interaction(interaction)
        else:
            ctx = await commands.Context.from_interaction(interaction)
            vc: wavelink.Player = ctx.voice_client
        


        await ctx.author.voice.channel.connect(cls=wavelink.Player)
        await interaction.guild.change_voice_state(channel=ctx.author.voice.channel,self_deaf=True)
        await interaction.response.send_message(f"Joined: <#{ctx.author.voice.channel.id}>")
        

async def setup(bot):
    await bot.add_cog(Music(bot))