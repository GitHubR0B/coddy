# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
import discord
from utils.emoji import CROSS, TICK
from discord.ext import commands
from discord import ui
import asyncio
from utils.Tools import *
import re


class EmbedBuilder(ui.LayoutView):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.message = None
        self.embed_data = {
            "title": "¡Edita tu embed!",
            "description": "Selecciona opciones del menú de abajo para personalizar.",
            "color": 0xFF0000,
            "thumbnail": None,
            "image": None,
            "footer_text": None,
            "footer_icon": None,
            "author_text": None,
            "author_icon": None,
            "fields": []
        }
        self.container = ui.Container(accent_color=None)
        self._build_view()
        self.add_item(self.container)

    def _get_preview(self):
        d = self.embed_data
        lines = []
        if d["title"]:
            lines.append(f"**Título:** {d['title']}")
        if d["description"]:
            lines.append(f"**Descripción:** {d['description']}")
        if d["color"]:
            lines.append(f"**Color:** `#{d['color']:06X}`")
        if d["thumbnail"]:
            lines.append(f"**Miniatura:** [Establecida]({d['thumbnail']})")
        if d["image"]:
            lines.append(f"**Imagen:** [Establecida]({d['image']})")
        if d["footer_text"]:
            lines.append(f"**Pie:** {d['footer_text']}")
        if d["footer_icon"]:
            lines.append(f"**Icono del pie:** [Establecido]({d['footer_icon']})")
        if d["author_text"]:
            lines.append(f"**Autor:** {d['author_text']}")
        if d["author_icon"]:
            lines.append(f"**Icono del autor:** [Establecido]({d['author_icon']})")
        if d["fields"]:
            for i, f in enumerate(d["fields"]):
                lines.append(f"**Campo {i+1}:** {f['name']} — {f['value']}")
        return "\n".join(lines) if lines else "Aún no hay propiedades establecidas."

    def _build_view(self):
        self.container.clear_items()

        self.container.add_item(ui.TextDisplay("# Constructor de embeds"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(self._get_preview()))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay("*Selecciona una opción para editar. Responde en 30 segundos.*"))

        # Select menu
        select = ui.Select(
            placeholder="Elige una opción para editar el embed",
            min_values=1, max_values=1,
            options=[
                discord.SelectOption(label="Título", value="Title", description="Edita el título"),
                discord.SelectOption(label="Descripción", value="Description", description="Edita la descripción"),
                discord.SelectOption(label="Agregar campo", value="Add Field", description="Agrega un campo"),
                discord.SelectOption(label="Color", value="Color", description="Edita el color (hex)"),
                discord.SelectOption(label="Miniatura", value="Thumbnail", description="Establece la URL de la miniatura"),
                discord.SelectOption(label="Imagen", value="Image", description="Establece la URL de la imagen"),
                discord.SelectOption(label="Texto del pie", value="Footer Text", description="Edita el texto del pie"),
                discord.SelectOption(label="Icono del pie", value="Footer Icon", description="Establece la URL del icono del pie"),
                discord.SelectOption(label="Texto del autor", value="Author Text", description="Edita el texto del autor"),
                discord.SelectOption(label="Icono del autor", value="Author Icon", description="Establece la URL del icono del autor"),
            ]
        )
        select.callback = self._select_callback
        self.container.add_item(ui.ActionRow(select))

        # Buttons
        send_btn = ui.Button(label="Enviar embed", emoji=TICK, style=discord.ButtonStyle.success)
        send_btn.callback = self._send_callback
        cancel_btn = ui.Button(label="Cancelar configuración", emoji=CROSS, style=discord.ButtonStyle.danger)
        cancel_btn.callback = self._cancel_callback
        self.container.add_item(ui.ActionRow(send_btn, cancel_btn))

    def _build_embed(self):
        """Build a real discord.Embed from stored data"""
        d = self.embed_data
        embed = discord.Embed(
            title=d["title"],
            description=d["description"],
            color=d["color"]
        )
        if d["thumbnail"]:
            embed.set_thumbnail(url=d["thumbnail"])
        if d["image"]:
            embed.set_image(url=d["image"])
        if d["footer_text"] or d["footer_icon"]:
            embed.set_footer(text=d["footer_text"] or "", icon_url=d["footer_icon"] or discord.Embed.Empty)
        if d["author_text"] or d["author_icon"]:
            embed.set_author(name=d["author_text"] or "", icon_url=d["author_icon"] or discord.Embed.Empty)
        for field in d["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        return embed

    async def _select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Este constructor no te pertenece.", ephemeral=True)
            return
        await interaction.response.defer()

        value = interaction.data["values"][0]

        def chk(m):
            return m.channel.id == self.ctx.channel.id and m.author.id == self.ctx.author.id

        prompts = {
            "Title": "Ingresa el **título** del embed:",
            "Description": "Ingresa la **descripción** del embed:",
            "Color": "Ingresa el color como valor hexadecimal (ej., `#FF0000`):",
            "Thumbnail": "Ingresa la **URL de la miniatura**:",
            "Image": "Ingresa la **URL de la imagen**:",
            "Footer Text": "Ingresa el **texto del pie**:",
            "Footer Icon": "Ingresa la **URL del icono del pie**:",
            "Author Text": "Ingresa el **texto del autor**:",
            "Author Icon": "Ingresa la **URL del icono del autor**:",
            "Add Field": "Ingresa el **título del campo**:",
        }

        await self.ctx.send(prompts.get(value, "Ingresa un valor:"))

        try:
            msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)

            if value == "Title":
                self.embed_data["title"] = msg.content
            elif value == "Description":
                self.embed_data["description"] = msg.content
            elif value == "Color":
                try:
                    self.embed_data["color"] = int(msg.content.strip("#"), 16)
                except ValueError:
                    await self.ctx.send("Color hexadecimal inválido. Inténtalo de nuevo.")
                    return
            elif value == "Thumbnail":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Formato de URL inválido.")
                    return
                self.embed_data["thumbnail"] = msg.content
            elif value == "Image":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Formato de URL inválido.")
                    return
                self.embed_data["image"] = msg.content
            elif value == "Footer Text":
                self.embed_data["footer_text"] = msg.content
            elif value == "Footer Icon":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Formato de URL inválido.")
                    return
                self.embed_data["footer_icon"] = msg.content
            elif value == "Author Text":
                self.embed_data["author_text"] = msg.content
            elif value == "Author Icon":
                if not msg.content.startswith("http"):
                    await self.ctx.send("Formato de URL inválido.")
                    return
                self.embed_data["author_icon"] = msg.content
            elif value == "Add Field":
                field_name = msg.content
                await self.ctx.send("Ingresa el **valor del campo**:")
                val_msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)
                self.embed_data["fields"].append({"name": field_name, "value": val_msg.content})

            # Rebuild and update
            self._build_view()
            await self.message.edit(view=self)

        except asyncio.TimeoutError:
            await self.ctx.send("Se agotó el tiempo.")

    async def _send_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Este constructor no te pertenece.", ephemeral=True)
            return
        await interaction.response.defer()

        await self.ctx.send("Menciona el **canal** donde quieres enviar este embed:")

        def chk(m):
            return m.channel.id == self.ctx.channel.id and m.author.id == self.ctx.author.id

        try:
            msg = await self.ctx.bot.wait_for("message", timeout=30, check=chk)
            chnl = msg.channel_mentions[0]
            embed = self._build_embed()
            await chnl.send(embed=embed)

            # Show success
            self.container.clear_items()
            self.container.add_item(ui.TextDisplay(f"# {TICK} Embed enviado"))
            self.container.add_item(ui.Separator())
            self.container.add_item(ui.TextDisplay(f"Embed enviado correctamente a {chnl.mention}"))
            await self.message.edit(view=self)

        except asyncio.TimeoutError:
            await self.ctx.send("Se agotó el tiempo.")
        except (IndexError, AttributeError):
            await self.ctx.send("Menciona un canal válido.")

    async def _cancel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Este constructor no te pertenece.", ephemeral=True)
            return
        self.container.clear_items()
        self.container.add_item(ui.TextDisplay("# Constructor de embeds"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(f"{CROSS} Configuración del embed cancelada."))
        await interaction.response.edit_message(view=self)
        self.stop()

    async def on_timeout(self):
        try:
            self.container.clear_items()
            self.container.add_item(ui.TextDisplay("# Constructor de embeds"))
            self.container.add_item(ui.Separator())
            self.container.add_item(ui.TextDisplay("⏰ El constructor se agotó. Usa el comando de nuevo."))
            await self.message.edit(view=self)
        except:
            pass


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="embed")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _embed(self, ctx):
        view = EmbedBuilder(ctx)
        view.message = await ctx.send(view=view)