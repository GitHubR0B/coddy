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
from utils.emoji import CROSS, DENIED, TICK, ZWARNING
import asyncio
import datetime
import re
import typing
import typing as t
from typing import *
from utils.Tools import *
from core import Cog, zyrox, Context
from discord.ext.commands import Converter
from discord.ext import commands, tasks
from discord.ui import Button, View
from typing import Union, Optional
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from typing import Union, Optional
from io import BytesIO
import requests
import aiohttp
import time
from datetime import datetime, timezone, timedelta
import sqlite3
from typing import *
from discord.utils import utcnow



time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
  args = argument.lower()
  matches = re.findall(time_regex, args)
  time = 0
  for key, value in matches:
    try:
      time += time_dict[value] * float(key)
    except KeyError:
      raise commands.BadArgument(
        f"{value} no es una unidad de tiempo válida. Los argumentos válidos son h|m|s|d")
    except ValueError:
      raise commands.BadArgument(f"¡{key} no es un número!")
  return round(time)

async def do_removal(ctx, limit, predicate, *, before=None, after=None):
    if limit > 2000:
        return await ctx.error(f"Se indicaron demasiados mensajes para buscar ({limit}/2000)")

    if before is None:
        before = ctx.message
    else:
        before = discord.Object(id=before)

    if after is not None:
        after = discord.Object(id=after)

    try:
        deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
    except discord.Forbidden as e:
        return await ctx.error("No tengo permisos para eliminar mensajes.")
    except discord.HTTPException as e:
        return await ctx.error(f"Error: {e} (¿pruebas con una búsqueda más pequeña?)")

    spammers = Counter(m.author.display_name for m in deleted)
    deleted = len(deleted)
    messages = [f'{TICK}> | {deleted} mensaje{" fue eliminado" if deleted == 1 else "s fueron eliminados"}.']
    if deleted:
        messages.append("")
        spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
        messages.extend(f"**{name}**: {count}" for name, count in spammers)

    to_send = "\n".join(messages)

    if len(to_send) > 2000:
        await ctx.send(f"{TICK}> | Se eliminaron {deleted} mensajes correctamente.", delete_after=7)
    else:
        await ctx.send(to_send, delete_after=7)




