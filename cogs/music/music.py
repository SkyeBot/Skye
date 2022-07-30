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
        self.muloop = {}

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='lavalink',
                                            port=2333,
                                            password='youshallnotpass')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        self.bot.logger.info(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track , reason):
        ctx = player
        vc = wavelink.Player

    
        if f"{ctx.guild.id}" in self.muloop.keys():
            last = await wavelink.YouTubeTrack.search(query=f"{self.muloop[f'{ctx.guild.id}']} ", return_first=True) 

            await player.play(last)
        else:
            if not player.queue.is_empty: 

    
                new = await player.queue.get_wait()
                await ctx.channel.send(f"Now playing: **{new}**")
                await player.play(new)



        
    @app_commands.command()
    async def play(self, interaction: discord.Interaction, *, track: str):
        """Play a song with the given tracl query.

        If not connected, connect to our voice channel.
        """

            
        
        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        
        if not interaction.user.voice:
            return await interaction.response.send_message("You are not connected to a voice channel!")

        song = await wavelink.YouTubeTrack.search(query=track, return_first=True)

        if re.match(url_regex, track):
            node = wavelink.NodePool.get_node()
            song = (await node.get_tracks(wavelink.YouTubeTrack, track))[0]
        

            
        
            try: 

                vc: wavelink.Player = interaction.guild.voice_client
                if not interaction.guild.voice_client:
                    vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                
                
                await interaction.guild.change_voice_state(channel=interaction.user.voice.channel,self_deaf=True)
                
                if f"{interaction.guild.id}" not in self.muloop.keys():
                    if vc.queue.is_empty and not vc.is_playing():
                        await vc.play(song)
                        embed = discord.Embed(description=f"Now playing: **[{song.title}]({song.uri}) By {song.author}**")
                        embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
                        embed.set_image(url=song.thumbnail)
                        return await interaction.response.send_message(embed=embed)    
                    else:
                        await vc.queue.put_wait(song)
                        await interaction.response.send_message(f'Added `{song.title}` to the queue...')


            except UnboundLocalError: 
                pass

    @app_commands.command()
    async def loop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not in a voice channel!")

        vc: wavelink.Player = interaction.guild.voice_client

        if f"{interaction.guild.id}" not in self.muloop.keys():
            
            cp = vc.track

            self.muloop[f'{interaction.guild.id}'] = cp.uri
            print( self.muloop[f'{interaction.guild.id}'])
            await interaction.response.send_message(f"Now looping: {cp.title}")
        else:
            self.muloop.pop(f"{interaction.guild.id}")
            await interaction.response.send_message("Successfully disabled looping")

        


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
            if f"{interaction.guild.id}" in self.muloop.keys():
                self.muloop[f'{interaction.guild.id}'] = vc.queue[1].uri
                self.bot.logger.info(self.muloop[f'{interaction.guild.id}'])


            if not vc.queue.is_empty:
                await vc.stop()        
                self.bot.logger.info(vc.queue)
                return await interaction.response.send_message(f"Skipped Song!\nNow Playing **{vc.queue[0]}**")
        except wavelink.errors.QueueEmpty:
            await interaction.response.send_message("No song to skip too in the queue!")

    @app_commands.command()
    async def stop(self, interaction: discord.Interaction):
        """Stops a song"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        if f"{interaction.guild.id}"in self.muloop.keys():
                self.muloop.pop(f"{interaction.guild.id}")

        await vc.stop()
        await interaction.response.send_message("Stopped!")

    @app_commands.command()
    async def disconnect(self, interaction:discord.Interaction):
        """Disconnects client from vc"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("I am not currently in a voice channel!")
        
        ctx = await commands.Context.from_interaction(interaction)

        if f"{interaction.guild.id}" not in self.muloop.keys():
                self.muloop.pop(f"{interaction.guild.id}")
        
        await ctx.guild.voice_client.disconnect(force=True)
        

        await interaction.response.send_message("Disconected from current vc!")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
    
        vc : wavelink.Player = voice_state
        if voice_state is None:
            return 

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()

        if after.channel is None:
            if f"{vc.guild.id}" in self.muloop.keys():
                self.muloop.pop(f"{vc.guild.id}")
            vc.queue.clear()
            
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
        
        if not vc.queue:
                return await itr.response.send_message(f"There is no songs in the queue!\nAdd one using the command ``skye queue add insertsongtitlehereorurl`` or by playing one!")
        else:
            embed = discord.Embed(title="Current queue")
            
            embed.description = "\n".join(f"{count+1}: {song} by {song.author}" for count, song in enumerate(vc.queue))
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