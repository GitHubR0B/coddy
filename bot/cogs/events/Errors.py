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
import json
import aiosqlite
from discord.ext import commands
from utils.config import serverLink
from core import zyrox, Cog, Context
from utils.Tools import get_ignore_data

class Errors(Cog):
  def __init__(self, client: zyrox):
    self.client = client

  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    if ctx.command is None:
      return
    

    if isinstance(error, commands.CommandNotFound):
      return

    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.CheckFailure):
      data = await get_ignore_data(ctx.guild.id)
      ch = data["channel"]
      iuser = data["user"]
      cmd = data["command"]
      buser = data["bypassuser"]

      if str(ctx.author.id) in buser:
        return

      if str(ctx.channel.id) in ch:
        await ctx.reply(f"{ctx.author.mention} **Este canal está en la lista de ignorados. Usa mis comandos en otro canal.**",
                        delete_after=8)
        return

      if str(ctx.author.id) in iuser:
        await ctx.reply(f"{ctx.author.mention} **Estás configurado como usuario ignorado en este servidor. Prueba mis comandos en otro servidor.**", delete_after=8)
        return

      if ctx.command.name in cmd or any(alias in cmd for alias in ctx.command.aliases):
        await ctx.reply(f"{ctx.author.mention} **Este comando está ignorado en este servidor. Usa otros comandos o prueba este en otro servidor.**", delete_after=8)
        return

    if isinstance(error, commands.NoPrivateMessage):
      embed = discord.Embed(color=0xFF0000, description="No puedes usar mis comandos en mensajes privados.")
      embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=20)
      return

    if isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.CommandOnCooldown):
      embed = discord.Embed(color=0xFF0000, description=f"**{ctx.author.mention} Espera un momento. Podrás usar comandos en {error.retry_after:.2f} segundos.**")
      embed.set_author(name="Tiempo de espera", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=10)
      return

    if isinstance(error, commands.MaxConcurrencyReached):
      embed = discord.Embed(color=0xFF0000, description=f"{ctx.author.mention} Este comando ya está en ejecución. Deja que termine e inténtalo de nuevo.")
      embed.set_author(name="Comando en progreso.", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=10)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.MissingPermissions):
      permisos_es = {
        "administrator": "Administrador", "manage_guild": "Gestionar servidor",
        "manage_roles": "Gestionar roles", "manage_channels": "Gestionar canales",
        "manage_messages": "Gestionar mensajes", "manage_webhooks": "Gestionar webhooks",
        "manage_nicknames": "Gestionar apodos", "manage_emojis": "Gestionar emojis",
        "kick_members": "Expulsar miembros", "ban_members": "Banear miembros",
        "moderate_members": "Moderar miembros", "view_audit_log": "Ver registro de auditoría",
        "read_message_history": "Leer historial de mensajes", "send_messages": "Enviar mensajes",
        "embed_links": "Insertar enlaces", "attach_files": "Adjuntar archivos",
        "add_reactions": "Añadir reacciones", "external_emojis": "Usar emojis externos",
        "mention_everyone": "Mencionar a todos", "connect": "Conectar a voz",
        "speak": "Hablar", "move_members": "Mover miembros", "mute_members": "Silenciar miembros",
        "deafen_members": "Ensordecer miembros", "priority_speaker": "Prioridad de voz",
        "create_instant_invite": "Crear invitaciones", "change_nickname": "Cambiar apodo",
        "create_private_threads": "Crear hilos privados", "create_public_threads": "Crear hilos públicos",
        "send_messages_in_threads": "Enviar mensajes en hilos", "manage_threads": "Gestionar hilos",
      }
      missing = [permisos_es.get(perm, perm.replace("_", " ").title()) for perm in error.missing_permissions]
      fmt = "{}, y {}".format(", ".join(missing[:-1]), missing[-1]) if len(missing) > 2 else " y ".join(missing)
      embed = discord.Embed(color=0xFF0000, description=f"**¡Ups! No tienes el permiso {fmt} para ejecutar el comando {ctx.command.name}.**")
      embed.set_author(name="Permisos faltantes", icon_url=self.client.user.avatar.url)
      
      embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed, delete_after=7)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.BadArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return

    if isinstance(error, commands.BotMissingPermissions):
      missing = ", ".join(error.missing_permissions)
      await ctx.reply(f'**¡Ey! Necesito el permiso {missing} para ejecutar el comando {ctx.command.qualified_name}. Concédeme el permiso {missing}.**', delete_after=7)
      return

    if isinstance(error, discord.HTTPException):
      print(f"[ERROR] HTTPException in {ctx.command}: {error}")
      return

    if isinstance(error, commands.CommandInvokeError):
      print(f"[ERROR] CommandInvokeError in {ctx.command}: {error}")
      print(f"  Original: {error.original}")
      return

  @commands.Cog.listener()
  async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Maneja los errores de los comandos slash (híbridos incluidos).

    Sin este listener, cualquier fallo en un slash se queda en un genérico
    "La aplicación no respondió" y no queda rastro en consola.
    """
    import traceback

    original = getattr(error, "original", error)
    command = getattr(interaction, "command", None)
    data = interaction.data if isinstance(interaction.data, dict) else {}
    name = getattr(command, "qualified_name", None) or data.get("name", "desconocido")
    print(f"[ERROR] AppCommandError en /{name}: {original}")
    traceback.print_exception(type(original), original, original.__traceback__)

    if isinstance(original, discord.app_commands.CommandSignatureMismatch):
      group = getattr(original, "command", None)
      subcommands = [child.name for child in getattr(group, "commands", [])]
      if subcommands:
        lista = ", ".join(f"`/{group.qualified_name} {sub}`" for sub in subcommands[:8])
        message = f"➡️ Ese comando necesita un subcomando. Prueba: {lista}"
      else:
        message = "➡️ Ese comando necesita un subcomando."
    elif isinstance(original, discord.app_commands.CommandNotFound):
      message = "🔄 Ese comando ya cambió de nombre. Actualiza Discord con Ctrl+R y vuelve a intentarlo."
    elif isinstance(original, discord.app_commands.CommandOnCooldown):
      message = f"⏳ Espera un momento. Podrás usar el comando en {original.retry_after:.2f} segundos."
    elif isinstance(original, discord.app_commands.MissingPermissions):
      message = "🔒 No tienes los permisos necesarios para ejecutar este comando."
    elif isinstance(original, discord.app_commands.BotMissingPermissions):
      message = "🤖 Necesito más permisos para ejecutar este comando. Revisa mi jerarquía de roles."
    elif isinstance(original, discord.app_commands.CheckFailure):
      message = "🚫 No puedes usar este comando aquí."
    else:
      message = "❌ Ocurrió un error al ejecutar el comando. Revisa la consola para más detalles."

    try:
      if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
      else:
        await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
      pass

