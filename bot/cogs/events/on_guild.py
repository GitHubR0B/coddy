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

from discord.ext import commands
from core import zyrox, Cog
import discord
from utils.emoji import ARROWRED, KING, ZBOT, ZHUMAN, ZROCKET
import logging
from discord.ui import View, Button, Select
from utils.config import *

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)

client = zyrox()


class Guild(Cog):
    def __init__(self, client: zyrox):
        self.client = client
        self.recently_removed_guilds = set()
        self._removal_timestamps = {}

    @client.event
    @commands.Cog.listener(name="on_guild_join")
    async def on_guild_add(self, guild):
        try:
            rope = [
                inv
                for inv in await guild.invites()
                if inv.max_age == 0 and inv.max_uses == 0
            ]
            ch = 1396794297386532978
            me = self.client.get_channel(ch)
            if me is None:
                logging.error(f"Channel with ID {ch} not found.")
                return

            channels = len(set(self.client.get_all_channels()))
            embed = discord.Embed(title=f"Información de {guild.name}", color=0xFF0000)

            embed.set_author(name="Servidor añadido")
            embed.set_footer(text=f"Añadido en {guild.name}")

            embed.add_field(
                name="**__Acerca de__**",
                value=f"**Nombre : ** {guild.name}\n**ID :** {guild.id}\n**Propietario {KING}  :** {guild.owner} (<@{guild.owner_id}>)\n**Creado el : **{guild.created_at.month}/{guild.created_at.day}/{guild.created_at.year}\n**Miembros :** {len(guild.members)}",
                inline=False,
            )
            embed.add_field(
                name="**__Descripción__**",
                value=f"""{guild.description}""",
                inline=False,
            )
            embed.add_field(
                name="**__Miembros__**",
                value=f"""{ZROCKET} Miembros : {len(guild.members)}\n {ZHUMAN} Humanos : {len(list(filter(lambda m: not m.bot, guild.members)))}\n {ZBOT} Bots : {len(list(filter(lambda m: m.bot, guild.members)))}
                """,
                inline=False,
            )
            embed.add_field(
                name="**__Canales__**",
                value=f"""
Categorías : {len(guild.categories)}
Canales de texto : {len(guild.text_channels)}
Canales de voz : {len(guild.voice_channels)}
Hilos : {len(guild.threads)}
                """,
                inline=False,
            )
            embed.add_field(
                name="__Estadísticas del bot:__",
                value=f"Servidores: `{len(self.client.guilds)}`\nUsuarios: `{len(self.client.users)}`\nCanales: `{channels}`",
                inline=False,
            )

            if guild.icon is not None:
                embed.set_thumbnail(url=guild.icon.url)

            embed.timestamp = discord.utils.utcnow()
            await me.send(
                f"{rope[0]}" if rope else "No se encontró ninguna invitación precreada", embed=embed
            )

            if not guild.chunked:
                await guild.chunk()

            embed = discord.Embed(
                description=f"{ARROWRED} El prefijo de este servidor es `>`\n{ARROWRED} Empieza con `>help`\n{ARROWRED} Para guías detalladas, preguntas frecuentes e información, visita nuestro sitio web",
                color=0xFF0000,
            )
            embed.set_author(
                name="¡Gracias por añadirme!", icon_url=self.bot.user.display_avatar.url
            )
            embed.set_footer(
                text=f"Desarrollado por {BRAND_NAME}™",
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            # Botón de enlaces web y dashboard
            website_button = Button(
                label="Web",
                style=discord.ButtonStyle.link,
                url="https://soycoddy.es/",
            )
            dashboard_button = Button(
                label="Dashboard",
                style=discord.ButtonStyle.link,
                url="https://soycoddy.es/dashboard",
            )

            view = View()
            view.add_item(website_button)
            view.add_item(dashboard_button)
            channel = discord.utils.get(guild.text_channels, name="general")
            if not channel:
                channels = [
                    channel
                    for channel in guild.text_channels
                    if channel.permissions_for(guild.me).send_messages
                ]
                if channels:
                    channel = channels[0]
                else:
                    logging.error(
                        f"No channel found with send permissions in guild: {guild.name}"
                    )
                    return

            await channel.send(embed=embed, view=view)

        except Exception as e:
            logging.error(f"Error in on_guild_join: {e}")

    @client.event
    @commands.Cog.listener(name="on_guild_remove")
    async def on_guild_remove(self, guild):
        import time

        current_time = time.time()

        if guild.id in self.recently_removed_guilds:
            last_removal = self._removal_timestamps.get(guild.id, 0)
            if current_time - last_removal < 60:
                return

        self.recently_removed_guilds.add(guild.id)
        self._removal_timestamps[guild.id] = current_time

        if len(self.recently_removed_guilds) > 100:
            self.recently_removed_guilds.clear()

        try:
            ch = 1396794297386532978
            idk = self.client.get_channel(ch)
            if idk is None:
                logging.error(f"Channel with ID {ch} not found.")
                return

            channels = len(set(self.client.get_all_channels()))
            embed = discord.Embed(title=f"Información de {guild.name}", color=0xFF0000)

            embed.set_author(name="Servidor eliminado")
            embed.set_footer(text=f"{guild.name}")

            embed.add_field(
                name="**__Acerca de__**",
                value=f"**Nombre : ** {guild.name}\n**ID :** {guild.id}\n**Propietario {KING} :** {guild.owner} (<@{guild.owner_id}>)\n**Creado el : **{guild.created_at.month}/{guild.created_at.day}/{guild.created_at.year}\n**Miembros :** {len(guild.members)}",
                inline=False,
            )
            embed.add_field(
                name="**__Descripción__**",
                value=f"""{guild.description}""",
                inline=False,
            )

            embed.add_field(
                name="**__Miembros__**",
                value=f"""
Miembros : {len(guild.members)}
Humanos : {len(list(filter(lambda m: not m.bot, guild.members)))}
Bots : {len(list(filter(lambda m: m.bot, guild.members)))}
                """,
                inline=False,
            )
            embed.add_field(
                name="**__Canales__**",
                value=f"""
Categorías : {len(guild.categories)}
Canales de texto : {len(guild.text_channels)}
Canales de voz : {len(guild.voice_channels)}
Hilos : {len(guild.threads)}
                """,
                inline=False,
            )
            embed.add_field(
                name="__Estadísticas del bot:__",
                value=f"Servidores: `{len(self.client.guilds)}`\nUsuarios: `{len(self.client.users)}`\nCanales: `{channels}`",
                inline=False,
            )

            if guild.icon is not None:
                embed.set_thumbnail(url=guild.icon.url)

            embed.timestamp = discord.utils.utcnow()
            await idk.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in on_guild_remove: {e}")


# client.add_cog(Guild(client))
