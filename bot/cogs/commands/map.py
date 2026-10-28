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

import discord
from utils.emoji import DELETE
from discord.ext import commands
from discord import ui, ButtonStyle, SelectOption
from discord.ui import LayoutView, TextDisplay, Separator, ActionRow, MediaGallery
import requests
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import *
class MapView(LayoutView):
    def __init__(self, bot, location, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.location = location
        self.ctx = ctx
        self.zoom_level = 14
        self.map_style = 'map'
        self.map_size = '1200,900'
        self.coordinates = self.get_coordinates(location)
        self.latitude, self.longitude = None, None
        if self.coordinates != (None, None):
            self.latitude, self.longitude = float(self.coordinates[0]), float(self.coordinates[1])
        
        self.update_map()

        b_left = ui.Button(label="", emoji="⬅️", style=ButtonStyle.secondary)
        b_left.callback = self.move_left
        b_up = ui.Button(label="", emoji="⬆️", style=ButtonStyle.secondary)
        b_up.callback = self.move_up
        b_delete = ui.Button(label="", emoji=DELETE, style=ButtonStyle.danger)
        b_delete.callback = self.delete_embed
        b_down = ui.Button(label="", emoji="⬇️", style=ButtonStyle.secondary)
        b_down.callback = self.move_down
        b_right = ui.Button(label="", emoji="➡️", style=ButtonStyle.secondary)
        b_right.callback = self.move_right

        self.add_item(ActionRow(b_left, b_up, b_delete, b_down, b_right))

        b_zin = ui.Button(label="Acercar", style=ButtonStyle.primary)
        b_zin.callback = self.zoom_in
        b_zout = ui.Button(label="Alejar", style=ButtonStyle.primary)
        b_zout.callback = self.zoom_out
        b_coords = ui.Button(label="Introducir coordenadas", style=ButtonStyle.primary)
        b_coords.callback = self.enter_coordinates
        b_addr = ui.Button(label="Introducir dirección", style=ButtonStyle.success)
        b_addr.callback = self.enter_address

        self.add_item(ActionRow(b_zin, b_zout, b_coords, b_addr))

        self.add_item(ActionRow(MapStyleSelect(self)))
        self.add_item(ActionRow(MapSizeSelect(self)))

        self.build_ui()

    def build_ui(self):
        
        container = build_container(
            TextDisplay(f"**Mapa de {self.location}**"),
            Separator(visible=True),
            TextDisplay(
                f"🌐 **[Abrir en la web](https://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom={self.zoom_level})**\n"
                f"🔍 **Nivel de zoom actual:** {str(self.zoom_level)}\n"
                f"🗺️ **Estilo del mapa:** {self.map_style}\n"
                f"📏 **Tamaño del mapa:** {self.map_size}\n"
                f"📍 **Coordenadas actuales:** {self.latitude}, {self.longitude}"
            )
        )
        
        gallery = MediaGallery()
        gallery.add_item(media=self.map_url)
        container.add_item(gallery)
        
        
        self.children = [c for c in self.children if not isinstance(c, type(container))]
        self.add_item(container)


    def get_coordinates(self, location):
        try:
            headers = {'User-Agent': f'{BRAND_NAME} Bot (https://codexdevs.in)'}
            response = requests.get(f'https://nominatim.openstreetmap.org/search?q={location}&format=json', headers=headers)
            response.raise_for_status()
            data = response.json()[0]
            return data['lat'], data['lon']
        except (requests.RequestException, IndexError) as e:
            print(f"Failed to get coordinates: {e}")
            return None, None

    def update_map(self):
        if self.latitude is None or self.longitude is None:
            return
        self.map_url = f'https://www.mapquestapi.com/staticmap/v5/map?key=E2SaL3qiTpXQ43nxZFBp0wzEnBI6pqbG&center={self.latitude},{self.longitude}&zoom={self.zoom_level}&size={self.map_size}&type={self.map_style}'
        self.build_ui()

    async def update_embed(self, interaction: discord.Interaction):
        if self.latitude is None or self.longitude is None:
            await interaction.response.send_message("No se pudieron obtener los datos del mapa. Inténtalo de nuevo.", ephemeral=True)
            return
        
        try:
            await interaction.message.edit(view=self)
        except Exception as e:
            await interaction.response.send_message(f"Error al actualizar el mensaje: {e}", ephemeral=True)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                view=CV2("⚠️ Acceso denegado", "Lo siento, solo el autor que lo solicitó puede controlar esto"),
                ephemeral=True
            )
            return False
        return True

    async def move_left(self, interaction: discord.Interaction):
        if self.longitude is not None:
            self.longitude -= 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Movido a la izquierda."), ephemeral=True)
    
    async def move_up(self, interaction: discord.Interaction):
        if self.latitude is not None:
            self.latitude += 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Movido hacia arriba."), ephemeral=True)

    async def delete_embed(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception as e:
            await interaction.response.send_message(f"Error al eliminar el mensaje: {e}", ephemeral=True)

    async def move_down(self, interaction: discord.Interaction):
        if self.latitude is not None:
            self.latitude -= 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Movido hacia abajo."), ephemeral=True)

    async def move_right(self, interaction: discord.Interaction):
        if self.longitude is not None:
            self.longitude += 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Movido a la derecha."), ephemeral=True)
    
    async def zoom_in(self, interaction: discord.Interaction):
        print("Zooming in")
        self.zoom_level = min(self.zoom_level + 1, 18)
        self.update_map()
        await self.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Zoom aumentado."), ephemeral=True)

    async def zoom_out(self, interaction: discord.Interaction):
        print("Zooming out")
        self.zoom_level = max(self.zoom_level - 1, 0)
        self.update_map()
        await self.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Zoom reducido."), ephemeral=True)

    async def enter_coordinates(self, interaction: discord.Interaction):
        await interaction.response.send_message("Introduce las coordenadas (latitud, longitud):", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            coords_msg = await self.bot.wait_for('message', check=check, timeout=60)
            coords = coords_msg.content.split(',')
            if len(coords) == 2:
                self.latitude, self.longitude = float(coords[0].strip()), float(coords[1].strip())
                self.update_map()
                await self.update_embed(interaction)
                await interaction.followup.send(view=CV2("✅ Mapa actualizado", "Coordenadas actualizadas."), ephemeral=True)
            else:
                await interaction.followup.send("Formato de coordenadas inválido. Introdúcelas en el formato 'latitud, longitud'.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tardaste demasiado en responder. Inténtalo de nuevo.", ephemeral=True)

    async def enter_address(self, interaction: discord.Interaction):
        await interaction.response.send_message("Introduce la dirección:", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            address_msg = await self.bot.wait_for('message', check=check, timeout=60)
            address = address_msg.content
            self.coordinates = self.get_coordinates(address)
            if self.coordinates == (None, None):
                await interaction.followup.send("No se pudieron obtener las coordenadas de la dirección. Inténtalo de nuevo.", ephemeral=True)
            else:
                self.latitude, self.longitude = float(self.coordinates[0]), float(self.coordinates[1])
                self.location = address
                self.update_map()
                await self.update_embed(interaction)
                await interaction.followup.send(view=CV2("✅ Mapa actualizado", "Dirección actualizada."), ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tardaste demasiado en responder. Inténtalo de nuevo.", ephemeral=True)


class MapStyleSelect(ui.Select):
    def __init__(self, map_view):
        super().__init__(placeholder='Selecciona el estilo del mapa')
        self.map_view = map_view  
        options = [
            SelectOption(label='Mapa', value='map'),
            SelectOption(label='Satélite', value='sat'),
            SelectOption(label='Híbrido', value='hyb'),
            SelectOption(label='Claro', value='light'),
            SelectOption(label='Oscuro', value='dark'),
        ]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        print(f"Changing map style to {self.values[0]}")
        self.map_view.map_style = self.values[0]
        self.map_view.update_map()
        await self.map_view.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Estilo del mapa actualizado correctamente."), ephemeral=True)

class MapSizeSelect(ui.Select):
    def __init__(self, map_view):
        super().__init__(placeholder='Selecciona el tamaño del mapa')
        self.map_view = map_view  
        options = [
            SelectOption(label='400x300', value='400,300'),
            SelectOption(label='800x600', value='800,600'),
            SelectOption(label='1200x900', value='1200,900')
        ]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        print(f"Changing map size to {self.values[0]}")
        self.map_view.map_size = self.values[0]
        self.map_view.update_map()
        await self.map_view.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Mapa actualizado", "Tamaño del mapa actualizado correctamente."), ephemeral=True)


class Map(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="map", help="Muestra un mapa de una ubicación", usage="<location>", description="Muestra un mapa de una ubicación")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def map(self, ctx, *, location: str):
        view = MapView(self.bot, location, ctx)
        if view.coordinates == (None, None):
            await ctx.send(view=CV2("❌ Error", "No se pudieron obtener las coordenadas de la ubicación. Inténtalo de nuevo."))
            return
        await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Map(bot))
