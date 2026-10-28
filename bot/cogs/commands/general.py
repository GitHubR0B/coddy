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

import asyncio
import discord
from utils.emoji import CROSS, TICK, ZWARNING, ZYROXCONNECTION, ZYROXLINKS
from discord.ext import commands, tasks
from discord.utils import get
import datetime
import random
import requests
import aiohttp
import re
from discord.ext.commands.errors import BadArgument
from discord.ext.commands import Cog
from discord.colour import Color
import hashlib
from utils.Tools import *
from traceback import format_exception
from discord import ButtonStyle
from discord.ui import Button, View, LayoutView, TextDisplay, Separator, MediaGallery, ActionRow
import psutil
import time
from datetime import datetime, timezone, timedelta
import sqlite3
from typing import *
import string
from utils.cv2 import CV2, build_container

lawda = [
  '8', '3821', '23', '21', '313', '43', '29', '76', '11', '9',
  '44', '470', '318' , '26', '69'
]


class AvatarView(View):
  def __init__(self, user, member, author_id, banner_url):
    super().__init__()
    self.user = user
    self.member = member
    self.author_id = author_id
    self.banner_url = banner_url

    if self.user.avatar.is_animated():
      self.add_item(Button(label='GIF', url=self.user.avatar.with_format('gif').url, style=discord.ButtonStyle.link))
    self.add_item(Button(label='PNG', url=self.user.avatar.with_format('png').url, style=discord.ButtonStyle.link))
    self.add_item(Button(label='JPEG', url=self.user.avatar.with_format('jpg').url, style=discord.ButtonStyle.link))
    self.add_item(Button(label='WEBP', url=self.user.avatar.with_format('webp').url, style=discord.ButtonStyle.link))

  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if interaction.user.id != self.author_id:
      await interaction.response.send_message(
        "¡Ups! Ese mensaje no es tuyo. Debes ejecutar este comando para interactuar con él.",
        ephemeral=True
      )
      return False
    return True

  @discord.ui.button(label='Avatar del servidor', style=discord.ButtonStyle.success, custom_id='server_avatar_button')
  async def server_avatar(self, interaction: discord.Interaction, button: Button):
    if not self.member.guild_avatar:
      await interaction.response.send_message(
        "Este usuario no tiene un avatar distinto en el servidor.",
        ephemeral=True
      )
    else:
      embed = interaction.message.embeds[0]
      embed.set_image(url=self.member.guild_avatar.url)
      await interaction.response.edit_message(embed=embed)

  @discord.ui.button(label='Banner del usuario', style=discord.ButtonStyle.success, custom_id='banner_button')
  async def banner(self, interaction: discord.Interaction, button: Button):
    if not self.banner_url:
      await interaction.response.send_message(
        "Este usuario no tiene banner.",
        ephemeral=True
      )
    else:
      embed = interaction.message.embeds[0]
      embed.set_image(url=self.banner_url)
      await interaction.response.edit_message(embed=embed)


from utils.config import BotName

