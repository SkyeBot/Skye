import discord

from discord.ext import commands

from discord import app_commands

import pymongo

from pymongo import MongoClient

class Autorole(commands.Cog):
    """Cog to hold autorole commands + autorole events"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    group = app_commands.Group(name="autorole", description="Autorole settings")
    
    @group.command(name="check")
    @app_commands.checks.has_permissions(administrator=True)
    async def check(self, interaction: discord.Interaction):
        exists =  await self.bot.db.fetchrow("SELECT role FROM AUTOROLE WHERE guild = $1", interaction.guild.id)
        print(exists)
        if exists is None:
            em = discord.Embed(title="Autorole is disabled for this guild.", color=discord.Color(0xff0000))
            await interaction.response.send_message(embed=em)
        else:
            em = discord.Embed(title="Autorole is enabled for this guild.", color = discord.Color(0x32ff00))
            rol = discord.utils.get(interaction.guild.roles, id= exists.get("role"))
            print(exists.get("role"))
            em.add_field(name="Current role:", value=rol.mention)
            await interaction.response.send_message(embed=em)

    @commands.Cog.listener()
    async def on_member_join(self,member: discord.Member):
        try:
            exists =  await self.bot.db.fetchrow("SELECT role FROM AUTOROLE WHERE guild = $1", member.guild.id)

            print(exists.get("role"))

            rol = discord.utils.get(member.guild.roles, id=exists.get("role"))
          
            await member.add_roles(rol)
        except:
            pass



    @group.command(name="enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def _enable(self, interaction: discord.Interaction, role: discord.Role=None):
        exists =  await self.bot.db.fetchrow("SELECT role FROM AUTOROLE WHERE guild = $1", interaction.guild.id)

        try: 
                if role == None:
                    await interaction.response.send_message("No role provided")
                else:
                 if (exists==None):
                    await self.bot.db.execute('INSERT INTO autorole(role, guild) VALUES ($1, $2)',role.id, interaction.guild.id)
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="Autorole enabled", value="Current role: {}".format(role.mention))
                    await interaction.response.send_message(embed=em)
                 else:
                    await self.bot.db.execute('UPDATE autorole SET role = $1 WHERE guild = $2',  role.id, interaction.guild.id)
                    em = discord.Embed(title="", color= discord.Color(0x32ff00))
                    em.add_field(name="Autorole Updated", value="new role: {}".format(role.mention))
                    await interaction.response.send_message(embed=em)
        except (Exception) as e:
            await interaction.response.send_message(e)    

    @group.command(name="disable")
    @app_commands.checks.has_permissions(administrator=True)
    async def _disable(self, interaction: discord.Interaction, role: discord.Role):
        exists =  await self.bot.db.fetchrow("SELECT role FROM AUTOROLE WHERE guild = $1", interaction.guild.id)
        
        if(exists!=None):
            await self.bot.db.execute("UPDATE autorole SET role = NULL, guild = NULL where guild = $1", interaction.guild.id)
            await interaction.response.send_message("Autorole is now disabled!")

    @commands.command()
    async def give(self, ctx:commands.Context):
        rol = discord.utils.get(ctx.guild.roles, id= 913161078370893885)

        await ctx.author.add_roles(rol)
    
    


async def setup(bot):
    await bot.add_cog(Autorole(bot))
        
