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
from utils.emoji import ZSAFE
from discord.ext import commands


class _antinuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Antinuke commands"""
  
    def help_custom(self):
		      emoji = ZSAFE
		      label = "Comandos de seguridad"
		      description = "Te muestra los comandos de antinuke"
		      return emoji, label, description

    @commands.group()
    async def __Antinuke__(self, ctx: commands.Context):
        """`antinuke` , `antinuke enable` , `antinuke disable` , `listablanca` , `listablanca @user` , `quitarlistablanca` , `verlistablanca` , `restablecerlistablanca` , `propietariosextra` , `propietariosextra set` , `propietariosextra view` , `propietariosextra reset`, `modonoche` , `modonoche activar` , `modonoche desactivar`\n"""

