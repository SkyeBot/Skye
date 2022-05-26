from venv import create
import discord
from io import BytesIO
from discord.ext import commands
from PIL import Image, ImageDraw, ImageChops, ImageFont
from utils import default



def circle(pfp,size = (215,215)):
    
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

class TestingCog(commands.Cog):
    """Testing commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    @commands.command()
    async def profile(self, ctx: commands.Context, *, member: discord.Member=None):
        if not member:
            member = ctx.author

        name  = str(member.name)
        nick = str(member.display_name)
        id  = str(member.id)
        status = str(member.status).upper()

        created_at = member.created_at.strftime("%a %b\n%B %Y")
        joined_at = member.joined_at.strftime("%a %b\n%B %Y")


        bank = await self.bot.db.fetchrow("SELECT money FROM ECONOMY WHERE userid = $1", ctx.author.id)
  
  
        money, level = f"0 dollars" if bank is None else f"{bank.get('money')} dollars", "100"

        base = Image.open("base.png").convert("RGBA")
        bg = Image.open("bg.png").convert("RGBA")

        pfp = member.avatar.replace(size=256)
        data = BytesIO(await pfp.read())
        pfp = Image.open(data).convert("RGBA")
        name = f"{name[:16]}.." if len(name) >16 else name
        name = f"AKA - {name[:17]}.." if len(nick) >17 else f"AKA - {nick}"

        draw = ImageDraw.Draw(base)
        pfp = circle(pfp,(215,215))
        font = ImageFont.truetype("/root/skye/bot/Nunito-Regular.ttf",38)
        akafont = ImageFont.truetype("/root/skye/bot/Nunito-Regular.ttf",30)
        subfont = ImageFont.truetype("/root/skye/bot/Nunito-Regular.ttf",25)
        
        draw.text((280,240), name, font=font)
        draw.text((270,315), nick, font=akafont)
        draw.text((65,490), id, font=subfont)
        draw.text((405,490), status, font=subfont)
        draw.text((65,635), money, font=subfont)
        draw.text((405,635), level, font=subfont)
        draw.text((65,770), created_at, font=subfont)
        draw.text((405,770), joined_at, font=subfont)

        base.paste(pfp, (56, 158), pfp)

        bg.paste(base,(0,0),base)

        with BytesIO() as a:
            bg.save(a,"PNG")
            a.seek(0)
            await ctx.send(file=discord.File(a,"profile.png"))
    
    @commands.command()
    async def testing5(self, ctx: commands.Context):
        async with self.bot.session.get("https://thino.pics/api/v1/tomboy") as resp:
            json = await resp.json()
            return await ctx.send(json["url"])


    @commands.command()
    async def spotify(self, ctx:commands.Context):
        spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), ctx.author.activities)

        if spotify is None:
            return await ctx.send("You are not listening to spotify!")
        artists = ', '.join(spotify.artists)
        embed = discord.Embed(description=f"You are listening to [{spotify.title}]({spotify.track_url}) by artist: **[{artists}](*")
        
        embed.set_image(url=spotify.album_cover_url)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(TestingCog(bot))
