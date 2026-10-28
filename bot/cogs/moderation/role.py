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
from utils.emoji import CROSS, TICK, ZWARNING
import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import re
from typing import *
from utils.Tools import *
from discord.ui import Button, View
from typing import Union, Optional
from typing import Union, Optional
from io import BytesIO
import requests
import aiohttp
import time
from datetime import datetime, timezone, timedelta


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


class Role(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.color = 0xFF0000


  @commands.group(name="role",invoke_without_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.has_permissions(manage_roles=True)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @top_check()
  @blacklist_check()
  async def role(self, ctx, member: discord.Member, *, role: discord.Role):
    if not ctx.guild.me.guild_permissions.manage_roles:
        return await ctx.send(f"{ZWARNING} ¡No tengo permiso para gestionar roles!")

    if role >= ctx.guild.me.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedo gestionar roles de un usuario con un rol igual o superior!"
        )

        error.set_author(name="Error")
        error.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=error)

    if ctx.author != ctx.guild.owner and ctx.author.top_role <= member.top_role:
        error = discord.Embed(
            color=self.color,
            description="¡No puedes gestionar roles de un usuario con un rol igual o superior al tuyo!"
        )
        error.set_author(name="Acceso denegado")
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
            success.set_author(name="Rol agregado")
            success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        else:
            await member.remove_roles(role, reason=f"Rol quitado por {ctx.author} (ID: {ctx.author.id})")
            success = discord.Embed(
                color=self.color,
                description=f"Se **quitó** el rol {role.name} de {member.mention} correctamente."
            )
            success.set_author(name="Rol quitado")
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


  @role.command(help="Otorga un rol a un miembro por un tiempo determinado")
  @commands.bot_has_permissions(manage_roles=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 7, commands.BucketType.user)
  @commands.has_permissions(manage_roles=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def temp(self, ctx, role: discord.Role, time, *, user: discord.Member):
    if ctx.author != ctx.guild.owner and role.position >= ctx.author.top_role.position:
        embed = discord.Embed(
              description=f"¡No puedes gestionar un rol igual o superior a tu rol más alto!",
              color=self.color
          )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)
          
    else:
      if role.position >= ctx.guild.me.top_role.position:
        embed1 = discord.Embed(
          description=
          f"{role} está por encima de mi rol más alto, mueve mi rol por encima de {role}.",
          color=self.color)
        embed1.set_author(name="Error")
        embed1.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed1)
    seconds = convert(time)
    await user.add_roles(role, reason=None)
    success = discord.Embed(
      description=
      f"Se agregó {role.mention} a {user.mention} correctamente.",
      color=self.color)
    success.set_author(name="Éxito")
    success.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.send(embed=success)
    await asyncio.sleep(seconds)
    await user.remove_roles(role)

  
  @role.command(help="Elimina un rol del servidor")
  @blacklist_check()
  @ignore_check()
  @top_check()
  @commands.cooldown(1, 7, commands.BucketType.user)
  @commands.has_permissions(manage_roles=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def delete(self, ctx, *, role: discord.Role):
    if ctx.author != ctx.guild.owner and role.position >= ctx.author.top_role.position:
        embed = discord.Embed(
            description=f"¡No puedes eliminar un rol igual o superior a tu rol más alto!",
            color=self.color
        )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)

    if role.position >= ctx.guild.me.top_role.position:
        embed = discord.Embed(
            description=f"No puedo eliminar {role} porque está por encima de mi rol más alto. Mueve mi rol por encima de {role}.",
            color=self.color
        )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)

    if role is None:
        embed = discord.Embed(
            description=f"No se encontró ningún rol llamado {role} en este servidor.",
            color=self.color
        )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)

    await role.delete()
    
    embed = discord.Embed(
        description=f"Se eliminó {role} correctamente.",
        color=self.color
    )
    embed.set_author(name="Éxito")
    embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)
      
  @role.command(help="Crea un rol en el servidor")
  @blacklist_check()
  @ignore_check()
  @top_check()
  @commands.cooldown(1, 7, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def create(self, ctx, *, name):
    embed = discord.Embed(
        description=f"Se creó el rol {name} correctamente.",
        color=self.color
    )
    embed.set_author(name="Éxito")
    embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.guild.create_role(name=name, color=discord.Color.default())
    await ctx.send(embed=embed)


  @role.command(help="Cambia el nombre de un rol en el servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def rename(self, ctx, role: discord.Role, *, newname):
    
    if role.position >= ctx.author.top_role.position:
        embed = discord.Embed(
            description=f"No puedes gestionar el rol {role.mention} porque es igual o superior a tu rol más alto.",
            color=self.color
        )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)

    
    if role.position >= ctx.guild.me.top_role.position:
        embed = discord.Embed(
            description=f"No puedo gestionar el rol {role.mention} porque está por encima de mi rol más alto.",
            color=self.color
        )
        embed.set_author(name="Error")
        embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.send(embed=embed)

    await role.edit(name=newname)
    embed = discord.Embed(
        description=f"El rol {role.name} se renombró a {newname}.",
        color=self.color
    )
    embed.set_author(name="Éxito")
    embed.set_footer(text=f"Solicitado por {ctx.author}",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)                  

  @role.command(name="humans", help="Otorga el rol a todos los humanos del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 15, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def role_humans(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Asignando {role.mention} a todos los humanos...")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        if not member.bot and role not in member.roles:
                            try:
                                await member.add_roles(role, reason=f"Comando Role Humans ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se asignó {role.mention} a {count} humano(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content=f"{ZWARNING} Me faltan los permisos necesarios. Concédelos e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. No se asignará el rol {role.mention} a ningún humano.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        members_without_role = [member for member in ctx.guild.members if not member.bot and role not in member.roles]
        if len(members_without_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{ZWARNING} | Todos los humanos ya tienen el rol {role.mention}.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f"¿Seguro que quieres asignar {role.mention} a {len(members_without_role)} miembros?")
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)

    else:
        denied = discord.Embed(title=f"{ZWARNING} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)



  @role.command(name="bots", help="Otorga el rol a todos los bots del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def role_bots(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Agregando {role.mention} a todos los bots...")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        if member.bot and role not in member.roles:
                            try:
                                await member.add_roles(role, reason=f"Comando Role Bots ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se agregó {role.mention} a {count} bot(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. No se asignará el rol {role.mention} a ningún bot.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        bots_without_role = [member for member in ctx.guild.members if member.bot and role not in member.roles]
        if len(bots_without_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{ZWARNING} | Todos los bots ya tienen el rol {role.mention}.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f"**¿Seguro que quieres dar {role.mention} a {len(bots_without_role)} bots?**")
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)

    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)



  @role.command(name="unverified", help="Otorga el rol a todos los miembros no verificados del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def role_unverified(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Agregando {role.mention} a todos los miembros no verificados.")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        if member.avatar is None and role not in member.roles:
                            try:
                                await member.add_roles(role, reason=f"Comando Role Unverified ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se agregó {role.mention} a {count} miembro(s) no verificado(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. No se asignará el rol {role.mention} a ningún miembro no verificado.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        embed = discord.Embed(
            color=self.color,
            description=f'**¿Seguro que quieres dar {role.mention} a todos los miembros no verificados de este servidor?**')
        view = View()
        button.callback = button_callback
        button1.callback = button1_callback
        view.add_item(button)
        view.add_item(button1)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)


  @role.command(name="all", help="Otorga el rol a todos los miembros del servidor")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 15, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(administrator=True)
  async def role_all(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Agregando {role.mention} a todos los miembros.")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        try:
                            await member.add_roles(role, reason=f"Comando Role All ejecutado por: {ctx.author}")
                            count += 1
                        except Exception as e:
                            print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se agregó {role.mention} a {count} miembro(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. No se asignará el rol {role.mention} a ningún miembro.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        members_without_role = [member for member in ctx.guild.members if role not in member.roles]
        if len(members_without_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"{ZWARNING} | {role.mention} ya está asignado a todos los miembros del servidor.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f'**¿Seguro que quieres dar {role.mention} a {len(members_without_role)} miembros?**')
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)
    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)



  @commands.group(name="removerole",invoke_without_command=True,
                 aliases=['rrole'],
                   help="Quita un rol de todos los miembros.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 5, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @blacklist_check()
  @commands.has_permissions(administrator=True)
  async def rrole(self,ctx):
    if ctx.subcommand_passed is None:
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)


  @rrole.command(name="humans", help="Quita un rol de todos los humanos del servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  async def rrole_humans(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Quitando {role.mention} de todos los humanos.")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        if not member.bot and role in member.roles:
                            try:
                                await member.remove_roles(role, reason=f"Comando Remove Role Humans ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}>| Se quitó {role.mention} de {count} humano(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. {role.mention} no se quitará de ningún humano.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        humans_with_role = [member for member in ctx.guild.members if not member.bot and role in member.roles]
        if len(humans_with_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"| Ningún humano tiene {role.mention}.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f'**¿Seguro que quieres quitar {role.mention} de {len(humans_with_role)} humanos de este servidor?**')
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)
    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)

        await ctx.send(embed=embed, mention_author=False)
        


  @rrole.command(name="bots", help="Quita un rol de todos los bots del servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  async def rrole_bots(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Quitando {role.mention} de todos los bots...")
                    await interaction.response.edit_message(embed=embed1, view=None)
                    for member in interaction.guild.members:
                        if member.bot and role in member.roles:
                            try:
                                await member.remove_roles(role, reason=f"Comando Remove Role Bots ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se quitó {role.mention} de {count} bot(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. {role.mention} no se quitará de ningún bot.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        bots_with_role = [member for member in ctx.guild.members if member.bot and role in member.roles]
        if len(bots_with_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"| Ningún bot tiene {role.mention}.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f'**¿Seguro que quieres quitar {role.mention} de {len(bots_with_role)} bots de este servidor?**')
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)
    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)

    



  @rrole.command(name="all", help="Quita un rol de todos los miembros del servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  async def rrole_all(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Confirm",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            removed_count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Quitando {role.mention} de todos los miembros.")
                    await interaction.response.edit_message(embed=embed1, view=None)

                    for member in interaction.guild.members:
                        if role in member.roles:
                            try:
                                await member.remove_roles(role, reason=f"Comando Remove Role All ejecutado por: {ctx.author}")
                                removed_count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}>| Se quitó {role.mention} de {removed_count} miembro(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message("¡Esta acción no es para ti!",
                                                        embed=None,
                                                        view=None,
                                                        ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. {role.mention} no se quitará de nadie.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message("¡Esta acción no es para ti!",
                                                        embed=None,
                                                        view=None,
                                                        ephemeral=True)

        members_with_role = [member for member in ctx.guild.members if role in member.roles]
        if len(members_with_role) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"| Ningún miembro tiene {role.mention} actualmente.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f'**¿Seguro que quieres quitar {role.mention} de {len(members_with_role)} miembros de este servidor?**')
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)
    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)

    
    

  @rrole.command(name="unverified", help="Quita un rol de todos los miembros no verificados del servidor.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 10, commands.BucketType.user)
  @commands.has_permissions(administrator=True)
  async def rrole_unverified(self, ctx, *, role: discord.Role):
    if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
        button = Button(label="Sí",
                        style=discord.ButtonStyle.green,
                        emoji=f"{TICK}>")
        button1 = Button(label="No",
                         style=discord.ButtonStyle.red,
                         emoji=CROSS)

        async def button_callback(interaction: discord.Interaction):
            count = 0
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.manage_roles:
                    embed1 = discord.Embed(
                        color=self.color,
                        description=f"Quitando {role.mention} de todos los miembros no verificados.")
                    await interaction.response.edit_message(embed=embed1, view=None)

                    for member in interaction.guild.members:
                        if member.avatar is None and role in member.roles:
                            try:
                                await member.remove_roles(role, reason=f"Comando Remove Role Unverified ejecutado por: {ctx.author}")
                                count += 1
                            except Exception as e:
                                print(e)

                    await interaction.channel.send(
                        content=f"{TICK}> | Se quitó {role.mention} de {count} miembro(s) no verificado(s) correctamente.")
                else:
                    await interaction.response.edit_message(
                        content="Me falta el permiso necesario. Concédelo e inténtalo de nuevo.",
                        embed=None,
                        view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                embed2 = discord.Embed(
                    color=self.color,
                    description=f"Acción cancelada. {role.mention} no se quitará de ningún miembro no verificado.")
                await interaction.response.edit_message(embed=embed2, view=None)
            else:
                await interaction.response.send_message(
                    "¡Esta acción no es para ti!",
                    embed=None,
                    view=None,
                    ephemeral=True)

        unverified_members = [member for member in ctx.guild.members if member.avatar is None and role in member.roles]
        if len(unverified_members) == 0:
            return await ctx.reply(embed=discord.Embed(description=f"| Ningún miembro no verificado tiene {role.mention}.", color=self.color))
        else:
            embed = discord.Embed(
                color=self.color,
                description=f'**¿Seguro que quieres quitar {role.mention} de {len(unverified_members)} miembros no verificados de este servidor?**')
            view = View()
            button.callback = button_callback
            button1.callback = button1_callback
            view.add_item(button)
            view.add_item(button1)
            await ctx.reply(embed=embed, view=view, mention_author=False)
    else:
        denied = discord.Embed(title=f"{CROSS} Acceso denegado",
            description="Tu rol debe estar por encima de mi rol más alto.",
            color=0xFF0000)
        denied.set_footer(text=f"Comando “{ctx.command.qualified_name}” ejecutado por {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=denied, mention_author=False)

  

 