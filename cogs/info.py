import discord, datetime, time
from discord.ext import commands

from utils import http, cache, default

import psutil
import aiohttp
import os

start_time = time.time()



import discord
from discord.ext import commands

# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),
            discord.SelectOption(label='Green', description='Your favourite colour is green', emoji='🟩'),
            discord.SelectOption(label='Blue', description='Your favourite colour is blue', emoji='🟦')
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's 
        # selected options. We only want the first one.
        await interaction.response.send_message(f'Your favourite colour is {self.values[0]}')


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(colour=ctx.message.author.top_role.colour)
        embed.add_field(name="Uptime", value=text)
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    @commands.command()
    async def ping(self, ctx):
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Skye's current ping is WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command()
    async def covid(self, ctx, *, country: str = None):
        async with ctx.channel.typing():
            
            if country == None:
                r = await http.get(f"https://disease.sh/v3/covid-19/all", res_method="json")

                if "message" in r:
                    return await ctx.send(f"The API returned an error:\n{r['message']}")
            
                json_data = [
                    ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                    ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                    ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                    ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
                ]

                embed = discord.Embed(
                    description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R> \n sad covid :("
                )


                for name, value in json_data:
                    embed.add_field(
                        name=name, value=f"{value:,}" if isinstance(value, int) else value
                    )

                    
                await ctx.send(
                    f"Worldwide **COVID-19**  Statistics: ",
                    embed=embed
                )
            else:
                r = await http.get(f"https://disease.sh/v3/covid-19/countries/{country.lower()}", res_method="json")

                if "message" in r:
                    return await ctx.send(f"The API returned an error:\n{r['message']}")





                json_data = [
                    ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                    ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                    ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                    ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
                ]

                embed = discord.Embed(
                    description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R> \n sad covid :("
                )

                for name, value in json_data:
                    embed.add_field(
                        name=name, value=f"{value:,}" if isinstance(value, int) else value
                    )

                await ctx.send(
                    f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                    f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                    embed=embed
                )

    @commands.command(aliases=["info", "stats", "status"])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)
        cpuUsage = self.process.cpu_percent()


        embedColour = 0x5a92b1

        
        if hasattr(ctx, "guild") and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(title=f"ℹ About **{ctx.bot.user}**",colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar)
        embed.add_field(
            name=f"Developer{'' if len(self.config['owners']) == 1 else 'No developers?'}",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]])
        ,inline=False)
        embed.add_field(name="Library", value=f"discord.py | Running Version: **{discord.__version__}**",inline=False)
        embed.add_field(name="Date Created", value=default.date(self.bot.user.created_at, ago=True), inline=False)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )", inline=False)
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]), inline=False)
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=False)


        await ctx.send(embed=embed)

    @commands.command()
    async def help(self,ctx):
        embed=discord.Embed(title="💡List Of Commands")
        embed.add_field(name="**Website**:", value="\n*Tip: you can find more info at our [Command List](https://skyebot.dev/commands)*")
        embed.add_field(name="**<:malding:929627018474176542> __Skye__**", value="``work``, ``mood``, ``invite``, ``website``, ``stats``", inline=False)
        embed.add_field(name="**<:admin:933871693687062588> __Administrator__**", value="``setprefix``, ``autorole``, ``logging``")
        embed.add_field(name="**:tools: __Moderation__**", value="``Ban``, ``Unban``, ``Purge``, ``Mute``, ``Unmute``, ``kick``, ``warn``, ``timeout``, ``rt``", inline=False)
        embed.add_field(name="**🎵__Music__**", value="``join``, ``resume``,``pause``,``play``, ``queue``, ``stop``,``volume``", inline=False)
        embed.add_field(name="**:video_game: __Fun__**", value="``nick``, ``howgay``, ``howsus``, ``facts``, ``memes``, ``osugame``, ``8ball``, ``banf``, ``snipe``,``kys``, ``urban``, ``beer``🍻, ``joke``, ``horny``, ``triggered``, ``simp``, ``jail``",inline=False)
        embed.add_field(name="**<:anime:939807968151613460> __anime/anime_fun__**", value="``neko``, ``bite``", inline=False)
        embed.add_field(name="**🐶__Animals__**", value="``duck``, ``birb``", inline=False)
        embed.add_field(name="**📦 __Misc__**", value="``covid``, ``uptime``, ``ping``, ``av``, ``banner``, ``serverinfo``, ``userinfo``, ``rtfm``", inline=False)
   
        await ctx.send(embed=embed) 


    @commands.command()
    async def colour(self,ctx):
        """Sends a message with our dropdown containing colours"""

    # Create the view containing our dropdown
        view = DropdownView()

    # Sending a message containing our view
        await ctx.send('Pick your favourite colour:', view=view)





async def setup(bot):
    await bot.add_cog(Information(bot))    