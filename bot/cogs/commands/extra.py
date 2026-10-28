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
from utils.emoji import BOOST, CODEBASE, CROSS, KING, TICK, UPTIME, ZWARNING
from discord.ext import commands
import datetime
import sys
from discord.ui import Button, View, LayoutView, TextDisplay, Separator, Container, ActionRow, MediaGallery
from utils.cv2 import CV2, build_container
import psutil
import time
from utils.Tools import *
from discord.ext import commands, menus
from discord.ext.commands import BucketType, cooldown
import requests
from typing import *
from utils import *
from utils.config import BotName, serverLink
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from core import Cog, zyrox, Context
from typing import Optional
import aiosqlite 
import asyncio
import aiohttp


start_time = time.time()


def datetime_to_seconds(thing: datetime.datetime):
  current_time = datetime.datetime.fromtimestamp(time.time())
  return round(
    round(time.time()) +
    (current_time - thing.replace(tzinfo=None)).total_seconds())

tick = f"{TICK}>"
cross = CROSS




class RoleInfoView(View):
  def __init__(self, role: discord.Role, author_id):
    super().__init__(timeout=180)
    self.role = role
    self.author_id = author_id

  @discord.ui.button(label='Mostrar permisos',  emoji=f"{CODEBASE} ", style=discord.ButtonStyle.secondary)
  async def show_permissions(self, interaction: discord.Interaction, button: Button):
    if interaction.user.id != self.author_id:
          await interaction.response.send_message("¡Ups! Ese mensaje no es tuyo. Debes ejecutar este comando para interactuar con él.", ephemeral=True)
          return

    permissions = [perm.replace("_", " ").title() for perm, value in self.role.permissions if value]
    permission_text = ", ".join(permissions) if permissions else "Ninguno"
    await interaction.response.send_message(view=CV2(f"Permisos de {self.role.name}", permission_text or "Sin permisos."), ephemeral=True)

    
class OverwritesView(View):
  def __init__(self, channel, author_id):
      super().__init__(timeout=180)
      self.channel = channel
      self.author_id = author_id

  @discord.ui.button(label='Mostrar permisos', style=discord.ButtonStyle.primary)
  async def show_overwrites(self, interaction: discord.Interaction, button: Button):
      if interaction.user.id != self.author_id:
          await interaction.response.send_message("¡Ups! Ese mensaje no es tuyo. Debes ejecutar este comando para interactuar con él.", ephemeral=True)
          return

      overwrites = []
      for target, perms in self.channel.overwrites.items():
          permissions = {
              "Ver canal": perms.view_channel,
              "Enviar mensajes": perms.send_messages,
              "Leer historial de mensajes": perms.read_message_history,
              "Gestionar mensajes": perms.manage_messages,
              "Insertar enlaces": perms.embed_links,
              "Adjuntar archivos": perms.attach_files,
              "Gestionar canales": perms.manage_channels,
              "Gestionar permisos": perms.manage_permissions,
              "Gestionar webhooks": perms.manage_webhooks,
              "Crear invitación instantánea": perms.create_instant_invite,
              "Añadir reacciones": perms.add_reactions,
              "Mencionar a todos": perms.mention_everyone,
              "Expulsar miembros": perms.kick_members,
              "Banear miembros": perms.ban_members,
              "Moderar miembros": perms.moderate_members,
              "Enviar mensajes TTS": perms.send_tts_messages,
              "Usar emojis externos": perms.external_emojis,
              "Usar stickers externos": perms.external_stickers,
              "Ver registro de auditoría": perms.view_audit_log,
              "Silenciar miembros (voz)": perms.mute_members,
              "Ensordecer miembros (voz)": perms.deafen_members,
              "Administrador": perms.administrator
          }

          overwrites.append(f"**Para {target.name}**\n" +
                            "\n".join(f"  * **{perm}:** {'{TICK}>' if value else '{CROSS}' if value is False else '⛔'}" for perm, value in permissions.items()))

      ow_text = "\n".join(overwrites) if overwrites else "No hay permisos configurados para este canal."
      footer = f"{TICK}> = Permitido, {CROSS} = Denegado, ⛔ = Ninguno"
      await interaction.response.send_message(view=CV2(f"Permisos de {self.channel.name}", ow_text, footer), ephemeral=True)




