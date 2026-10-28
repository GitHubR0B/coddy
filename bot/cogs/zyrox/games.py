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
from utils.emoji import GAMES
from discord.ext import commands


class _games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""

    def help_custom(self):
        emoji = GAMES
        label = "Comandos de juegos"
        description = "Te muestra los comandos de juegos"
        return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`blackjack` , `ajedrez` , `tresenraya` , `country-guesser` , `ppt` , `luces` , `wordle` , `2048` , `memoria` , `deslizador` , `hundirflota` , `conecta4` , `slots`, `counting`"""
