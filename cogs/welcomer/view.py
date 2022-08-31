import discord

class ImageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set Image!", custom_id="ImageModal!")

    url = discord.ui.TextInput(label="url", style=discord.TextStyle.paragraph, custom_id="ImageUrl", placeholder="Insert Image URL here")

    async def on_submit(self, itr: discord.Interaction):
        pass
    



class WelcomerConfigView(discord.ui.View):
    def __init__(self):
        pass

    @discord.ui.button()
    async def image(self, itr: discord.Interaction, button: discord.Button):
       modal = ImageModal()
    
