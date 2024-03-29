import discord
import string
import io

class ImgModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Image url")

    url = discord.ui.TextInput(label='Set Image url', placeholder="Set an image url here")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        async with interaction.client.session.get(self.url.value) as resp:  
            image = io.BytesIO(await resp.read())
        await interaction.response.send_message("Succesfully set image to the following",file=discord.File(image, filename=self.url.value.split('/')[3]), ephemeral=True)

class MsgModal(discord.ui.Modal):  
    def __init__(self):
      super().__init__(title="Welcome Message")
    
    msg = discord.ui.TextInput(label="Make an message", placeholder="vars = $user, $guild", default="Welcome $user to $guild!", )
    
    async def on_submit(self, itr: discord.Interaction):
        new_text = string.Template(self.msg.value).safe_substitute(
            user=itr.user.mention,
            guild=itr.guild
        )
        return await itr.response.send_message(f"Welcome Message Is Now Set To: **{new_text}**", ephemeral=True, allowed_mentions=discord.AllowedMentions(users=False, roles=False))

class ChannelModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set Welcome Channel")

    channeltext = discord.ui.TextInput(label="Channel", placeholder="Insert channel id or name",)

    async def on_submit(self, itr: discord.Interaction):
        
    
        
        if self.channeltext.value.isnumeric():
            channel = itr.guild.get_channel(int(self.channeltext.value))
        else:
            channel = discord.utils.find(lambda c: c.name == self.channeltext.value, itr.guild.text_channels)

        if channel is None:
            return await itr.response.send_message("There's no channel with that name or ID!", ephemeral=True)
        
        return await itr.response.send_message(f"Set channel to {channel.mention} ({channel.id})!", ephemeral=True)

class MyView(discord.ui.View):
    def __init__(self, author_id: int, channel: int, itr: discord.Interaction):
        self.author_id = author_id
        super().__init__(timeout=None)
        self.channel = itr.client.get_channel(channel)
        self.msg = None
        self.image = None
    
    async def interaction_check(self, itr: discord.Interaction) -> bool:
        if itr.user.id == self.author_id:
            return True
        await itr.response.send_message(f"You cant use this as you're not the command invoker, only the author (<@{itr.client.get_user(self.author_id).id}>) Can Do This!", ephemeral=True)
        return False

    @discord.ui.button(label="Welcome Image", style=discord.ButtonStyle.blurple)
    async def welcome_image(self, interaction: discord.Interaction, button: discord.ui.button):
        modal = ImgModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.image = modal.url.value or self.image
    
    @discord.ui.button(label="Custom Message", style=discord.ButtonStyle.blurple)
    async def message(self, itr: discord.Interaction, button: discord.ui.button):
        modal = MsgModal()
        await itr.response.send_modal(modal)
        await modal.wait()
        self.msg = modal.msg.value
    
        
    @discord.ui.button(label="Custom Channel", style=discord.ButtonStyle.blurple)
    async def custom_channel(self, itr: discord.Interaction, button: discord.ui.button):
        modal = ChannelModal()
        await itr.response.send_modal(modal)
        await modal.wait()
        

        if modal.channeltext.value.isnumeric():
            self.channel = itr.guild.get_channel(int(modal.channeltext.value))
        else:
            self.channel = discord.utils.find(lambda c: c.name == modal.channeltext.value, itr.guild.text_channels)
            
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.danger)
    async def disable(self, itr: discord.Interaction, button: discord.ui.button) -> None:
        exists = await itr.client.pool.fetchrow("SELECT * FROM welcomer_config WHERE guild_id = $1", itr.guild.id)
        if exists:
            await itr.client.pool.execute("DELETE FROM welcomer_config WHERE guild_id = $1", itr.guild.id)
            for item in self.children:
                item.disabled = True
            await itr.message.edit(view=self)
            return await itr.response.send_message("Succesfully disabled welcomer for this guild!", ephemeral=True)
        
        return await itr.response.send_message("Cannot disable welcomer as welcommer is not enabled in the first place!", ephemeral=True)

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.green)
    async def idk(self, itr: discord.Interaction, button: discord.ui.button):
        query = """
            INSERT INTO welcomer_config (channel_id, message, guild_id, image) VALUES($1, $2, $3, $4)
            ON CONFLICT(guild_id) DO 
            UPDATE SET channel_id = excluded.channel_id, message = excluded.message, image = excluded.image

        """
        itr.message.reference.cached_message.attachments[0].read

        
        await itr.client.pool.execute(query, self.channel.id, self.msg if self.msg else "Welcome $user to $guild!", itr.guild.id, self.image)
        msg = string.Template(self.msg if self.msg else "Welcome $user to $guild!").safe_substitute(
            user=itr.user.mention,
            guild=itr.guild
        )
        embed = discord.Embed(description=f"**{msg}**")
        embed.set_author(name=itr.user, icon_url=itr.user.display_avatar.url)
        embed.set_image(url=self.image)
        embed.timestamp = discord.utils.utcnow()
        await itr.response.send_message(f"Heres the finished product that should be sent to {self.channel.mention if self.channel else itr.channel.mention}", embed=embed, ephemeral=True)