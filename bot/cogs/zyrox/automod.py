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
from utils.emoji import ZBOT
from discord.ext import commands

class _automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Automod commands"""
  
    def help_custom(self):
		      emoji = ZBOT
		      label = "Comandos de automod"
		      description = "Te muestra los comandos de automod"
		      return emoji, label, description

    @commands.group()
    async def __Automod__(self, ctx: commands.Context):
        """`automod` , `automod activar` , `automod desactivar` , `automod castigo` , `automod configuracion` , `automod registros` `automod ignorar` , `automod ignorar canal` , `automod ignorar rol` , `automod ignorar ver` , `automod ignorar restablecer` , `automod permitir` , `automod permitir canal` , `automod permitir rol`\n\n__**Blacklistword Commands**__\n`blacklistword` , `blacklistword add <word>` , `blacklistword remove <word>` , `blacklistword reset` , `blacklistword config` , `blacklistword bypass add <user/role>` , `blacklistword bypass remove <user/role>` , `blacklistword bypass show`
"""