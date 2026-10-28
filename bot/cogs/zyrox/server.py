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
from utils.emoji import WIFI
from discord.ext import commands

class _server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Server commands"""
  
    def help_custom(self):
		      emoji = WIFI
		      label = "Comandos de servidor"
		      description = "Te muestra los comandos de servidor"
		      return emoji, label, description

    @commands.group()
    async def __Setup__(self, ctx: commands.Context):
        """`rolespersonalizados` , `rolespersonalizados crear <name>` , `rolespersonalizados eliminar <name>`  , `rolespersonalizados lista` , `rolespersonalizados staff` , `rolespersonalizados girl` , `rolespersonalizados friend` , `rolespersonalizados vip` , `rolespersonalizados guest` , `rolespersonalizados configuracion` , `rolespersonalizados restablecer` , `staff` , `girl` , `friend` , `vip` , `guest`\n\n__**Auto Role**__\n`autorole bots add` , `autorole bots remove` , `autorole bots` , `autorole config` , `autorole humans add` , `autorole humans remove` , `autorole humans` , `autorole reset all` , `autorole reset bots` , `autorole reset humans` , `autorole`\n\n__**Autoresponder**__\n`autoresponder` , `autoresponder create` , `autoresponder delete` , `autoresponder edit` , `autoresponder config`\n\n__**Auto React Commands**__\n`react` , `react add` , `react remove` , `react list` , `react reset`"""

