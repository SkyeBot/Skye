import youtube_dl
import discord

import aiohttp
import asyncio

from discord.ext import commands

bot = commands.Bot()


youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)




class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")
        self.channel = data.get("channel")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def playfile(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(
            source, after=lambda e: print(f"Player error: {e}") if e else None
        )

        await ctx.send(f"Now playing: {query}")

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
    
            
        if voice_state is None:
                # Exiting if the bot it's not connected to a voice channel
            return 

        if len(voice_state.channel.members) == 1:
            await voice_state.disconnect()
   
    @commands.command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""


        channel = ctx.message.author.voice.channel
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)


                
        async with ctx.typing():
            
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                
                player, after=lambda e: print(f"Player error: {e}") if e else None,
            )
            
        embed = discord.Embed(title=f"Now playing: **{player.title}**", description=f"**Uploaded by {player.channel}**")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        
        await ctx.send(embed=embed)

    
    
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if volume > 100:
            await ctx.send("You cannot put this over 100 Volume!")
        else:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"Changed volume to {volume}%")

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconected!")

    @commands.command()
    async def lyrics(self, ctx, artist,*, title):
        async with aiohttp.ClientSession() as session:
           async with session.get(f"https://api.lyrics.ovh/v1/{artist}/{title}") as response:
                data = await response.json()
                lyrics = data['lyrics']
                if lyrics is None:
                    await ctx.send("Song not found! Please enter correct Artist and Song title")
                if len(lyrics) > 2048:
                    lyrics = lyrics[:2048]
                emb = discord.Embed(title = f"{title}" , description = f"{lyrics}", color = 0xa3a3ff)
                await ctx.send(embed=emb)
        await session.close()
    
    @commands.command()
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send(f"Paused!")

    @commands.command()
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send(f"Resumed!")
    
    @playfile.before_invoke
    @yt.before_invoke
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def setup(bot):
    bot.add_cog(Music(bot))

