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
from utils.emoji import CROSS, EMOTE, TICK, ZSAFE, ZSETTINGS
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, Container, Button, ActionRow
import aiosqlite
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import *




class Antinuke(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.bot.loop.create_task(self.initialize_db())

  async def initialize_db(self):
    self.db = await aiosqlite.connect('db/anti.db')
    await self.db.execute('''
        CREATE TABLE IF NOT EXISTS antinuke (
            guild_id INTEGER PRIMARY KEY,
            status BOOLEAN
        )
    ''')
    await self.db.commit()

    
  async def enable_limit_settings(self, guild_id):
    default_limits = DEFAULT_LIMITS
    for action, limit in default_limits.items():
      await self.db.execute('INSERT OR REPLACE INTO limit_settings (guild_id, action_type, action_limit, time_window) VALUES (?, ?, ?, ?)', (guild_id, action, limit, TIME_WINDOW))
      await self.db.commit()

  async def disable_limit_settings(self, guild_id):
    await self.db.execute('DELETE FROM limit_settings WHERE guild_id = ?', (guild_id,))
    await self.db.commit()


  @commands.hybrid_command(name='antinuke', aliases=['antiwizz', 'anti'], help="Activa o desactiva el módulo Anti-Nuke en el servidor")
  
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 4, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def antinuke(self, ctx, option: str = None):
    guild_id = ctx.guild.id
    pre=ctx.prefix

    async with self.db.execute('SELECT status FROM antinuke WHERE guild_id = ?', (guild_id,)) as cursor:
      row = await cursor.fetchone()

    async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

    is_owner = ctx.author.id == ctx.guild.owner_id
    if not is_owner and not check:
      view = CV2(f"{CROSS} Acceso denegado", "¡Solo el propietario del servidor o un propietario extra puede ejecutar este comando!")
      return await ctx.send(view=view)

    is_activated = row[0] if row else False

    if option is None:
      view = CV2(
        f"{ZSAFE} {BRAND_NAME} Security",
        "**Modo de defensa Antinuke** — Protege tu servidor de acciones administrativas dañinas con protocolos de seguridad automatizados e inteligentes.",
        "**Funciones principales**\n"
        "• Banea automáticamente las actividades administrativas maliciosas al instante.\n"
        "• Protección de lista blanca para usuarios de confianza.\n"
        "• Supervisión en tiempo real de las acciones administrativas.\n"
        "• Detección y neutralización rápida de amenazas.",
        "**Panel de configuración**\n"
        f"{TICK} Activar protección: `antinuke enable`\n"
        f"{CROSS} Desactivar protección: `antinuke disable`"
      )
      await ctx.send(view=view)

    elif option.lower() == 'enable':
      if is_activated:
        view = CV2(
          f"Configuración de seguridad de {ctx.guild.name}",
          f"Tu servidor __**ya tiene Antinuke activado.**__\n\nEstado actual: {TICK} Activado\nPara desactivarlo usa `antinuke disable`"
        )
        await ctx.send(view=view)
      else:
        
        setup_view = CV2(f"Configuración de Antinuke {EMOTE}", f"{TICK} | ¡Iniciando configuración rápida!")
        setup_message = await ctx.send(view=setup_view)

        
        if not ctx.guild.me.guild_permissions.administrator:
          view = CV2(f"Configuración de Antinuke {EMOTE}",
            f"{TICK} | ¡Iniciando configuración rápida!\n"
            f"{CROSS} | **¡Ups! Parece que no tengo permiso de Administrador para activar Antinuke**.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        view = CV2(f"Configuración de Antinuke {EMOTE}",
          f"{TICK} | ¡Iniciando configuración rápida!\n"
          f"{TICK} Comprobando la posición del rol de {BRAND_NAME} para una configuración óptima...")
        await setup_message.edit(view=view)

        await asyncio.sleep(1)
        view = CV2(f"Configuración de Antinuke {EMOTE}",
          f"{TICK} | ¡Iniciando configuración rápida!\n"
          f"{TICK} Comprobando la posición del rol de {BRAND_NAME} para una configuración óptima...\n"
          f"{TICK} | Creando y configurando el rol {BRAND_NAME} Supreme...")
        await setup_message.edit(view=view)
        
        try:
          role = await ctx.guild.create_role(
            name=f"{BRAND_NAME} Supreme™",
            color=0xFF0000,
            permissions=discord.Permissions(administrator=True),
            hoist=False,
            mentionable=False,
            reason="Creación del rol de configuración de Antinuke"
          )
          await ctx.guild.me.add_roles(role)
        except discord.Forbidden:
          view = CV2("Configuración de Antinuke", f"{CROSS} | **¡Vaya! No tengo permisos para activar Antinuke**.")
          await setup_message.edit(view=view)
          return
        except discord.HTTPException as e:
          view = CV2("Configuración de Antinuke", f"{CROSS} | **Error: HTTPException: {e}\nRevisa el registro de auditoría del servidor**.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        view = CV2(f"Configuración de Antinuke {EMOTE}",
          f"{TICK} | ¡Iniciando configuración rápida!\n"
          f"{TICK} Comprobando la posición del rol de {BRAND_NAME}...\n"
          f"{TICK} | Creando el rol {BRAND_NAME} Supreme...\n"
          f"{TICK} | Asegurando la ubicación precisa del rol {BRAND_NAME} Supreme™...")
        await setup_message.edit(view=view)

        try:
          await ctx.guild.edit_role_positions(positions={role: 1})
        except discord.Forbidden:
          view = CV2("Configuración de Antinuke", f"{CROSS} | ¡Ups! No tengo permisos suficientes para mover el rol.")
          await setup_message.edit(view=view)
          return
        except discord.HTTPException as e:
          view = CV2("Configuración de Antinuke", f"{CROSS} | La configuración falló: HTTPException: {e}.")
          await setup_message.edit(view=view)
          return

        await asyncio.sleep(1)
        await asyncio.sleep(1)

        await self.db.execute('INSERT OR REPLACE INTO antinuke (guild_id, status) VALUES (?, ?)', (guild_id, True))
        await self.db.commit()

        await asyncio.sleep(1)
        await setup_message.delete()

        modules = (
          f"{TICK} **Anti baneos**\n"
          f"{TICK} **Anti expulsiones**\n"
          f"{TICK} **Anti bots**\n"
          f"{TICK} **Anti creación de canales**\n"
          f"{TICK} **Anti eliminación de canales**\n"
          f"{TICK} **Anti actualización de canales**\n"
          f"{TICK} **Anti menciones @everyone/Here**\n"
          f"{TICK} **Anti creación de roles**\n"
          f"{TICK} **Anti eliminación de roles**\n"
          f"{TICK} **Anti actualización de roles**\n"
          f"{TICK} **Anti actualización de miembros**\n"
          f"{TICK} **Anti actualización del servidor**\n"
          f"{TICK} **Anti integraciones**\n"
          f"{TICK} **Anti creación de webhooks**\n"
          f"{TICK} **Anti eliminación de webhooks**\n"
          f"{TICK} **Anti actualización de webhooks**\n"
          f"{TICK} **Anti purga**\n"
          f"{TICK} **Recuperación automática**"
        )

        punishment_btn = Button(label="Mostrar tipo de castigo", style=discord.ButtonStyle.secondary)
        punishment_btn.callback = self._show_punishment

        result_view = LayoutView(timeout=None)
        result_view.add_item(
          build_container(
            TextDisplay(f"**{ZSETTINGS} Ajustes de seguridad de {ctx.guild.name}**"),
            Separator(visible=True),
            TextDisplay("Consejo: Para un funcionamiento óptimo, asegúrate de que mi rol tenga permisos de **Administración** y esté colocado en la **parte superior** de la lista de roles."),
            Separator(visible=True),
            TextDisplay(f"**Módulos activados**\n{modules}"),
            Separator(visible=True),
            TextDisplay(f"Antinuke activado correctamente | Desarrollado por {BRAND_NAME} Development™"),
            ActionRow(punishment_btn)
          )
        )

        await ctx.send(view=result_view)

    elif option.lower() == 'disable':
      if not is_activated:
        view = CV2(
          f"Configuración de seguridad de {ctx.guild.name}",
          f"Vaya, parece que tu servidor no ha activado Antinuke.\n\nEstado actual: {CROSS} Desactivado\n\nPara activarlo usa `antinuke enable`"
        )
      else:
        await self.db.execute('DELETE FROM antinuke WHERE guild_id = ?', (guild_id,))
        await self.db.commit()
        view = CV2(
          f"Configuración de seguridad de {ctx.guild.name}",
          f"Antinuke ha sido desactivado correctamente en este servidor.\n\nEstado actual: {CROSS} Desactivado\n\nPara activarlo usa `antinuke enable`"
        )
      await ctx.send(view=view)
    else:
      view = CV2(f"{CROSS} Error", "Opción no válida. Usa `enable` o `disable`.")
      await ctx.send(view=view)

  async def _show_punishment(self, interaction: discord.Interaction):
    view = CV2(
      "Tipos de castigo para administradores/moderadores no incluidos en la lista blanca",
      "**Anti baneos:** Banear\n"
      "**Anti expulsiones:** Banear\n"
      "**Anti bots:** Banear al invitador del bot\n"
      "**Anti creación/eliminación/actualización de canales:** Banear\n"
      "**Anti menciones @everyone/Here:** Eliminar el mensaje y silenciar 1 hora\n"
      "**Anti creación/eliminación/actualización de roles:** Banear\n"
      "**Anti actualización de miembros:** Banear\n"
      "**Anti actualización del servidor:** Banear\n"
      "**Anti integraciones:** Banear\n"
      "**Anti creación/eliminación/actualización de webhooks:** Banear\n"
      "**Anti purga:** Banear\n"
      "**Recuperación automática:** Recupera automáticamente canales, roles y ajustes dañados",
      "Nota: En el caso de las actualizaciones de miembros, solo se tomarán medidas si el rol contiene permisos peligrosos como Banear miembros, Administrador, Gestionar servidor, Gestionar canales, Gestionar roles, Gestionar webhooks o Mencionar a todos"
    )
    await interaction.response.send_message(view=view, ephemeral=True)
