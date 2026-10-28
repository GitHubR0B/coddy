"""
Shared CV2 (Component V2) utilities for the bot.
Container() does NOT accept positional children: items go via .add_item().
"""

import discord
from discord.ui import LayoutView, TextDisplay, Separator, Container


def build_container(*items, accent_color=None):
    """Build a Container and add items to it via .add_item()."""
    container = Container(accent_color=accent_color)
    for item in items:
        container.add_item(item)
    return container


class CV2(LayoutView):
    """Quick helper: CV2("Title", "section1", "section2", ...)"""
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        container = build_container(
            TextDisplay(f"**{title}**"),
            *[item for s in sections for item in (Separator(visible=True), TextDisplay(str(s)))]
        )
        self.add_item(container)


def add_action_rows(container, components):
    """Safely adds components to a CV2 container across multiple ActionRows"""
    from discord.ui import ActionRow
    current_row = []
    for item in components:
        if getattr(item, 'type', None) and getattr(item.type, 'value', 0) != 2:
            if current_row:
                container.add_item(ActionRow(*current_row))
                current_row = []
            container.add_item(ActionRow(item))
        else:
            current_row.append(item)
            if len(current_row) == 5:
                container.add_item(ActionRow(*current_row))
                current_row = []
    if current_row:
        container.add_item(ActionRow(*current_row))


class CV2Embed(CV2):
    """A CV2 container that behaves like a discord.Embed.

    style="classic" (por defecto): igual que antes (separadores entre bloques).
    style="clean": sin separadores, título grande (##) y campos con ###,
                   gasta muchos menos componentes.
    """
    def __init__(self, title="", description="", **kwargs):
        self._title = title
        self._description = description or ""
        self._fields = []
        self._footer = None
        self._image = None
        self._style = kwargs.get("style", "classic")
        super().__init__(title, self._description)
        self.color = kwargs.get("color", 0xFF0000)
        self._rebuild()

    def _rebuild(self):
        self.clear_items()
        children = []

        if self._style == "clean":
            if self._title:
                children.append(TextDisplay(f"## {self._title}"))
            if self._description:
                children.append(TextDisplay(self._description))
            for name, value in self._fields:
                header = f"### {name}\n" if name else ""
                children.append(TextDisplay(f"{header}{value}"))
            if self._footer:
                children.append(TextDisplay(f"-# {self._footer}"))
        else:
            sections = [self._description] if self._description else []
            for name, value in self._fields:
                sections.append(f"**{name}**\n{value}")
            if self._footer:
                sections.append(f"*{self._footer}*")
            children.append(TextDisplay(f"**{self._title}**"))
            for s in sections:
                children.append(Separator(visible=True))
                children.append(TextDisplay(str(s)))

        if self._image:
            children.append(
                discord.ui.MediaGallery(discord.MediaGalleryItem(self._image))
            )

        self.add_item(build_container(*children, accent_color=self.color))

    def add_field(self, name, value, inline=False, **kwargs):
        self._fields.append((name, value))
        self._rebuild()
        return self

    def set_footer(self, text=None, icon_url=None, **kwargs):
        if text:
            self._footer = text
            self._rebuild()
        return self

    def set_thumbnail(self, url=None, **kwargs):
        return self

    def set_author(self, name=None, url=None, icon_url=None, **kwargs):
        return self

    def set_image(self, url=None, **kwargs):
        # CORREGIDO: antes no hacía nada. Ahora añade un MediaGallery al final.
        self._image = url
        self._rebuild()
        return self

    def to_dict(self):
        return {"title": self._title, "description": self._description}