import contextlib
import typing
from discord import ui
import discord
import wavelink
from discord.ext import menus
from utils.context import Context


class Pages(
    ui.View
):  # Took some of this from the pagination tutorial + robodanny's paginator <3
    def __init__(self, source: menus.PageSource, *, ctx: discord.Interaction):
        super().__init__(timeout=None)
        self._source = source
        self.current_page = 0
        self.ctx: Context = ctx
        self.message = None

    async def show_page(self, page_number, interaction):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await interaction.response.edit_message(**kwargs)

    async def show_checked_page(self, page_number, interaction: discord.Interaction):
        max_pages = self._source.get_max_pages()
        with contextlib.suppress(IndexError):
            if max_pages is None or max_pages > page_number >= 0:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number, interaction)
            elif max_pages >= page_number:
                await interaction.response.send_message(
                    "You're at the end of the paginator!", ephemeral=True
                )

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx: discord.Interaction = ctx
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self.message = await self.ctx.message.edit(**kwargs, view=self)

    async def _get_kwargs_from_page(self, page: int) -> typing.Dict[str, typing.Any]:
        value = await discord.utils.maybe_coroutine(
            self._source.format_page, self, page
        )
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"embed": value, "content": None}
        else:
            return {}

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.user.id:
            return True
        await interaction.response.defer()
        await interaction.followup.send(
            f"You cant use this as you're not the command invoker, only the author ({self.ctx.user.mention}) Can Do This!",
            ephemeral=True,
        )
        return False

    # This is extremely similar to Custom MenuPages(I will not explain these)
    @ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await self.show_page(0, interaction)

    @ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction, button):
        await self.show_checked_page(self.current_page - 1, interaction)

    @ui.button(emoji="⏹️", style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction: discord.Interaction, button):
        await interaction.response.defer()
        self.stop()
        for item in self.children:
            item.disabled = True

        # Step 3
        await self.message.edit(view=self)

    @ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction, button):
        await self.show_checked_page(self.current_page + 1, interaction)

    @ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await self.show_page(self._source.get_max_pages() - 1, interaction)


class MusicPageSource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        stuff = [f"{count + 1}: {song} by {song.author}" for count, song in enumerate(entries, start=-0)]

        current_playing = menu.vc.source.title

        menu.embed = discord.Embed(
            title=f"Current queue for {menu.ctx.guild}",
            description=f"Current Playing: {current_playing} - {menu.vc.source.author}\n"
            + "\n".join(stuff),
        )
        return menu.embed


class MusicPages(Pages):
    """A simple pagination session reminiscent of the old Pages interface.
    Basically an embed with some normal formatting.
    """

    def __init__(
        self,
        entries,
        *,
        ctx: discord.Interaction,
        vc: wavelink.Player,
        per_page: int = 12,
    ):
        super().__init__(MusicPageSource(entries, per_page=per_page), ctx=ctx)
        self.embed = discord.Embed()
        self.ctx = ctx
        self.vc = vc


class SimplePageSource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        e = discord.Embed()
        menu.embed.description = "\n".join(entries)
        return menu.embed


class SimplePages(Pages):
    """A simple pagination session reminiscent of the old Pages interface.
    Basically an embed with some normal formatting.
    """

    def __init__(
        self,
        entries,
        *,
        ctx: discord.Interaction,
        embed: discord.Embed,
        per_page: int = 12,
    ):
        super().__init__(SimplePageSource(entries, per_page=per_page), ctx=ctx)
        self.embed = discord.Embed()