class Extra(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.color = 0xFF0000
    self.start_time = datetime.datetime.now()

  @commands.hybrid_group(name="banner")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def banner(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send_help(ctx.command)

  @banner.command(name="server")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  async def server(self, ctx):
    if not ctx.guild.banner:
      await ctx.reply(view=CV2(f"{cross} Error", "Este servidor no tiene banner."))
    else:
      webp = ctx.guild.banner.replace(format='webp')
      jpg = ctx.guild.banner.replace(format='jpg')
      png = ctx.guild.banner.replace(format='png')
      links = f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      if ctx.guild.banner.is_animated():
          links += f" | [`GIF`]({ctx.guild.banner.replace(format='gif')})"
      view = LayoutView(timeout=None)
      gallery = MediaGallery()
      gallery.add_item(media=str(ctx.guild.banner.url))
      view.add_item(build_container(
          TextDisplay(f"**{ctx.guild.name}**"),
          Separator(visible=True),
          TextDisplay(links),
          gallery
      ))
      await ctx.reply(view=view)

  
  @banner.command(name="user")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def _user(self,
                  ctx,
                  member: Optional[Union[discord.Member,
                                         discord.User]] = None):
    if member == None or member == "":
      member = ctx.author
    bannerUser = await self.bot.fetch_user(member.id)
    if not bannerUser.banner:
      await ctx.reply(view=CV2(f"{cross} Error", f"{member} no tiene banner."))
    else:
      webp = bannerUser.banner.replace(format='webp')
      jpg = bannerUser.banner.replace(format='jpg')
      png = bannerUser.banner.replace(format='png')
      links = f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      if bannerUser.banner.is_animated():
          links += f" | [`GIF`]({bannerUser.banner.replace(format='gif')})"
      view = LayoutView(timeout=None)
      gallery = MediaGallery()
      gallery.add_item(media=str(bannerUser.banner.url))
      view.add_item(build_container(
          TextDisplay(f"**{member}**"),
          Separator(visible=True),
          TextDisplay(links),
          gallery
      ))
      await ctx.send(view=view)


  
  

  @commands.command(name="uptime", description="Muestra el tiempo de actividad del bot.")
  @blacklist_check() 
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def uptime(self, ctx):
      pfp = ctx.author.display_avatar.url

      uptime_seconds = int(round(time.time() - start_time))
      uptime_timedelta = datetime.timedelta(seconds=uptime_seconds)

      uptime_string = f"Activo desde {datetime.datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')} UTC"
      uptime_duration_string = f"{uptime_timedelta.days} días, {uptime_timedelta.seconds // 3600} horas, {(uptime_timedelta.seconds // 60) % 60} minutos, {uptime_timedelta.seconds % 60} segundos"

      uptime_text = (
          f"**__UTC__**\n{ZWARNING} {uptime_string}\n\n"
          f"**__Duración en línea__**\n{UPTIME} {uptime_duration_string}"
      )
      await ctx.send(view=CV2(f"Tiempo activo de {BRAND_NAME}", uptime_text))

    

  @commands.hybrid_command(name="serverinfo",
                           aliases=["sinfo", "si"],
                           with_app_command=True)
  @blacklist_check() 
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def serverinfo(self, ctx):
        c_at = ctx.guild.created_at.strftime("%Y-%m-%d %H:%M:%S")
        about = (
            f"**Nombre:** {ctx.guild.name}\n"
            f"**ID:** {ctx.guild.id}\n"
            f"**Dueño {KING}:** {ctx.guild.owner} (<@{ctx.guild.owner_id}>)\n"
            f"**Creado el:** {c_at}\n"
            f"**Miembros:** {len(ctx.guild.members)}"
        )
        desc_section = f"\n\n**__Descripción__**\n{ctx.guild.description}" if ctx.guild.description else ""
        stats = (
            f"**Nivel de verificación:** {ctx.guild.verification_level}\n"
            f"**Canales:** {len(ctx.guild.channels)}\n"
            f"**Roles:** {len(ctx.guild.roles)}\n"
            f"**Emojis:** {len(ctx.guild.emojis)}\n"
            f"**Estado de boosts:** Nivel {ctx.guild.premium_tier} (Boosts: {ctx.guild.premium_subscription_count})"
        )
        features_text = ""
        if ctx.guild.features:
            features = "\n".join([f"{TICK}>: {f[:1].upper() + f[1:].lower().replace('_', ' ')}" for f in ctx.guild.features])
            features_text = f"\n\n**__Características__**\n{features[:1000] if len(features) > 1024 else features}"
        regular_emojis = [e for e in ctx.guild.emojis if not e.animated]
        animated_emojis = [e for e in ctx.guild.emojis if e.animated]
        emoji_info = f"Normales: {len(regular_emojis)}/100 | Animados: {len(animated_emojis)}/100 | Total: {len(ctx.guild.emojis)}/200"
        roles = ctx.guild.roles
        roles_display = "\n".join([r.mention for r in roles[:10]])
        if len(roles) > 10:
            roles_display += f"\n...y {len(roles) - 10} más"
        full_text = (
            f"**__Acerca de__**\n{about}{desc_section}\n\n"
            f"**__Estadísticas generales__**\n{stats}{features_text}\n\n"
            f"**__Canales__**\n**Total:** {len(ctx.guild.channels)} — {len(ctx.guild.text_channels)} de texto, {len(ctx.guild.voice_channels)} de voz\n\n"
            f"**__Información de emojis__**\n{emoji_info}\n\n"
            f"**__Estado de boosts__**\nNivel: {ctx.guild.premium_tier} [{BOOST}{ctx.guild.premium_subscription_count} boosts]\n\n"
            f"**__Roles del servidor__ [{len(roles)}]**\n{roles_display}"
        )
        icon_url = ctx.guild.icon.url if ctx.guild.icon else None
        view = LayoutView(timeout=None)
        items = [TextDisplay(f"# Información de {ctx.guild.name}"), Separator(visible=True), TextDisplay(full_text)]
        if icon_url or ctx.guild.banner:
            gallery = MediaGallery()
            if icon_url:
                gallery.add_item(media=str(icon_url))
            if ctx.guild.banner:
                gallery.add_item(media=str(ctx.guild.banner.url))
            items.append(gallery)
        view.add_item(build_container(*items))
        await ctx.send(view=view)
        

  
  @commands.hybrid_command(name="userinfo",
                           aliases=["whois", "ui"],
                           usage="Userinfo [user]",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def _userinfo(self,
                      ctx,
                      member: Optional[Union[discord.Member,
                                             discord.User]] = None):
    if member == None or member == "":
      member = ctx.author
    elif member not in ctx.guild.members:
      member = await self.bot.fetch_user(member.id)

    badges = ""
    if member.public_flags.hypesquad:
      badges += "Eventos HypeSquad, "
    if member.public_flags.hypesquad_balance:
      badges += "HypeSquad Balance, "
    if member.public_flags.hypesquad_bravery:
      badges += "HypeSquad Bravery, "
    if member.public_flags.hypesquad_brilliance:
      badges += "HypeSquad Brilliance, "
    if member.public_flags.early_supporter:
      badges += "Early Supporter, "
    if member.public_flags.active_developer:
      badges += "Desarrollador activo, "
    if member.public_flags.verified_bot_developer:
      badges += "Desarrollador de bots verificado, "
    if member.public_flags.discord_certified_moderator:
      badges += "Alumni del programa de moderadores, "
    if member.public_flags.staff:
      badges += "Staff de Discord, "
    if member.public_flags.partner:
      badges += "Dueño de servidor asociado "
    if badges == None or badges == "":
      badges += f"{cross}"

    if member in ctx.guild.members:
      nickk = f"{member.nick if member.nick else 'Ninguno'}"
      joinedat = f"<t:{round(member.joined_at.timestamp())}:R>"
    else:
      nickk = "Ninguno"
      joinedat = "Ninguno"

    kp = ""
    if member in ctx.guild.members:
      if member.guild_permissions.kick_members:
        kp += "Expulsar miembros"
      if member.guild_permissions.ban_members:
        kp += " , Banear miembros"
      if member.guild_permissions.administrator:
        kp += " , Administrador"
      if member.guild_permissions.manage_channels:
        kp += " , Gestionar canales"
        
      if  member.guild_permissions.manage_guild:
        kp += " , Gestionar servidor"
        
      if member.guild_permissions.manage_messages:
        kp += " , Gestionar mensajes"
      if member.guild_permissions.mention_everyone:
        kp += " , Mencionar a todos"
      if member.guild_permissions.manage_nicknames:
        kp += " , Gestionar apodos"
      if member.guild_permissions.manage_roles:
        kp += " , Gestionar roles"
      if member.guild_permissions.manage_webhooks:
        kp += " , Gestionar webhooks"
      if member.guild_permissions.manage_emojis:
        kp += " , Gestionar emojis"

      if kp is None or kp == "":
        kp = "Ninguno"

    if member in ctx.guild.members:
      if member == ctx.guild.owner:
        aklm = "Dueño del servidor"
      elif member.guild_permissions.administrator:
        aklm = "Administrador del servidor"
      elif member.guild_permissions.ban_members or member.guild_permissions.kick_members:
        aklm = "Moderador del servidor"
      else:
        aklm = "Miembro del servidor"

    bannerUser = await self.bot.fetch_user(member.id)
    embed = discord.Embed(color=self.color)
    embed.timestamp = discord.utils.utcnow()
    if not bannerUser.banner:
      pass
    else:
      embed.set_image(url=bannerUser.banner)
    embed.set_author(name=f"Información de {member.name}",
                     icon_url=member.avatar.url
                     if member.avatar else member.default_avatar.url)
    embed.set_thumbnail(
      url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="__Información general__",
                    value=f"""
**Nombre:** {member}
**ID:** {member.id}
**Apodo:** {nickk}
**¿Bot?:** {'{TICK}> Sí' if member.bot else '{CROSS} No'}
**Insignias:** {badges}
**Cuenta creada:** <t:{round(member.created_at.timestamp())}:R>
**Se unió al servidor:** {joinedat}
            """,
                    inline=False)
    if member in ctx.guild.members:
      r = (', '.join(role.mention for role in member.roles[1:][::-1])
           if len(member.roles) > 1 else 'Ninguno.')
      embed.add_field(name="__Información de roles__",
                      value=f"""
**Rol más alto:** {member.top_role.mention if len(member.roles) > 1 else 'Ninguno'}
**Roles [{f'{len(member.roles) - 1}' if member.roles else '0'}]:** {r if len(r) <= 1024 else r[0:1006] + ' y más...'}
**Color:** {member.color if member.color else '99aab5'}
                """,
                      inline=False)
    if member in ctx.guild.members:
      embed.add_field(
        name="__Extra__",
        value=
        f"**Impulsando:** {f'<t:{round(member.premium_since.timestamp())}:R>' if member in ctx.guild.premium_subscribers else 'Ninguno'}\n**Voz:** {'Ninguno' if not member.voice else member.voice.channel.mention}",
        inline=False)
    if member in ctx.guild.members:
      embed.add_field(name="__Permisos clave__",
                      value=", ".join([kp]),
                      inline=False)
    if member in ctx.guild.members:
      embed.add_field(name="__Reconocimiento__",
                      value=f"{aklm}",
                      inline=False)
    if member in ctx.guild.members:
      embed.set_footer(text=f"Solicitado por {ctx.author}",
                       icon_url=ctx.author.avatar.url
                       if ctx.author.avatar else ctx.author.default_avatar.url)
    else:
      if member not in ctx.guild.members:
        embed.set_footer(text=f"{member.name} no está en este servidor.",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar
                         else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)



  @commands.hybrid_command(name='roleinfo', aliases=["ri"], help="Muestra información sobre un rol especificado.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def roleinfo(self, ctx, role: discord.Role):
    members = role.members
    created_at = role.created_at.strftime("%Y-%m-%d %H:%M:%S")
    total_roles = len(ctx.guild.roles)
    role_position = total_roles - role.position
    role_text = (
        f"**__Información general__**\n"
        f"**ID:** {role.id}\n**Nombre:** {role.name}\n**Mención:** <@&{role.id}>\n"
        f"**Color:** {str(role.color)}\n**Miembros totales:** {len(role.members)}\n\n"
        f"**Posición:** {role_position}\n**Mencionable:** {role.mentionable}\n"
        f"**Mostrado aparte:** {role.hoist}\n**Gestionado:** {role.managed}\n**Creado el:** {created_at}"
    )
    view = RoleInfoView(role, ctx.author.id)
    await ctx.send(content=role_text, view=view)





  @commands.command(name="boostcount",
                    help="Muestra el número de boosts",
                    usage="boosts",
                    aliases=["bco"],
                    with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def boosts(self, ctx):
    await ctx.send(view=CV2(f"{BOOST} Número de boosts de {ctx.guild.name}", f"**Total: `{ctx.guild.premium_subscription_count}` boosts**"))

  @commands.hybrid_group(name="list",
                         invoke_without_command=True,
                         with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def __list_(self, ctx: commands.Context):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

  @__list_.command(name="boosters",
                   aliases=["boost", "booster"],
                   usage="List boosters",
                   help="Lista de boosters del servidor",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_boost(self, ctx):
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{round(mem.premium_since.timestamp())}:R>"
      for no, mem in enumerate(guild.premium_subscribers, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=
      f"Lista de boosters en {guild.name} - {len(guild.premium_subscribers)}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="bans", help= "Lista de todos los miembros baneados del servidor", aliases=["ban"], with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(view_audit_log=True)
  @commands.bot_has_permissions(view_audit_log=True)
  async def list_ban(self, ctx):
    bans = [member async for member in ctx.guild.bans()]
    if len(bans) == 0:
      return await ctx.reply("No hay usuarios baneados en este servidor.", mention_author=False)
    else:
      mems = ([
      member async for member in ctx.guild.bans()
    ])
      guild = ctx.guild
      entries = [
      f"`#{no}.` {mem}"
      for no, mem in enumerate(mems, start=1)
    ]
      paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Usuarios baneados en {guild.name} - {len(bans)}",
      description="",
      per_page=10),
                          ctx=ctx)
      await paginator.paginate()

  @__list_.command(
    name="inrole",
    aliases=["inside-role"],
    help="Lista de miembros que tienen el rol especificado",
    with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_inrole(self, ctx, role: discord.Role):
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(role.members, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Lista de miembros en {role} - {len(role.members)}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="emojis",
                   aliases=["emoji"],
                   help="Lista de emojis del servidor con sus IDs",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_emojis(self, ctx):
    guild = ctx.guild
    entries = [
      f"`#{no}.` {e} - `{e}`"
      for no, e in enumerate(ctx.guild.emojis, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Lista de emojis en {guild.name} - {len(ctx.guild.emojis)}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="roles",
                   aliases=["role"],
                   help="Lista de todos los roles del servidor con sus IDs",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_roles=True)
  async def list_roles(self, ctx):
    guild = ctx.guild
    entries = [
      f"`#{no}.` {e.mention} - `[{e.id}]`"
      for no, e in enumerate(ctx.guild.roles, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Lista de roles en {guild.name} - {len(ctx.guild.roles)}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="bots",
                   aliases=["bot"],
                   help="Lista de todos los bots del servidor",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_bots(self, ctx):
    guild = ctx.guild
    people = filter(lambda member: member.bot, ctx.guild.members)
    people = sorted(people, key=lambda member: member.joined_at)
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}]"
      for no, mem in enumerate(people, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Bots en {guild.name} - {len(people)}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="admins",
                   aliases=["admin"],
                   help="Lista de todos los administradores del servidor",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_admin(self, ctx):
    mems = ([
      mem for mem in ctx.guild.members
      if mem.guild_permissions.administrator
    ])
    mems = sorted(mems, key=lambda mem: not mem.bot)
    admins = len([
      mem for mem in ctx.guild.members
      if mem.guild_permissions.administrator
    ])
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Administradores en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="invoice", help="Lista de todos los usuarios de un canal de voz", aliases=["invc"], with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def listusers(self, ctx):
    if not ctx.author.voice:
      return await ctx.send("No estás conectado a un canal de voz")
    members = ctx.author.voice.channel.members
    entries = [
      f"`[{n}]` | {member} [{member.mention}]"
      for n, member in enumerate(members, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      title=f"Lista de voz de {ctx.author.voice.channel.name} - {len(members)}",
      color=self.color),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="moderators", help= "Lista de todos los moderadores del servidor", aliases=["mods"], with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_mod(self, ctx):
    membs = ([
      mem for mem in ctx.guild.members
      if mem.guild_permissions.ban_members
      or mem.guild_permissions.kick_members
    ])
    mems = filter(lambda member: member.bot, ctx.guild.members)
    mems = sorted(membs, key=lambda mem: mem.joined_at)
    admins = len([
      mem for mem in ctx.guild.members
      if mem.guild_permissions.ban_members
      or mem.guild_permissions.kick_members
    ])
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Moderadores en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="early", aliases=["sup"], help= "Lista de miembros que tienen la insignia Early Supporter.", with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_early(self, ctx):
    mems = ([
      memb for memb in ctx.guild.members
      if memb.public_flags.early_supporter
    ])
    mems = sorted(mems, key=lambda memb: memb.created_at)
    admins = len([
      memb for memb in ctx.guild.members
      if memb.public_flags.early_supporter
    ])
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id})  [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"IDs de Early Supporters en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="activedeveloper", help= "Lista de miembros que tienen la insignia de Desarrollador activo.",
                   aliases=["activedev"],
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_activedeveloper(self, ctx):
    mems = ([
      memb for memb in ctx.guild.members
      if memb.public_flags.active_developer
    ])
    mems = sorted(mems, key=lambda memb: memb.created_at)
    admins = len([
      memb for memb in ctx.guild.members
      if memb.public_flags.active_developer
    ])
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) [{mem.mention}] - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"IDs de desarrolladores activos en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="createdat", help= "Lista de fechas de creación de cuenta de todos los usuarios", with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_cpos(self, ctx):
    mems = ([memb for memb in ctx.guild.members])
    mems = sorted(mems, key=lambda memb: memb.created_at)
    admins = len([memb for memb in ctx.guild.members])
    guild = ctx.guild
    entries = [
      f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) - <t:{int(mem.created_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Creación de cada ID en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="joinedat", help= "Lista de fechas de ingreso al servidor de todos los usuarios", with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def list_joinpos(self, ctx):
    mems = ([memb for memb in ctx.guild.members])
    mems = sorted(mems, key=lambda memb: memb.joined_at)
    admins = len([memb for memb in ctx.guild.members])
    guild = ctx.guild
    entries = [
      f"`#{no}.` [{mem}](https://discord.com/users/{mem.id}) Se unió el - <t:{int(mem.joined_at.timestamp())}:D>"
      for no, mem in enumerate(mems, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Posición de ingreso de cada usuario en {guild.name} - {admins}",
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()




  @commands.command(name="joined-at",
                    help="Muestra cuándo se unió un usuario",
                    usage="joined-at [user]",
                    with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def joined_at(self, ctx):
    joined = ctx.author.joined_at.strftime("%a, %d %b %Y %I:%M %p")
    await ctx.send(view=CV2("Fecha de ingreso", f"**`{joined}`**"))

  @commands.command(name="github", usage="github [search]")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def github(self, ctx, *, search_query):
    json = requests.get(
      f"https://api.github.com/search/repositories?q={search_query}").json()

    if json["total_count"] == 0:
      await ctx.send(f"No se encontraron repositorios con el nombre: {search_query}")
    else:
      await ctx.send(
        f"Resultado encontrado para '{search_query}':\n{json['items'][0]['html_url']}")

  @commands.hybrid_command(name="vcinfo",
                           description="Muestra información sobre un canal de voz.",
                           help="Muestra información sobre un canal de voz.", 
                           usage="<VoiceChannel>",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def vcinfo(self, ctx, channel: discord.VoiceChannel = None):
    if channel is None:
      await ctx.reply(view=CV2(f"{cross} Error", "Proporciona un canal de voz válido."))
      return
    vc_text = (
        f"**ID:** {channel.id}\n**Miembros:** {len(channel.members)}\n"
        f"**Bitrate:** {channel.bitrate/1000} kbps\n"
        f"**Creado el:** {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"**Categoría:** {channel.category.name if channel.category else 'Ninguna'}\n"
        f"**Región:** {channel.rtc_region}"
    )
    if channel.user_limit:
        vc_text += f"\n**Límite de usuarios:** {channel.user_limit}"
    view = LayoutView(timeout=None)
    join_btn = Button(label="Unirse", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{ctx.guild.id}/{channel.id}")
    view.add_item(build_container(
        TextDisplay(f"**Información del canal de voz — {channel.name}**"),
        Separator(visible=True),
        TextDisplay(vc_text),
        ActionRow(join_btn)
    ))
    await ctx.send(view=view)


  @commands.hybrid_command(name="channelinfo",
     aliases=['cinfo', 'ci'],
     description='Obtén información sobre un canal.',
     help='Obtén información sobre un canal.',
     usage="<Channel>",
     with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def channelinfo(self, ctx, channel: discord.TextChannel = None):
    if channel is None:
      channel = ctx.channel
      
    ch_text = (
        f"**ID:** {channel.id}\n**Creado el:** {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"**Categoría:** {channel.category.name if channel.category else 'Ninguna'}\n"
        f"**Tema:** {channel.topic if channel.topic else 'Ninguno'}\n"
        f"**Modo lento:** {f'{channel.slowmode_delay} segundos' if channel.slowmode_delay else 'Desactivado'}\n"
        f"**NSFW:** {channel.is_nsfw()}"
    )
    view = OverwritesView(channel, ctx.author.id)
    view.add_item(Button(label="Ir al canal", style=discord.ButtonStyle.green, url=f"https://discord.com/channels/{ctx.guild.id}/{channel.id}"))
    await ctx.send(content=ch_text, view=view)


  @commands.hybrid_command(name="ping", aliases=['latency'], help="Comprueba la latencia del bot.")
  @ignore_check()
  @blacklist_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def ping(self, ctx: commands.Context):
    """Muestra las latencias del WebSocket, la API y la base de datos del bot."""
    
    # 1. Start timer and send an initial "Pinging..." message
    start_time = time.monotonic()
    msg = await ctx.send(view=CV2("Comprobando latencia...", "Calculando los tiempos de respuesta, espera por favor."))
    end_time = time.monotonic()

    bot_latency = round(self.bot.latency * 1000)
    api_latency = round((end_time - start_time) * 1000)
    
    db_latency = "No disponible"
    try:
        async with aiosqlite.connect("db/afk.db") as db:
            db_start_time = time.perf_counter()
            await db.execute("SELECT 1")
            db_end_time = time.perf_counter()
            db_latency = f"{round((db_end_time - db_start_time) * 1000)}ms"
    except Exception as e:
        print(f"Database latency check failed: {e}")

    latency_text = (
        f"**Bot (WebSocket):** `{bot_latency}ms`\n"
        f"**API (Ida y vuelta):** `{api_latency}ms`\n"
        f"**Base de datos:** `{db_latency}`"
    )
    await msg.edit(view=CV2("Informe de latencia del sistema", latency_text))




  
  @commands.command(name="permissions", aliases= ["perms"],
                           help="Comprueba y muestra los permisos clave de un usuario específico",
                           usage="perms <user>",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def keyperms(self, ctx, member: discord.Member):
    key_permissions = []

    if member.guild_permissions.create_instant_invite:
      key_permissions.append("Crear invitación instantánea")
    if member.guild_permissions.kick_members:
      key_permissions.append("Expulsar miembros")
    if member.guild_permissions.ban_members:
      key_permissions.append("Banear miembros")
    if member.guild_permissions.administrator:
      key_permissions.append("Administrador")
    if member.guild_permissions.manage_channels:
      key_permissions.append("Gestionar canales")
    if member.guild_permissions.manage_messages:
      key_permissions.append("Gestionar mensajes")
    if member.guild_permissions.mention_everyone:
      key_permissions.append("Mencionar a todos")
    if member.guild_permissions.manage_nicknames:
      key_permissions.append("Gestionar apodos")
    if member.guild_permissions.manage_roles:
      key_permissions.append("Gestionar roles")
    if member.guild_permissions.manage_webhooks:
      key_permissions.append("Gestionar webhooks")
    if member.guild_permissions.manage_emojis:
      key_permissions.append("Gestionar emojis")
    if member.guild_permissions.manage_guild:
      key_permissions.append("Gestionar servidor")
    if member.guild_permissions.manage_permissions:
      key_permissions.append("Gestionar permisos")
    if member.guild_permissions.manage_threads:
      key_permissions.append("Gestionar hilos")
    if member.guild_permissions.moderate_members:
      key_permissions.append("Moderar miembros")
    if member.guild_permissions.move_members:
      key_permissions.append("Mover miembros")
    if member.guild_permissions.mute_members:
      key_permissions.append("Silenciar miembros (voz)")
    if member.guild_permissions.deafen_members:
      key_permissions.append("Ensordecer miembros")
    if member.guild_permissions.priority_speaker:
      key_permissions.append("Orador prioritario")
    if member.guild_permissions.stream:
      key_permissions.append("Transmitir")
    
    
    

    permissions_list = ", ".join(key_permissions) if key_permissions else "Ninguno"

    await ctx.reply(view=CV2(f"Permisos clave de {member}", f"__**Permisos clave**__\n{permissions_list}"))

  




  @commands.hybrid_command(name="report",
                           aliases=["bug"],
                           usage='Report <bug>',
                           description='Reporta un bug al equipo de desarrollo.',
                           help='Reporta un bug al equipo de desarrollo.',
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 30, commands.BucketType.channel)
  async def report(self, ctx, *, bug):
    channel = self.bot.get_channel(1396813063642153030)
    report_text = f"{bug}\n\n**Reportado por:** {ctx.author.name}\n**Servidor:** {ctx.guild.name}\n**Canal:** {ctx.channel.name}"
    await channel.send(view=CV2("Bug reportado", report_text))
    await ctx.reply(view=CV2(f"{TICK} Bug reportado", "Gracias por reportar el bug. Lo revisaremos."))

