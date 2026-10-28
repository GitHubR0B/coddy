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
from utils.emoji import ZMODULE
from discord.ext import commands


class _general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """General commands"""

    def help_custom(self):
              emoji = ZMODULE
              label = "Comandos generales"
              description = "Te muestra los comandos generales"
              return emoji, label, description

    @commands.group()
    async def __General__(self, ctx: commands.Context):
        """`status` , `afk` , `avatar` , `banner` , `iconoservidor` , `miembros` , `encuesta` , `hack` , `token` , `users` , `wizz` , `urban` , `rickroll` , `hash` , `snipe` , `users` , `lista boosters` , `lista enrol` , `lista emojis` , `lista bots` , `lista admins` , `lista envoz` , `lista moderadores` , `lista earlysupporter` , `lista desarrolladoractivo` , `lista createpos` , `lista roles` , `calculator`"""