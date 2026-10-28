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
from utils.emoji import ZAI
from discord .ext import commands 

class _ai (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 

    """AI commands"""

    def help_custom (self ):
        emoji =ZAI
        label ="Comandos de IA"
        description ="Te muestra los comandos de IA"
        return emoji ,label ,description 

    @commands .group ()
    async def __AI__ (self ,ctx :commands .Context ):
        """`ai activate`, `ai deactivate`, `ai analyze`, `ai analyse`, `ai code`, `ai explain`, `ai conversation-clear`, `ai mood-analyzer`, `ai personality`, `ai conversation-stats`, `ai summarize`, `ai ask`, `ai fact`, `ai database-clear`, `ai roleplay-enable`, `ai roleplay-disable`"""
        pass 
