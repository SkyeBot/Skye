import discord

from discord.ext import commands


import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(description="Mutes Member")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member=None, *, reason=None):
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")

        if member == None:
            await ctx.send("`Who are you muting?`")
        else:
            if not mutedRole:
                mutedRole = await guild.create_role(name="Muted")
        
                for channel in guild.channels:
                    await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
        
            embed =  discord.Embed(title="❌ Muted", description=f"{ctx.author.mention} Muted {member.mention}", colour=discord.Colour.light_gray())
            embed.add_field(name="reason:", value=reason, inline=False)
    
            if member == ctx.author:
                await ctx.send('you cannot mute yourself!')
            else:
                await ctx.send(embed=embed)
                await member.add_roles(mutedRole, reason=reason)
                await member.send(f'You have been muted from {guild.name}! \n Reason: {reason}')    

    @commands.command(description="Unmutes a specified user.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        guild = ctx.guild
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
        else:    
            await member.remove_roles(mutedRole)
            embed = discord.Embed(title="✅ Unmuted!", description=f"Unmuted {member.mention}",colour=discord.Colour.light_gray())
            await ctx.send(embed=embed)
            await member.send(f"you have unmuted from: {ctx.guild.name}")        

    @commands.command(aliases=['clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self,ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        embed=discord.Embed(title="Cleared", description=f"**``{limit} Messages``**")
        embed.set_footer(text=f'Requested By {ctx.author}', icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @purge.error
    async def purge_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"<a:siren:922358771735461939> You can't use this command! Command requires ``Manage Messages`` Permissions! <a:siren:922358771735461939>")
            print(f"Command ``sotd`` was attempted \n User Who Used It == {ctx.author}! \n ID == {ctx.author.id} \n -------------------------------------------------------")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self,ctx, member:discord.Member=None, *, reason: commands.clean_content = ""):    
        if member == None:
            await ctx.send("``Who Are You Banning?``")
        else:
            if member == self.bot.user:
                await ctx.send("``You Cannot Ban Me!``")
            else:
                if member == ctx.author:
                    await ctx.send('``You Cannot Ban Yourself!``')
                else:    
                    if reason == None:
                        reason="No Reason Specified" 

                    embed = discord.Embed(title=f"succesfully banned {member.name} from this server", description=f"Reason: {reason}\nBy: {ctx.author.mention}")    

                    await member.ban(reason=reason)
                    await ctx.send(embed=embed) 
                    await member.send(f'``You Have Been Banned From {ctx.guild.name} for`` \n``{reason}``')
                     

    @ban.error
    async def ban_error(self,ctx, error):   
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"<a:siren:922358771735461939> You can't use this command! Command requires ``Ban Members`` Permissions! <a:siren:922358771735461939>")
            print(f"Command ``sotd`` was attempted \n User Who Used It == {ctx.author}! \n ID == {ctx.author.id} \n -------------------------------------------------------") 

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self,ctx, *, user=None):
        if user == None:
            await ctx.send("``Who Are You Banning?``")
        else:
            try:
                user = await commands.converter.UserConverter().convert(ctx, user)
            except:
                await ctx.send("Error: user could not be found!")
                return

            try:
                bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
                if user in bans:
                    await ctx.guild.unban(user, reason="Responsible moderator: "+ str(ctx.author))
                else:
                    await ctx.send("User not banned!")
                    return

            except discord.Forbidden:
                await ctx.send("I do not have permission to unban!")
                return

            except:
                await ctx.send("Unbanning failed!")
                return

            embed=discord.Embed(title="Successfully unbanned", description=f"{user.mention}")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self,ctx, member:discord.Member=None, *, reason=None):
        if member == None:
            await ctx.send("Who are you kicking?")
        else:
            if member == ctx.author:
                await ctx.send('``You Cannot kick Yourself!``')
            if reason == None:
                reason="No Reason Specified"

            embed = discord.Embed(title=f"Successfully kicked {member}", description=f"Reason: {reason}")   
            await member.kick(reason=reason)
            await member.send(f'``You Have Been Kicked From {ctx.guild.name} for`` \n ``{reason}``')
            await ctx.send(embed=embed)        


    @commands.command()
    async def timeout(self,ctx, member:discord.Member=None, minutes: int=None, *, reason=None):
        if member == None:
            await ctx.send("Please Specify The Person You Are Timing Out!")
        else:
            if minutes == None:
                await ctx.send("Please Say The Duration Of The Timeout!")
            if reason == None:
                reason = "No Reason Specified"

            duration = datetime.timedelta(minutes=minutes)
            await member.timeout_for(duration, reason=reason)

            embed = discord.Embed(title=f"Timedout {member}\nReason: {reason}", description=f"Duration: {duration}")
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Moderation(bot))         