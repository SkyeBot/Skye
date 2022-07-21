import discord
from discord import ui
from discord.ext import menus
from discord.ext import commands

class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None

    async def show_page(self, page_number, interaction):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await interaction.response.edit_message(**kwargs)

    
    async def show_checked_page(self, page_number, interaction):
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number, interaction)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number, interaction)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.defer()
        await interaction.followup.send(f"You cant use this as you're not the command invoker, only the author (<@{self.ctx.author.mention}>) Can Do This!", ephemeral=True)
        return False
    # This is extremely similar to Custom MenuPages(I will not explain these)
    @ui.button(emoji='⏮️', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await self.show_page(0, interaction)

    @ui.button(emoji='◀️', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await self.show_checked_page(self.current_page - 1, interaction)
    
    @ui.button(emoji='⏹️', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        self.stop()
        for item in self.children:
            item.disabled = True

        # Step 3
        await self.message.edit(view=self)
        

    @ui.button(emoji='▶️', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await self.show_checked_page(self.current_page + 1, interaction)

    @ui.button(emoji='⏭️', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await self.show_page(self._source.get_max_pages() - 1, interaction)

class MySource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        embed = discord.Embed(
            description=f"This is number {entries}.", 
            color=discord.Colour.random()
        )
        embed.set_footer(text=f"Requested by {menu.ctx.author}")
        return embed

class aa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test_menus(self,ctx):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        formatter = MySource(data, per_page=1) # MySource came from Custom MenuPages subtopic. [Please refer to that]
        menu = MyMenuPages(formatter)
        await menu.start(ctx)

async def setup(bot):
    await bot.add_cog(aa(bot))