import discord
from utils.Tools import *
from utils.cv2 import build_container
from utils.emoji import PREVIOUS, NEXT, HOME
from discord.ui import LayoutView, TextDisplay, ActionRow

# Discord limita el texto total de un mensaje Components V2 (~4000 caracteres).
# Las categorías largas se parten en varias páginas de este tamaño.
CHUNK_LIMIT = 3000


class Dropdown(discord.ui.Select):

    def __init__(self, ctx, options, placeholder="Elige una categoría de ayuda"):
        super().__init__(placeholder=placeholder,
                         min_values=1,
                         max_values=1,
                         options=options)
        self.invoker = ctx.author

    async def callback(self, interaction: discord.Interaction):
        if self.invoker == interaction.user:
            index = self.view.find_index_from_select(self.values[0])
            await self.view.set_page(index or 0, interaction)
        else:
            await interaction.response.send_message(
                "Debes ejecutar este comando para interactuar con él.", ephemeral=True)


class View(LayoutView):

    def __init__(self, mapping: dict, ctx, homeembed, ui: int):
        super().__init__(timeout=None)
        self.mapping = mapping
        self.ctx = ctx
        self.index = 0
        self.current_page = 0
        self.ui = ui
        self.label_to_index = {}
        self.color = getattr(homeembed, "color", None) or 0xFFE000

        self.options, self.pages, self.total_pages = self.gen_pages(homeembed)
        self._rebuild()

    # ------------------------------------------------------------------ UI
    def _rebuild(self):
        self.clear_items()
        page = self.pages[self.index]
        items = []

        # Texto (sin separadores, estilo "clean")
        if page.get('title'):
            items.append(TextDisplay(f"## {page['title']}"))
        if page.get('description'):
            items.append(TextDisplay(page['description']))
        for name, value in page.get('fields', []):
            header = f"### {name}\n" if name else ""
            items.append(TextDisplay(f"{header}{value}"))
        if page.get('body'):
            items.append(TextDisplay(page['body']))

        # Banner (solo en Inicio)
        if page.get('image'):
            items.append(discord.ui.MediaGallery(discord.MediaGalleryItem(page['image'])))

        # Navegación: SOLO aparece si la categoría ocupa más de una página
        start, end = page.get('group', (self.index, self.index))
        if end > start:
            prevB = discord.ui.Button(emoji=PREVIOUS, style=discord.ButtonStyle.secondary,
                                      disabled=self.index <= start)
            nextB = discord.ui.Button(emoji=NEXT, style=discord.ButtonStyle.secondary,
                                      disabled=self.index >= end)
            prevB.callback = self._back_cb
            nextB.callback = self._next_cb
            items.append(TextDisplay(f"-# Página {self.index - start + 1}/{end - start + 1}"))
            items.append(ActionRow(prevB, nextB))

        # Select de secciones (se mantiene)
        if self.ui == 2:
            mid = len(self.options) // 2
            o1, o2 = self.options[:mid], self.options[mid:]
            if o1:
                items.append(ActionRow(Dropdown(ctx=self.ctx, options=o1, placeholder="Comandos principales")))
            if o2:
                items.append(ActionRow(Dropdown(ctx=self.ctx, options=o2, placeholder="Comandos extra")))
        else:
            items.append(ActionRow(Dropdown(ctx=self.ctx, options=self.options[:25])))

        self.add_item(build_container(*items, accent_color=self.color))

    async def _check(self, interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "Debes ejecutar este comando para interactuar con él.", ephemeral=True)
            return False
        return True

    async def _back_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(self.index - 1, interaction)

    async def _next_cb(self, interaction):
        if await self._check(interaction):
            await self.set_page(self.index + 1, interaction)

    def find_index_from_select(self, value):
        return self.label_to_index.get(value, 0)

    def get_cogs(self):
        return list(self.mapping.keys())

    # ------------------------------------------------------------- páginas
    @staticmethod
    def _chunk(blocks, limit=CHUNK_LIMIT, sep="\n\n"):
        chunks, current, size = [], [], 0
        for block in blocks:
            if current and size + len(block) + len(sep) > limit:
                chunks.append(sep.join(current))
                current, size = [], 0
            current.append(block)
            size += len(block) + len(sep)
        if current:
            chunks.append(sep.join(current))
        return chunks or ["Sin comandos disponibles."]

    def gen_pages(self, homeembed):
        options, pages = [], []
        used_labels = set()

        options.append(discord.SelectOption(label="Inicio", emoji=HOME, description="Panel principal"))
        self.label_to_index["Inicio"] = 0

        # Página de inicio a partir del CV2Embed
        if hasattr(homeembed, '_title'):
            home_page = {
                'title': homeembed._title or '',
                'description': homeembed._description or '',
                'fields': list(getattr(homeembed, '_fields', [])),
                'image': getattr(homeembed, '_image', None),
            }
        else:
            home_page = {
                'title': getattr(homeembed, 'title', '') or '',
                'description': getattr(homeembed, 'description', '') or '',
                'fields': [(f.name, f.value) for f in homeembed.fields] if getattr(homeembed, 'fields', None) else [],
                'image': getattr(getattr(homeembed, 'image', None), 'url', None),
            }
        home_page['group'] = (0, 0)
        pages.append(home_page)
        used_labels.add("Inicio")

        prefix = getattr(self.ctx, "prefix", "") or ""

        for cog in self.get_cogs():
            if cog.__class__.__name__ == "Roleplay":
                continue
            if "help_custom" not in dir(cog):
                continue

            emoji, label, description = cog.help_custom()
            original_label = label
            counter = 1
            while label in used_labels:
                label = f"{original_label} {counter}"
                counter += 1
            used_labels.add(label)
            options.append(discord.SelectOption(label=label, emoji=emoji, description=description))

            # Un bloque por comando con su ayuda COMPLETA (sin cortar)
            lines = []
            for command in cog.get_commands():
                params = "".join(f" <{p}>" for p in command.clean_params if p not in ("self", "ctx"))
                help_text = (command.help or "Sin descripción disponible").strip()
                if len(help_text) > 1000:
                    help_text = help_text[:997] + "..."
                lines.append(f"**`{prefix}{command.name}{params}`**\n{help_text}")

            chunks = self._chunk(lines)
            first = len(pages)
            last = first + len(chunks) - 1
            self.label_to_index[label] = first
            for chunk in chunks:
                pages.append({
                    'title': f"{emoji} {original_label}",
                    'description': '',
                    'fields': [],
                    'body': chunk,
                    'group': (first, last),
                })

        return options, pages, len(pages)

    async def set_page(self, page, interaction):
        self.index = max(0, min(page, len(self.pages) - 1))
        self.current_page = self.index
        self._rebuild()
        await interaction.response.edit_message(view=self)