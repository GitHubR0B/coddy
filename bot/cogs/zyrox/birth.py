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
from utils.emoji import ZCIRCLE
from discord .ext import commands 


class _birth(commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 

    """Birthday commands"""

    def help_custom (self ):
              emoji =ZCIRCLE
              label ="Comandos de cumpleaños"
              description ="Te muestra los comandos de cumpleaños"
              return emoji ,label ,description 

    @commands.group ()
    async def __Birthday__ (self ,ctx :commands .Context ):
        """`birthdaysetup` , `setbirthday` , `removebirthday` , `listbirthdays` , `birthday`"""
        pass
