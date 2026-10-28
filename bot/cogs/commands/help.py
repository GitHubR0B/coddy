# ╔══════════════════════════════════════════════════════════════════╗
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from utils.emoji import ARROWRED, BOOST, CAST, GAMES, LEVEL_UP, LOADINGRED, LOCK, MESSAGE, MINECRAFT, MUSIC, NEW, PIN, SEED, STAR, SWORD, SYSTEM, THUNDER, TICKET, WIFI, ZAI, ZARROW, ZBAN, ZBOT, ZCIRCLE, ZCIRCLE_ALT1, ZCLOUD, ZCOUNTING, ZMODULE, ZPEOPLE, ZROCKET, ZSAFE, ZTADA, ZUNMUTE, ZWRENCH
from discord.ext import commands
from discord import app_commands, Interaction
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.zyrox import zyrox
from core.Cog import Cog
from utils.Tools import ignore_check, get_ignore_data, blacklist_check, getConfig
from utils.config import BRAND_NAME
from utils.cv2 import CV2, CV2Embed
from itertools import chain
import json
from utils import help as vhelp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import asyncio

color = 0xFF0000
client = zyrox()

from utils.config import BotName


class HelpCommand(commands.HelpCommand):

  async def send_ignore_message(self, ctx, ignore_type: str):
    if ignore_type == "channel":
      await ctx.reply("Este canal está ignorado.", mention_author=False)
    elif ignore_type == "command":
      await ctx.reply(f"{ctx.author.mention} Este comando, canal o tú estáis ignorados aquí.", delete_after=6)
    elif ignore_type == "user":
      await ctx.reply("Estás ignorado.", mention_author=False)

  async def on_help_command_error(self, ctx, error):
    # CORREGIDO: `error.original` solo existe en CommandInvokeError
    original = getattr(error, "original", error)

    if isinstance(error, commands.CommandOnCooldown):
      return

    known = (commands.CommandNotFound, discord.HTTPException, commands.CommandInvokeError)
    if not isinstance(error, known):
      await self.context.reply(f"Ocurrió un error desconocido\n{original}",
                               mention_author=False)
      return

    return await super().on_help_command_error(ctx, error)

  async def command_not_found(self, string: str) -> None:
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
    matches = get_close_matches(string, cmds)

    embed = CV2Embed(
        title=f"Ayuda de {BotName}",
        description=f">>> **¡Ups! No se encontró ningún comando con el nombre** `{string}`.",
        color=0xFF0000
    )

    await ctx.reply(view=embed, mention_author=True)

  async def send_bot_help(self, mapping):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    # Mensaje de carga
    loading_embed = CV2(f"{LOADINGRED} Cargando menú de ayuda...")
    loading_msg = await ctx.reply(view=loading_embed)

    await asyncio.sleep(2)

    with suppress(discord.NotFound):
      await loading_msg.delete()

    bot = self.context.bot
    user_id = bot.user.id

    # TODO: pon aquí tus enlaces reales
    SUPPORT_URL = "https://discord.gg/TU_INVITE"
    TOPGG_URL = "https://top.gg/bot/7737377"
    DCBOTLIST_URL = "https://discordbotlist.com/bots/coddy"
    INVITE_URL = (
        f"https://discord.com/api/oauth2/authorize?client_id={user_id}"
        f"&permissions=8&scope=bot%20applications.commands"
    )

    total_guilds = len(bot.guilds)
    total_cmds = len(set(bot.walk_commands()))
    total_users = sum(g.member_count or 0 for g in bot.guilds)
    latency = round(bot.latency * 1000)

    # Solo 4 campos + imagen: muy por debajo del límite de 40 componentes
    embed = CV2Embed(
        title="🏠 Bienvenido al Panel de ayuda",
        description=(
            f"Hola! Me alegra que estés por aquí. Puedes revisar las categorías "
            f"de {BotName} según tu selección en el Panel."
        ),
        color=0xFFE000,
        style="clean"
    )

    embed.add_field(
        name=f"Información de {BotName}",
        value=(
            f"• {total_guilds} servidores.\n"
            f"• {total_cmds} comandos.\n"
            f"• {total_users} usuarios.\n"
            f"• {latency}ms"
        ),
        inline=False
    )

    embed.add_field(
        name="También puedes votar por mí en las siguientes BotList:",
        value=(
            f"[Top.GG]({TOPGG_URL})\n"
            f"[DCBotList]({DCBOTLIST_URL})"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ Recuerda:",
        value=(
            "Si encuentras algún bug o error en el bot, no dudes en notificarlo "
            "en el servidor de soporte para que podamos solucionarlo lo más rápido "
            f"posible. [Servidor Soporte de {BotName}]({SUPPORT_URL})"
        ),
        inline=False
    )

    embed.add_field(
        name="👥 Invitame:",
        value=f"¿Quieres a {BotName} en tu servidor? Invitame dando [click aqui]({INVITE_URL})",
        inline=False
    )

    # Banner "HELP MENU" (URL directa, no hace falta subir archivo)
    BANNER_URL = "https://i.imgur.com/GASuFOz.png"
    if hasattr(embed, "set_image"):
        embed.set_image(url=BANNER_URL)

    # ui=2 -> select menu con las secciones (como ahora, sin botones)
    view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
    await ctx.reply(view=view)

  async def send_command_help(self, command):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    zyrox = f">>> {command.help}" if command.help else '>>> Sin ayuda disponible...'
    embed = CV2Embed(
        description=f"""{zyrox}""",
        color=color)
    alias = ' & '.join(command.aliases)

    embed.add_field(name="**Comandos alternativos**",
                      value=f"```{alias}```" if command.aliases else "Sin comandos alternativos",
                      inline=False)
    embed.add_field(name="**Uso**",
                      value=f"```{self.context.prefix}{command.signature}```\n")
    embed.set_author(name=f"Comando {command.qualified_name.title()}")
    embed.set_footer(text="[ ] = opcional | < > = obligatorio • Usa el prefijo antes de los comandos.")
    await self.context.reply(view=embed, mention_author=False)

  def get_command_signature(self, command: commands.Command) -> str:
    parent = command.full_parent_name
    if len(command.aliases) > 0:
      aliases = ' | '.join(command.aliases)
      fmt = f'[{command.name} | {aliases}]'
      if parent:
        fmt = f'{parent}'
      alias = f'[{command.name} | {aliases}]'
    else:
      alias = command.name if not parent else f'{parent} {command.name}'
    return f'{alias} {command.signature}'

  def common_command_formatting(self, embed_like, command):
    embed_like.title = self.get_command_signature(command)
    if command.description:
      embed_like.description = f'{command.description}\n\n{command.help}'
    else:
      embed_like.description = command.help or 'No se encontró ayuda...'

  async def send_group_help(self, group):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [
        (
            f"`{self.context.prefix}{cmd.qualified_name}`\n",
            f"{cmd.short_doc if cmd.short_doc else ''}\n\u200b"
        )
        for cmd in group.commands
      ]

    count = len(group.commands)

    embeds = FieldPagePaginator(
      entries=entries,
      title=f"{group.qualified_name.title()} [{count}]",
      description="< > Obligatorio | [ ] Opcional\n",
      per_page=4
   )

    paginator = Paginator(ctx, embeds)
    await paginator.paginate()

  async def send_cog_help(self, cog):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [(
      f"> `{self.context.prefix}{cmd.qualified_name}`",
      f"-# Descripción: {cmd.short_doc if cmd.short_doc else ''}"
      f"\n\u200b",
    ) for cmd in cog.get_commands()]
    paginator = Paginator(source=FieldPagePaginator(
      entries=entries,
      title=f"{cog.qualified_name.title()} de {BRAND_NAME} ({len(cog.get_commands())})",
      description="`<..> Obligatorio | [..] Opcional`\n\n",
      color=0xFF0000,
      per_page=4),
                          ctx=self.context)
    await paginator.paginate()


class Help(Cog, name="help"):

  def __init__(self, client: zyrox):
    self.client = client
    self._original_help_command = client.help_command
    attributes = {
      'name': "help",
      'aliases': ['h'],
      'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
      'help': 'Muestra la ayuda del bot, de un comando o de una categoría'
    }
    client.help_command = HelpCommand(command_attrs=attributes)
    client.help_command.cog = self

  async def cog_unload(self):
    # CORREGIDO: antes se asignaba a self.help_command (no restauraba nada)
    self.client.help_command = self._original_help_command