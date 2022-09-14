from collections import Counter
import logging
import discord

from discord.ext import commands

from discord import app_commands

from typing import Union, Optional
from utils.context import Context

#Local imports
from utils import default, time, format


logger = logging.getLogger(__name__)

class Dropdown(discord.ui.Select):
    def __init__(self, user: int, author_id: int,guild_id: int=None):
        self.member =  user
        self.embed: discord.Embed = discord.Embed()
        self.guild_id = guild_id
        self.author_id = author_id
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='avatar', description='Avatar of the user'),
            discord.SelectOption(label='banner', description='The Banner of the user'),
            discord.SelectOption(label='info', description='Actual userinfo'),
            discord.SelectOption(label="roles", description="Gets roles if user is a member")
        ]


        super().__init__(min_values=1, max_values=1, options=options, custom_id="MYVEERYCOOLUSERSELECT")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.client.get_guild(self.guild_id) 
        if guild is None:
            guild = interaction.guild

        await interaction.response.defer()
   


        if self.values[0] == "banner":
            member = guild.get_member(self.member)

            if member is None:
                member = await interaction.client.fetch_user(self.member) 
                banner = member.banner  
            else:
                banner = (await interaction.client.fetch_user(self.member)).banner
    

            self.embed.description=f"{member.mention} Banner"
            self.embed.color =0x3867a8

            if banner is None:
                self.embed.description = "User does not have a banner!"
            else:
                self.embed.set_image(url=banner.url)
        
            
            await interaction.message.edit(embed=self.embed, view=DropdownView(member.id, self.author_id,guild.id))

        if self.values[0] == "avatar":
            member = guild.get_member(self.member)
            if member is None:
                member = await interaction.client.fetch_user(self.member) 

           
            text = f"[PNG]({member.display_avatar.with_static_format('png').url}) | [JPG]({member.display_avatar.with_static_format('jpg').url}) | [JPEG]({member.display_avatar.with_static_format('jpeg').url}) | [WEBP]({member.display_avatar.with_static_format('webp').url})"

            self.embed.description = text
            self.embed.color = 0x3867a8
            self.embed.set_image(url=member.display_avatar.url)
            await interaction.message.edit(embed=self.embed, view=DropdownView(member.id, self.author_id,guild.id))

        if self.values[0] == "info":
            member = guild.get_member(self.member)
            logger.info(guild)
            logger.info(member)
            if member is None:
                member = await interaction.client.fetch_user(self.member) 


            self.embed.description = f"**Info About {member.mention}**"
            self.embed.color = interaction.client.color
            roles = [role.mention for role in getattr(member, 'roles', [])]

            joined_date = default.date(getattr(member, "joined_at", None), ago=True)


            self.embed.add_field(name="Joined At", value=joined_date)
            

    
            view = DropdownView(member.id, self.author_id,guild.id)
            created_date = default.date(member.created_at, ago=True)

            self.embed.add_field(name="ID", value=member.id)
            self.embed.add_field(name="Created At", value=created_date,inline=True)
            if roles:
                self.embed.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
            self.embed.set_author(name=member, icon_url=member.display_avatar.url)
            self.embed.set_thumbnail(url=member.display_avatar.url)

            await interaction.message.edit(embed=self.embed,view=view)

        if self.values[0] == "roles":
            member = guild.get_member(self.member)
            if member is None:
                member = await interaction.client.fetch_user(self.member) 

            roles = [role.mention for role in getattr(member, 'roles', [])]
                   
            self.embed.title = f"{member}'s Roles"
            self.embed.description = ', '.join(roles) if roles else "Member has no roles or is a User"

            view = DropdownView(member.id, self.author_id,guild.id)
            await interaction.message.edit(embed=self.embed,view=view)

class DropdownView(discord.ui.View):
    def __init__(self, member: int , author_id: int ,guild_id: int=None,):
        super().__init__(timeout=None)
        self.member = member
        self.author_id = author_id
        # Adds the dropdown to our view object.
        self.add_item(Dropdown(self.member, author_id,guild_id))



    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.author_id:
            return True
        else:
            await interaction.response.send_message(f"You cant use this as you're not the command invoker, only the author (<@{interaction.client.get_user(self.author_id).id}>) Can Do This!", ephemeral=True)
            return False

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo")
    async def userinfo_slash(self, itr: discord.Interaction, member: Optional[Union[discord.Member, discord.User]]):
        """Get's info about a user"""
        user = member if member is not None else itr.user
        embed = discord.Embed(description=f"**Info About {user.mention}**", color=self.bot.color)

        roles = [role.mention for role in getattr(user, 'roles', [])]

        joined_date = default.date(getattr(user, "joined_at", None), ago=True)


        embed.add_field(name="Joined At", value=joined_date)


        persistent_query = "INSERT INTO persistent_view (user_id, message_id, guild_id, author_id) VALUES ($1, $2, $3, $4)"
 
        view = DropdownView(user.id, itr.user.id,itr.guild.id)
        

        created_date = default.date(user.created_at, ago=True)

        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Created At", value=created_date,inline=True)
        if roles:
            embed.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        embed.set_author(name=user, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
    
        await itr.response.send_message(embed=embed, view=view)

        await self.bot.pool.execute(persistent_query, user.id, (await itr.original_response()).id, itr.guild.id, itr.user.id)
    
    @app_commands.command(name="serverinfo")
    async def serverinfo(self, interaction: discord.Interaction):
        """Shows info about the current server."""
        guild = interaction.guild


        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed()
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:1014007933245337631>',
            discord.VoiceChannel: '<:voice_channel:1014007956829917205>',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)

        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner',
        }

        info = []

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{self.bot.tick(True)}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({time.format_relative(last_boost.premium_since)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({format.plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

        fmt = (
            f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n'
            f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n'
        )
        if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit*2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await interaction.response.send_message(embed=e)