class General(commands.Cog):

  def __init__(self, bot, *args, **kwargs):
    self.bot = bot
    self.aiohttp = aiohttp.ClientSession()
    self._URL_REGEX = r'(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;"\'\\]\s])'
    self.color = 0xFF0000


  @commands.hybrid_command(
    usage="Avatar <member>",
    name='avatar',
    aliases=['av'],
    help="Obtén el avatar de un usuario/servidor y el banner de un usuario."
  )
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def _user(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None):
    try:
      if member is None:
        member = ctx.author
      user = await self.bot.fetch_user(member.id)

      banner_url = user.banner.url if user.banner else None

      # Avatar still uses embed because AvatarView buttons edit embed images
      description = f"[`PNG`]({user.avatar.with_format('png').url}) | [`JPG`]({user.avatar.with_format('jpg').url}) | [`WEBP`]({user.avatar.with_format('webp').url})"
      if user.avatar.is_animated():
        description += f" | [`GIF`]({user.avatar.with_format('gif').url})"
      if banner_url:
        description += f" | [`Banner`]({banner_url})"

      embed = discord.Embed(
        color=self.color,
        description=description
      )
      embed.set_author(name=f"{member}", icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
      embed.set_image(url=user.avatar.url)
      embed.set_footer(text=f"Solicitado por {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

      view = AvatarView(user, member, ctx.author.id, banner_url)
      await ctx.send(embed=embed, view=view)
    except Exception as e:
      print(f"Error: {e}")

  @commands.hybrid_command(
    name="servericon",
    help="Obtén el icono del servidor",
    usage="Servericon"
  )
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def servericon(self, ctx: commands.Context):
    server = ctx.guild
    if server.icon is None:
      await ctx.reply(view=CV2("❌ Error", "Este servidor no tiene icono."))
      return

    webp = server.icon.replace(format='webp')
    jpg = server.icon.replace(format='jpg')
    png = server.icon.replace(format='png')

    links = f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
    if server.icon.is_animated():
      gif = server.icon.replace(format='gif')
      links += f" | [`GIF`]({gif})"

    view = LayoutView(timeout=None)
    gallery = MediaGallery()
    gallery.add_item(media=str(server.icon.url))
    dl_btn = Button(label="Descargar icono", url=str(server.icon.url), style=ButtonStyle.link)
    view.add_item(build_container(
        TextDisplay(f"**Icono de {server}**"),
        Separator(visible=True),
        TextDisplay(links),
        gallery,
        ActionRow(dl_btn)
    ))
    await ctx.send(view=view)


  @commands.hybrid_command(name="membercount",
                           help="Obtén el total de miembros del servidor",
                           usage="membercount",
                           aliases=["mc"])
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  async def membercount(self, ctx: commands.Context):
        total_members = len(ctx.guild.members)
        total_humans = len([m for m in ctx.guild.members if not m.bot])
        total_bots = len([m for m in ctx.guild.members if m.bot])

        online = len([m for m in ctx.guild.members if m.status == discord.Status.online])
        offline = len([m for m in ctx.guild.members if m.status == discord.Status.offline])
        idle = len([m for m in ctx.guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in ctx.guild.members if m.status == discord.Status.do_not_disturb])

        stats_text = (
            f"**__Estadísticas de conteo:__**\n"
            f"Miembros totales: {total_members}\nHumanos totales: {total_humans}\nBots totales: {total_bots}\n\n"
            f"**__Estadísticas de presencia:__**\n"
            f"En línea: {online} | No molestar: {dnd} | Ausente: {idle} | Desconectado: {offline}"
        )
        await ctx.send(view=CV2("Estadísticas de miembros", stats_text))

  @commands.hybrid_command(name="poll", usage="Poll <message>")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def poll(self, ctx: commands.Context, *, message):
    author = ctx.author
    msg = await ctx.send(view=CV2(f"**¡Encuesta creada por {author}!**", message))
    await msg.add_reaction(TICK)
    await msg.add_reaction(CROSS)


  @commands.command(name="hack",
    help="hackea la cuenta de Discord de alguien",
    usage="Hack <member>")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def hack(self, ctx: commands.Context, member: discord.Member):
    stringi = member.name
    min_length = 2
    max_length = 12
    length = random.randint(min_length, max_length)
    stringg = member.name
    remaining_length = length - len(stringg)
    all_chars = string.ascii_letters + string.digits + string.punctuation
    random_chars = random.choices(all_chars, k=remaining_length)

    password = stringg + ''.join(random_chars)

    lund = await ctx.send(f"Procesando el hackeo de {member.mention}...")
    await asyncio.sleep(2)
    random_pass = random.choice(lawda)

    random_pass2 = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
    hack_text = (
        f"**Usuario:** {member.mention}\n"
        f"**Correo:** {''.join(c for c in stringi if c.isalnum())}{random_pass}@gmail.com\n"
        f"**Contraseña de la cuenta:** {member.name}@{random_pass2}"
    )
    await ctx.send(view=CV2(f"¡{member.display_name} hackeado!", hack_text))
    await lund.delete()


  @commands.command(name="token", usage="Token <member>")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 2, commands.BucketType.user)
  async def token(self, ctx: commands.Context, user: discord.Member = None):
    list = [
      "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
      "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "_"
      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
      'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0',
      '1', '2', '3', '4', '5', '6', '7', '8', '9'
    ]
    token = random.choices(list, k=59)
    if user is None:
      user = ctx.author
    await ctx.send(view=CV2("🔐 Token", f"Token de {user.mention}: `{''.join(token)}`"))

  @commands.command(name="users", help=f"muestra el total de usuarios de {BotName}.")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def users(self, ctx: commands.Context):
    users = sum(g.member_count for g in self.bot.guilds
                if g.member_count != None)
    guilds = len(self.bot.guilds)
    await ctx.send(view=CV2(f"Usuarios de {BotName}", f"❯ Total de __**{users}**__ usuarios en **{guilds}** servidores"))


  @commands.command(name="wizz", usage="Wizz")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def wizz(self, ctx: commands.Context):
    message6 = await ctx.send(
      f"`Aplicando wizz a {ctx.guild.name}, tardará 22 segundos en completarse`")
    message7 = await ctx.send(f"Cambiando todos los ajustes del servidor...")
    message5 = await ctx.send(f"Eliminando **{len(ctx.guild.roles)}** roles...")
    await asyncio.sleep(1)
    message4 = await ctx.send(
      f"Eliminando **{len(ctx.guild.channels)}** canales...")
    await asyncio.sleep(1)
    message3 = await ctx.send(f"Eliminando webhooks...")
    message2 = await ctx.send(f"Eliminando emojis")
    await asyncio.sleep(1)
    message1 = await ctx.send(f"Instalando oleada de baneos...")
    await asyncio.sleep(1)
    await message6.delete()
    await message7.delete()
    await message5.delete()
    await message4.delete()
    await message3.delete()
    await message2.delete()
    await message1.delete()
    await ctx.send(view=CV2(f"{self.bot.user.name}", f"**{ZWARNING} Wizz aplicado con éxito en {ctx.guild.name}**"))


  @commands.hybrid_command(
    name="urban",
    description="Busca la frase indicada en urbandictionary",
    help="Obtén el significado de la frase indicada",
    usage="Urban <phrase>")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def urban(self, ctx: commands.Context, *, phrase):
    async with self.aiohttp.get(
        "http://api.urbandictionary.com/v0/define?term={}".format(
          phrase)) as urb:
      urban = await urb.json()
      try:
        definition = urban['list'][0]['definition'].replace('[', '').replace(']', '')
        example = urban['list'][0]['example'].replace('[', '').replace(']', '')
        author = urban['list'][0]['author'].replace('[', '').replace(']', '')
        written_on = urban['list'][0]['written_on'].replace('[', '').replace(']', '')

        urban_text = (
            f"**__Definición:__**\n{definition}\n\n"
            f"**__Ejemplo:__**\n{example}\n\n"
            f"**__Autor:__** {author}\n"
            f"**__Escrito el:__** {written_on}"
        )
        temp = await ctx.reply(view=CV2(f"Significado de \"{phrase}\"", urban_text), mention_author=True)
        await asyncio.sleep(45)
        await temp.delete()
        await ctx.message.delete()
      except:
        pass

  @commands.command(name="rickroll",
                           help="Detecta si la url proporcionada es un rick-roll",
                           usage="Rickroll <url>")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def rickroll(self, ctx: commands.Context, *, url: str):
    if not re.match(self._URL_REGEX, url):
      raise BadArgument("URL inválida")

    phrases = [
      "rickroll", "rick roll", "rick astley", "never gonna give you up"
    ]
    source = str(await (await self.aiohttp.get(
      url, allow_redirects=True)).content.read()).lower()
    rickRoll = bool((re.findall('|'.join(phrases), source,
                                re.MULTILINE | re.IGNORECASE)))
    title = "Rick Roll {} en la página".format("encontrado" if rickRoll else "no encontrado")
    await ctx.reply(view=CV2(title, "🎵 ¡Nunca te rendiré, nunca te decepcionaré!" if rickRoll else "✅ ¡Seguro para hacer clic!"), mention_author=True)

  @commands.command(name="hash",
                           help="Genera el hash del texto indicado con el algoritmo indicado")
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def hash(self, ctx: commands.Context, algorithm: str, *, message):
    algos: dict[str, str] = {
      "md5": hashlib.md5(bytes(message.encode("utf-8"))).hexdigest(),
      "sha1": hashlib.sha1(bytes(message.encode("utf-8"))).hexdigest(),
      "sha224": hashlib.sha224(bytes(message.encode("utf-8"))).hexdigest(),
      "sha3_224": hashlib.sha3_224(bytes(message.encode("utf-8"))).hexdigest(),
      "sha256": hashlib.sha256(bytes(message.encode("utf-8"))).hexdigest(),
      "sha3_256": hashlib.sha3_256(bytes(message.encode("utf-8"))).hexdigest(),
      "sha384": hashlib.sha384(bytes(message.encode("utf-8"))).hexdigest(),
      "sha3_384": hashlib.sha3_384(bytes(message.encode("utf-8"))).hexdigest(),
      "sha512": hashlib.sha512(bytes(message.encode("utf-8"))).hexdigest(),
      "sha3_512": hashlib.sha3_512(bytes(message.encode("utf-8"))).hexdigest(),
      "blake2b": hashlib.blake2b(bytes(message.encode("utf-8"))).hexdigest(),
      "blake2s": hashlib.blake2s(bytes(message.encode("utf-8"))).hexdigest()
    }
    if algorithm.lower() not in list(algos.keys()):
      hash_lines = "\n".join(f"**{algo}:** `{algos[algo]}`" for algo in algos)
    else:
      hash_lines = f"**{algorithm}:** `{algos[algorithm.lower()]}`"
    await ctx.reply(view=CV2(f"Hash de \"{message}\"", hash_lines), mention_author=True)

  @commands.command(
      name="invite",
      aliases=['invite-bot'],
      description="¡Obtén el enlace de soporte y de invitación del bot!"
  )
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 3, commands.BucketType.user)
  async def invite(self, ctx: commands.Context):
      invite_text = (
          "```¡Potencia tu servidor con funciones ultrarrápidas y soporte 24/7!```\n"
          f"{ZYROXLINKS} **Acciones rápidas**\n"
          f">>> **[Invita a {BotName}](https://discord.com/oauth2/authorize?client_id=1396114795102470196&permissions=8&integration_type=0&scope=bot+applications.commands)**\n"
          "**[Servidor de soporte](https://discord.gg/codexdev)**"
      )
      await ctx.send(view=CV2(f"{ZYROXCONNECTION} ¡Centro de integración de {BotName}!", invite_text))