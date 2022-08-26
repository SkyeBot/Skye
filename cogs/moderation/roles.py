import discord
from discord.ext import commands
from core.bot import SkyeBot
from discord import app_commands


class Roles(commands.Cog):
    def __init__(self, bot: SkyeBot):
        self.bot = bot

    roles = app_commands.Group(name="role", description="Does role stuff", default_permissions=discord.Permissions(manage_roles=True))

    @roles.command(description="Adds a role to a user")
    async def add(self, itr: discord.Interaction, member: discord.Member, role: discord.Role):

        if role in member.roles:
            return itr.response.send_message("This user already has this role!", ephemeral=True)
        
        elif itr.user.top_role <= role or itr.guild.me.top_role <= role:
            return await itr.response.send_message("This role is higher than the author's or my top role!", ephemeral=True)

        await member.add_roles(role, reason="Added using the /role add command!")

        return await itr.response.send_message(f"Succesfully added {role.mention} to {member.mention}!", allowed_mentions=discord.AllowedMentions(roles=False, users=False), ephemeral=True)

    @roles.command()
    async def remove(self, itr: discord.Interaction, member: discord.Member, role: discord.Role):
        if role not in member.roles:
            return await itr.response.send_message("This user does not have the role", ephemeral=True)
        
        elif itr.user.top_role <= role or itr.guild.me.top_role <= role:
            return await itr.response.send_message("This role is higher than the author's or my top role!", ephemeral=True)
        
        await member.remove_roles(role, reason="Removed role using /role remove command!")
        return await itr.response.send_message(f"Succesfully removed {role.mention} from {member.mention}'s roles!", allowed_mentions=discord.AllowedMentions(roles=False, users=False), ephemeral=True)