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
from utils.emoji import ZWRENCH
from discord.ext import commands


class _extra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Utility commands"""
  
    def help_custom(self):
		      emoji = ZWRENCH
		      label = "Comandos de utilidad"
		      description = "Te muestra los comandos de utilidad"
		      return emoji, label, description

    @commands.group()
    async def __Utility__(self, ctx: commands.Context):
        """`botinfo` , `estadisticas` , `invite` , `infoservidor` , `infousuario` , `inforol` , `boostcount` , `desbaneartodo` ,  `joined-at` , `ping` , `github` , `infovoz` , `infocanal` , `badges` , `banner usuario` , `banner servidor` , `reminder start` , `reminder clear` , `permissions` , `temporizador`\n\n__**Media Commands**__\n`media` , `media configurar ` , `media eliminar` , `media configuracion` , `media exentos` , `media exentos agregar` , `media exentos quitar` , `media exentos ver`"""