class Moderation(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.color = 0xFF0000
    self.sniped = {}

  def convert(self, time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    unit = time[-1]
    if unit not in pos:
      return -1
    try:
      val = int(time[:-1])
    except:
      return -2
    return val * time_dict[unit]



  @commands.command()
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def enlarge(self, ctx,  emoji: Union[discord.Emoji, discord.PartialEmoji, str]):
    url = emoji.url
    await ctx.send(url)




  @commands.hybrid_command(name="unlockall",
                    help="Desbloquea todos los canales del servidor.",
                    usage="unlockall")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  @commands.cooldown(1, 15, commands.BucketType.channel)
  async def unlockall(self, ctx):
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
          button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
          button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=ZWARNING)
          async def button_callback(interaction: discord.Interaction):
              a = 0
              if interaction.user == ctx.author:
                  if interaction.guild.me.guild_permissions.manage_roles:
                      embed1 = discord.Embed(
                     color=self.color,
                    description=f"Desbloqueando todos los canales de {ctx.guild.name}...")
                      await interaction.response.edit_message(
                       embed=embed1, view=None)
                      for channel in interaction.guild.channels:
                          try:
                              await channel.set_permissions(
                                   ctx.guild.default_role,
                                overwrite=discord.PermissionOverwrite(send_messages=True,
                                                 read_messages=True),
                                         reason="Comando Unlockall ejecutado por: {}".format(ctx.author))
                              a += 1  
                          except Exception as e:
                              print(e)
                      await interaction.channel.send(
                              content=f"{TICK}> | Se desbloquearon {a} canales correctamente")   
                      return
                  else:
                    await interaction.response.edit_message(
                         content=
                           f"{ZWARNING} | Parece que me faltan los permisos necesarios. Concédeme el permiso `gestionar roles` e inténtalo de nuevo.",
                              embed=None,
                                  view=None)
              else:
                await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

          async def button1_callback(interaction: discord.Interaction):   
              if interaction.user == ctx.author:  
                  embed2 = discord.Embed(
                     color=self.color,
                    description=f"Cancelado, no desbloquearé ningún canal.")
                  await interaction.response.edit_message(
                      embed=embed2, view=None)   
              else:
                  await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)
          embed = discord.Embed(
                  color=self.color,
                 description=f'**¿Seguro que quieres desbloquear todos los canales de {ctx.guild.name}?**')
          view = View()
          button.callback = button_callback
          button1.callback = button1_callback
          view.add_item(button)
          view.add_item(button1)
          embed.set_footer(text="Haz clic en 'Confirmar' o 'Cancelar' para continuar. ¡Tienes 30 segundos para decidir!")
          await ctx.reply(embed=embed, view=view, mention_author=False,delete_after=30)     


      else:
          embed5 = discord.Embed(title=f"{ZWARNING} Acceso denegado",
                description="Tu rol debe estar por encima de mi rol más alto.",
                color=0xFF0000)
          embed5.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await ctx.send(embed=embed5, mention_author=False)  



  @commands.hybrid_command(name="lockall",
                    help="Bloquea todos los canales del servidor.",
                    usage="lockall")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  @commands.cooldown(1, 15, commands.BucketType.channel)
  async def lockall(self, ctx):
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
          button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
          button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=CROSS)
          async def button_callback(interaction: discord.Interaction):
              a = 0
              if interaction.user == ctx.author:
                  if interaction.guild.me.guild_permissions.manage_roles:
                      embed1 = discord.Embed(
                     color=self.color,
                    description=f"Bloqueando todos los canales de {ctx.guild.name}...")
                      await interaction.response.edit_message(
                       embed=embed1, view=None)
                      for channel in interaction.guild.channels:
                          try:
                              await channel.set_permissions(ctx.guild.default_role,
                                      overwrite=discord.PermissionOverwrite(
                                        send_messages=False,
                                        read_messages=True),
                                         reason="Comando Lockall ejecutado por: {}".format(ctx.author))
                              a += 1  
                          except Exception as e:
                              print(e)
                      await interaction.channel.send(
                              content=f"{TICK}>| Se bloquearon {a} canales correctamente")
                      return
                  else:
                    await interaction.response.edit_message(
                         content=
                           f"{ZWARNING} | Parece que me faltan los permisos necesarios. Concédeme el permiso `gestionar roles` e inténtalo de nuevo.",
                              embed=None,
                                  view=None)
              else:
                await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

          async def button1_callback(interaction: discord.Interaction):   
              if interaction.user == ctx.author:  
                  embed2 = discord.Embed(
                     color=self.color,
                    description=f"Cancelado, no bloquearé ningún canal.")
                  await interaction.response.edit_message(
                      embed=embed2, view=None)   
              else:
                  await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)
          embed = discord.Embed(
                  color=self.color,
                 description=f'**¿Seguro que quieres bloquear todos los canales de {ctx.guild.name}?**')
          view = View()
          button.callback = button_callback
          button1.callback = button1_callback
          view.add_item(button)
          view.add_item(button1)
          embed.set_footer(text=f"Haz clic en 'Confirmar' o 'Cancelar' para continuar. ¡Tienes 30 segundos para decidir!")
          await ctx.reply(embed=embed, view=view, mention_author=False,delete_after=30)     

      else:
          denied = discord.Embed(title=f"{ZWARNING} Acceso denegado",
              description="Tu rol debe estar por encima de mi rol más alto.",
              color=0xFF0000)
          denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                     icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await ctx.send(embed=denied, mention_author=False)
          

  @commands.hybrid_command(name="give",
                    help="Otorga un rol al usuario mencionado.",
                    usage="give <user> <role>",
                    aliases=["addrole"])
  @blacklist_check()
  @ignore_check()
  @top_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(manage_roles=True)
  @commands.bot_has_permissions(manage_roles= True)
  async def give(self, ctx, member: discord.Member, *, role: discord.Role):
    if not ctx.guild.me.guild_permissions.manage_roles:
        return await ctx.send(f"{DENIED} ¡No tengo permiso para gestionar roles!")

    if role >= ctx.guild.me.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedo gestionar roles de un usuario con un rol igual o superior!"
        )

        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    if ctx.author != ctx.guild.owner and ctx.author.top_role <= member.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedes gestionar roles de un usuario con un rol igual o superior al tuyo!"
        )
        error.set_author(name="Acceso denegado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    try:
        if role not in member.roles:
            await member.add_roles(role, reason=f"Rol agregado por {ctx.author} (ID: {ctx.author.id})")
            success = discord.Embed(
                color=self.color,
                description=f"Se **agregó** el rol {role.name} a {member.mention} correctamente."
            )
            success.set_author(name="Rol agregado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
            success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        else:
            await member.remove_roles(role, reason=f"Rol quitado por {ctx.author} (ID: {ctx.author.id})")
            success = discord.Embed(
                color=self.color,
                description=f"Se **quitó** el rol {role.name} de {member.mention} correctamente."
            )
            success.set_author(name="Rol quitado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
            success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=success)
    except discord.Forbidden:
        error = discord.Embed(
            color=self.color,
            description=f"{ZWARNING} ¡No tengo permiso para gestionar los roles de este usuario!"
        )
        await ctx.send(embed=error)
    except Exception as e:
        error = discord.Embed(
            color=self.color,
            description=f"{ZWARNING} Ocurrió un error inesperado: {str(e)}"
        )
        await ctx.send(embed=error)



  @commands.hybrid_command(name="hideall", help="Oculta todos los canales.",
                    usage="hideall")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  @commands.cooldown(1, 15, commands.BucketType.channel)
  async def hideall(self, ctx):
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
          button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
          button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=CROSS)
          async def button_callback(interaction: discord.Interaction):
              a = 0
              if interaction.user == ctx.author:
                  if interaction.guild.me.guild_permissions.manage_roles:
                      embed1 = discord.Embed(
                     color=self.color,
                    description=f"Ocultando todos los canales de {ctx.guild.name}...")
                      await interaction.response.edit_message(
                       embed=embed1, view=None)
                      for channel in interaction.guild.channels:
                          try:
                              await channel.set_permissions(ctx.guild.default_role, view_channel=False,
                                         reason="Comando Hideall ejecutado por: {}".format(ctx.author))
                              a += 1  
                          except Exception as e:
                              print(e)
                      await interaction.channel.send(
                              content=f"{TICK}> | Se ocultaron {a} canal(es) correctamente.")
                      return
                  else:
                    await interaction.response.edit_message(
                         content=
                           f"{ZWARNING} | Parece que me faltan los permisos necesarios. Concédeme el permiso `gestionar canales` e inténtalo de nuevo.",
                              embed=None,
                                  view=None)
              else:
                await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

          async def button1_callback(interaction: discord.Interaction):   
              if interaction.user == ctx.author:  
                  embed2 = discord.Embed(
                     color=self.color,
                    description=f"Cancelado, no ocultaré ningún canal.")
                  await interaction.response.edit_message(
                      embed=embed2, view=None)   
              else:
                  await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)
          embed = discord.Embed(
                  color=self.color,
                 description=f'**¿Seguro que quieres ocultar todos los canales de {ctx.guild.name}?**')
          view = View()
          button.callback = button_callback
          button1.callback = button1_callback
          view.add_item(button)
          view.add_item(button1)
          embed.set_footer(text=f"Haz clic en 'Confirmar' o 'Cancelar' para continuar. ¡Tienes 30 segundos para decidir!")
          await ctx.reply(embed=embed, view=view, mention_author=False,delete_after=30)

      else:
          denied = discord.Embed(title=f"{ZWARNING} Acceso denegado",
              description="Tu rol debe estar por encima de mi rol más alto.",
              color=0xFF0000)
          denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                     icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await ctx.send(embed=denied, mention_author=False)

  @commands.hybrid_command(name="unhideall", help="Muestra todos los canales del servidor.",
                    usage="unhideall")
  @blacklist_check()
  @ignore_check()
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  @commands.cooldown(1, 15, commands.BucketType.channel)
  async def unhideall(self, ctx):
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
          button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
          button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=CROSS)
          async def button_callback(interaction: discord.Interaction):
              a = 0
              if interaction.user == ctx.author:
                  if interaction.guild.me.guild_permissions.manage_roles:
                      embed1 = discord.Embed(
                     color=self.color,
                    description=f"Mostrando todos los canales de {ctx.guild.name}...")
                      await interaction.response.edit_message(
                       embed=embed1, view=None)
                      for channel in interaction.guild.channels:
                          try:
                              await channel.set_permissions(ctx.guild.default_role, view_channel=True,
                                         reason="Comando Unhideall ejecutado por: {}".format(ctx.author))
                              a += 1  
                          except Exception as e:
                              print(e)
                      await interaction.channel.send(
                              content=f"{TICK}> | Se mostraron {a} canal(es) correctamente.")
                      return
                  else:
                    await interaction.response.edit_message(
                         content=
                           f"{ZWARNING} | Parece que me faltan los permisos necesarios. Concédeme el permiso `gestionar canales` e inténtalo de nuevo.",
                              embed=None,
                                  view=None)
              else:
                await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

          async def button1_callback(interaction: discord.Interaction):   
              if interaction.user == ctx.author:  
                  embed2 = discord.Embed(
                     color=self.color,
                    description=f"Cancelado, no mostraré ningún canal.")
                  await interaction.response.edit_message(
                      embed=embed2, view=None)   
              else:
                  await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)
          embed = discord.Embed(
                  color=self.color,
                 description=f'**¿Seguro que quieres mostrar todos los canales de {ctx.guild.name}?**')
          view = View()
          button.callback = button_callback
          button1.callback = button1_callback
          view.add_item(button)
          view.add_item(button1)
          embed.set_footer(text=f"Haz clic en 'Confirmar' o 'Cancelar' para continuar. ¡Tienes 30 segundos para decidir!")
          await ctx.reply(embed=embed, view=view, mention_author=False,delete_after=30)     

      else:
          denied = discord.Embed(title=f"{ZWARNING} Acceso denegado",
              description="Tu rol debe estar por encima de mi rol más alto.",
              color=0xFF0000)
          denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                     icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await ctx.send(embed=denied, mention_author=False)



  @commands.hybrid_command(
        name="prefix",
        aliases=["setprefix", "prefixset"],
        help="Te permite cambiar el prefijo del bot en este servidor"
    )
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(administrator=True)
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def _prefix(self, ctx: commands.Context, prefix: str):
      if not prefix:
          await ctx.reply(embed=discord.Embed(title=f"{CROSS} Error",
                description="El prefijo no puede estar vacío. Proporciona un prefijo válido.",
                color=self.color
            ))
          return
          
      data = await getConfig(ctx.guild.id)
      if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
          data["prefix"] = str(prefix)
          await updateConfig(ctx.guild.id, data)
          embed1=discord.Embed(title=f"{TICK}> Éxito",
                description=f"Se cambió el prefijo de este servidor a `{prefix}`\n\nEl nuevo prefijo de **{ctx.guild.name}** es: `{prefix}`\nUsa `{prefix}help` para más información.",
                color=self.color
                             )
          await ctx.reply(embed=embed1)
      else:
          denied = discord.Embed(title=f"{ZWARNING} Acceso denegado",
              description="Tu rol debe estar por encima de mi rol más alto.",
              color=0xFF0000)
          denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                     icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await ctx.send(embed=denied, mention_author=False)
        


  @commands.hybrid_command(name="clone", help="Clona un canal.")
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(manage_channels=True)
  async def clone(self, ctx: commands.Context, channel: discord.TextChannel):
    
    if not ctx.guild.me.guild_permissions.manage_channels:
        error = discord.Embed(
            color=self.color,
            description="¡No tengo permiso para gestionar canales!"
        )
        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)


    try:
        
        await channel.clone()
        success = discord.Embed(
            color=self.color,
            description=f"Se clonó correctamente {channel.name}"
        )
        success.set_author(name="Éxito", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=success)
    except discord.Forbidden:
        error = discord.Embed(
            color=self.color,
            description="¡No tengo permiso para clonar canales!"
        )
        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        await ctx.send(embed=error)
    except Exception as e:
        error = discord.Embed(
            color=self.color,
            description=f"Ocurrió un error al intentar clonar el canal: {str(e)}"
        )
        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        await ctx.send(embed=error)
        

  @commands.hybrid_command(name="nick",
                           aliases=['setnick'],
                           help="Para cambiar el apodo de alguien.",
                           usage="nick [member]")
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(manage_nicknames=True)
  @commands.bot_has_permissions(manage_nicknames=True)
  async def changenickname(self, ctx: commands.Context, member: discord.Member, *, name: str = None):
    
    
    if member == ctx.guild.owner:
        error = discord.Embed(
            color=self.color,
            description="¡No puedo cambiar el apodo del dueño del servidor!"
        )
        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    
    if member.top_role >= ctx.guild.me.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedo cambiar el apodo de un usuario con un rol igual o superior al mío!"
        )
        error.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    
    if ctx.author != ctx.guild.owner and ctx.author.top_role <= member.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedes cambiar el apodo de un usuario con un rol igual o superior al tuyo!"
        )
        error.set_author(name="Acceso denegado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    try:
        await member.edit(nick=name)
        if name:
            success = discord.Embed(
                color=self.color,
                description=f"Se cambió el apodo de {member.mention} a {name}."
            )
            success.set_author(name="Apodo actualizado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
            success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        else:
            success = discord.Embed(
                color=self.color,
                description=f"Se borró el apodo de {member.mention}."
            )
            success.set_author(name="Apodo borrado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
            success.set_footer(text=f"Solicitado por {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=success)
    except discord.Forbidden:
        error = discord.Embed(
            color=self.color,
            description=f"{ZWARNING} | ¡No tengo permiso para gestionar el apodo de este usuario!"
        )
        await ctx.send(embed=error)
    except Exception as e:
        error = discord.Embed(
            color=self.color,
            description=f"{ZWARNING} | Ocurrió un error al intentar cambiar el apodo: {str(e)}"
        )
        await ctx.send(embed=error)
        

  @commands.hybrid_command(name="nuke", help="Elimina y recrea un canal", usage="nuke")
  @blacklist_check()
  @ignore_check()
  @top_check()
  @commands.cooldown(1, 7, commands.BucketType.user)
  @commands.has_permissions(manage_channels=True)
  async def _nuke(self, ctx: commands.Context):
    button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
    button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=CROSS)

    async def button_callback(interaction: discord.Interaction):
      if interaction.user == ctx.author:
        if interaction.guild.me.guild_permissions.manage_channels:
          channel = interaction.channel
          newchannel = await channel.clone()
          await newchannel.edit(position=channel.position)

          await channel.delete()
          embed = discord.Embed(
            description="El canal fue eliminado y recreado correctamente por **`%s`**" % (ctx.author),
            color=self.color)
          embed.set_author(name="Canal recreado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
          embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
          await newchannel.send(embed=embed)
        else:
          await interaction.response.edit_message(
            content=
            f"{ZWARNING} | Parece que me faltan los permisos necesarios. Concédeme el permiso `gestionar canal` e inténtalo de nuevo.",
            embed=None,
            view=None)
      else:
        await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

    async def button1_callback(interaction: discord.Interaction):
      if interaction.user == ctx.author:
        await interaction.response.edit_message(
          content="Cancelado, no eliminaré ni recrearé el canal.", embed=None, view=None)
      else:
        await interaction.response.send_message("¡Ups! Parece que ese mensaje no es tuyo. Debes ejecutar el comando tú mismo para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

    embed = discord.Embed(
      color=self.color, description='**¿Seguro que quieres eliminar y recrear el canal?**')

    view = View()
    button.callback = button_callback
    button1.callback = button1_callback
    view.add_item(button)
    view.add_item(button1)
    embed.set_footer(text="Haz clic en 'Confirmar' o 'Cancelar' para continuar. ¡Tienes 30 segundos para decidir!")
    await ctx.reply(embed=embed, view=view, mention_author=False,delete_after=30)



  @commands.hybrid_command(name="slowmode",
                           help="Cambia el modo lento",
                           usage="slowmode [seconds]",
                           aliases=["slow"])
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  async def _slowmode(self, ctx: commands.Context, seconds: int = 0):
    if seconds > 120:
      embed=discord.Embed(description="El modo lento no puede superar los 2 minutos",
                            color=self.color)
      embed.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
      embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      return await ctx.send(embed=embed)
    if seconds == 0:
      await ctx.channel.edit(slowmode_delay=seconds)
      await ctx.send(embed=discord.Embed(
        title="Modo lento", description="El modo lento está desactivado", color=self.color))
    else:
      await ctx.channel.edit(slowmode_delay=seconds)
      embed=discord.Embed(description="Se estableció el modo lento en **`%s`**" % (seconds),
                            color=self.color)
      embed.set_author(name="Modo lento activado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
      embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.send(embed=embed)
      

  @commands.hybrid_command(name="unslowmode",
                           help="Desactiva el modo lento",
                           usage="unslowmode",
                           aliases=["unslow"])
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.has_permissions(manage_messages=True)
  @commands.bot_has_permissions(manage_messages=True)
  async def _unslowmode(self, ctx: commands.Context):
    await ctx.channel.edit(slowmode_delay=0)
    embed=discord.Embed(description="Se desactivó el modo lento", color=self.color)
    embed.set_author(name="Modo lento desactivado", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
    embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)



  @commands.command(aliases=["deletesticker", "removesticker"], description="Elimina el sticker del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_emojis=True)
  @commands.bot_has_permissions(manage_emojis=True)
  async def delsticker(self, ctx: commands.Context, *, name=None):
        if ctx.message.reference is None:
            return await ctx.reply("No se encontró un mensaje respondido")
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if len(msg.stickers) == 0:
            return await ctx.reply("No se encontró ningún sticker")
        try:
            name = ""
            for i in msg.stickers:
                name = i.name
                await ctx.guild.delete_sticker(i)
            await ctx.reply(f"{TICK}> Se eliminó correctamente el sticker llamado `{name}`")
        except:
            await ctx.reply("No se pudo eliminar el sticker")


  @commands.command(aliases=["deleteemoji", "removeemoji"], description="Elimina el emoji del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(manage_emojis=True)
  async def delemoji(self, ctx, emoji: str = None):
    init_message = await ctx.reply("Procesando la eliminación de emojis...", mention_author=False)
    message_content = None

    
    if ctx.message.reference is not None:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        message_content = str(referenced_message.content)
    else:
        message_content = str(ctx.message.content)

    
    if message_content:
        
        emoji_pattern = r"<a?:\w+:(\d+)>"
        found_emojis = re.findall(emoji_pattern, message_content)
        delete_count = 0

        if len(found_emojis) != 0:
            
            if len(found_emojis) > 15:
                await init_message.delete()
                return await ctx.reply("Se pueden eliminar como máximo 15 emojis a la vez.")

            
            for emoji_id in found_emojis:
                try:
                    emoji_to_delete = await ctx.guild.fetch_emoji(int(emoji_id))
                    await emoji_to_delete.delete(reason=f"Eliminado por {ctx.author}")
                    delete_count += 1
                except discord.NotFound:
                    continue  
                except discord.Forbidden:
                    continue  
            await init_message.delete()
            return await ctx.reply(f"{TICK}> | Se eliminaron {delete_count}/{len(found_emojis)} emoji(s) correctamente.")

    
    await init_message.delete()
    return await ctx.reply("No se encontró ningún emoji válido para eliminar.")



  
  @commands.command(description="Cambia el icono del rol.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  @commands.bot_has_guild_permissions(manage_roles=True)
  async def roleicon(self, ctx: commands.Context, role: discord.Role, *, icon: Union[discord.Emoji, discord.PartialEmoji, str] = None):
    
    if role.position >= ctx.guild.me.top_role.position:
        error_embed = discord.Embed(
            description=f"{role.mention} está por encima de mi rol. Mueve mi rol por encima de él.",
            color=self.color
        )
        error_embed.set_author(name="Error", icon_url="https://cdn.discordapp.com/avatars/1396114795102470196/198b9bc616ec574f6fd2f7121a1d3abc.png?size=1024")
        error_embed.set_footer(
            text=f"Solicitado por {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        return await ctx.send(embed=error_embed)

    
    if ctx.author != ctx.guild.owner and ctx.author.top_role.position <= role.position:
        error_embed = discord.Embed(
            description=f"¡{role.mention} tiene la misma posición o una superior a tu rol más alto!",
            color=self.color
        )
        error_embed.set_author(name="Error")
        error_embed.set_footer(
            text=f"Solicitado por {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        return await ctx.send(embed=error_embed)

    
    if icon is None:
        attachment_found = False
        attachment_url = None
        for attachment in ctx.message.attachments:
            attachment_url = attachment.url
            attachment_found = True

        if attachment_found:
            try:
                async with aiohttp.request("GET", attachment_url) as r:
                    image_data = await r.read()
                await role.edit(display_icon=image_data)
                success_embed = discord.Embed(
                    description=f"Se cambió el icono de {role.mention} correctamente.",
                    color=self.color
                )
                success_embed.set_author(name="Icono actualizado")
                success_embed.set_footer(
                    text=f"Solicitado por {ctx.author}",
                    icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
                )
                return await ctx.send(embed=success_embed)
            except Exception as e:
                print(e)
                return await ctx.reply("No se pudo cambiar el icono del rol.")
        else:
            await role.edit(display_icon=None)
            removal_embed = discord.Embed(
                description=f"Se quitó el icono de {role.mention} correctamente.",
                color=self.color
            )
            removal_embed.set_author(name="Icono quitado")
            removal_embed.set_footer(
                text=f"Solicitado por {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.reply(embed=removal_embed, mention_author=False)

    
    if isinstance(icon, discord.Emoji) or isinstance(icon, discord.PartialEmoji):
        emoji_url = f"https://cdn.discordapp.com/emojis/{icon.id}.png"
        try:
            async with aiohttp.request("GET", emoji_url) as r:
                image_data = await r.read()
            await role.edit(display_icon=image_data)
            success_embed = discord.Embed(
                description=f"Se cambió el icono de {role.mention} a {icon} correctamente.",
                color=self.color
            )
            success_embed.set_author(name="Icono actualizado")
            success_embed.set_footer(
                text=f"Solicitado por {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.reply(embed=success_embed, mention_author=False)
        except Exception as e:
            print(e)
            return await ctx.reply("No se pudo cambiar el icono del rol.")

    
    else:
        if not icon.startswith("https://"):
            return await ctx.reply("Proporciona un enlace válido.")
        try:
            async with aiohttp.request("GET", icon) as r:
                image_data = await r.read()
            await role.edit(display_icon=image_data)
            success_embed = discord.Embed(
                description=f"{TICK}>| Se cambió el icono de {role.mention} correctamente.",
                color=self.color
            )
            return await ctx.reply(embed=success_embed, mention_author=False)
        except Exception as e:
            print(e)
            return await ctx.reply("Ocurrió un error al cambiar el icono del rol.")
  
  
      
  @commands.hybrid_command(name="unbanall",
                           help="¡Desbanea a todos en el servidor!",
                           aliases=['massunban'],
                           usage="Unbanall",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 30, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(ban_members=True)
  async def unbanall(self, ctx):
    button = Button(label="Confirmar",
                    style=discord.ButtonStyle.green,
                    emoji=f"{TICK}>")
    button1 = Button(label="Cancelar",
                     style=discord.ButtonStyle.red,
                     emoji=CROSS)

    async def button_callback(interaction: discord.Interaction):
      a = 0
      if interaction.user == ctx.author:
        if interaction.guild.me.guild_permissions.ban_members:
          await interaction.response.edit_message(
            content="Desbaneando a todos los miembros baneados...", embed=None, view=None)
          async for idk in interaction.guild.bans(limit=None):
            await interaction.guild.unban(
              user=idk.user,
              reason="Comando Unbanall ejecutado por: {}".format(ctx.author))
            a += 1
          await interaction.channel.send(
            content=f"{TICK}> Se desbanearon {a} miembros correctamente")
        else:
          await interaction.response.edit_message(
            content=
            "Me falta el permiso `banear miembros` en este servidor.",
            embed=None,
            view=None)
      else:
        await interaction.response.send_message("¡Vaya! Ese mensaje no te pertenece.\nDebes ejecutar este comando para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

    async def button1_callback(interaction: discord.Interaction):
      if interaction.user == ctx.author:
        await interaction.response.edit_message(
          content="Cancelado, no desbanearé a nadie.", embed=None, view=None)
      else:
        await interaction.response.send_message("¡Vaya! Ese mensaje no te pertenece.\nDebes ejecutar este comando para interactuar con él.",
                                                embed=None,
                                                view=None,
                                                ephemeral=True)

    embed = discord.Embed(
      color=self.color,
      description='**¿Seguro que quieres desbanear a todos los miembros de este servidor?**')

    view = View()
    button.callback = button_callback
    button1.callback = button1_callback
    view.add_item(button)
    view.add_item(button1)
    await ctx.reply(embed=embed, view=view, mention_author=False)
  
  @commands.hybrid_command(name="audit",
                           help="Mira las acciones recientes del registro de auditoría del servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.has_permissions(view_audit_log=True)
  @commands.bot_has_permissions(view_audit_log=True)
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def auditlog(self, ctx, limit: int):
    if limit >= 31:
      await ctx.reply(
        "Acción rechazada, no se te permite obtener más de `30` entradas.",
        mention_author=False)
      return
    idk = []
    str = ""
    async for entry in ctx.guild.audit_logs(limit=limit):
      idk.append(f'''Usuario: `{entry.user}`
Acción: `{entry.action}`
Objetivo: `{entry.target}`
Razón: `{entry.reason}`\n\n''')
    for n in idk:
      str += n
    str = str.replace("AuditLogAction.", "")
    embed = discord.Embed(title=f"Registros de auditoría de {ctx.guild.name}",
                          description=f">>> {str}",
                          color=0xFF0000)
    embed.set_footer(text=f"Acciones del registro de auditoría de {ctx.guild.name}")
    await ctx.reply(embed=embed, mention_author=False)
      
