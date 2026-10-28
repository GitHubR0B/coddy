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
from discord.ext import commands
import os
from core import Cog, zyrox, Context
import games as games
from utils.Tools import *
from utils.cv2 import CV2
from games import button_games as btn
import random
import asyncio



class Games(Cog):
    """Juegos de Zyrox"""

    def __init__(self, client: zyrox):
        self.client = client


    @commands.hybrid_command(name="chess",
                             help="Juega al ajedrez con un usuario.",
                             usage="Chess <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _chess(self, ctx: Context, player: discord.Member):
        if player == ctx.author:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar contra ti mismo!"))
        elif player.bot:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar con bots!"))
        else:
            game = btn.BetaChess(white=ctx.author, black=player)
            await game.start(ctx)


    @commands.hybrid_command(name="rps",
                             help="Juega piedra, papel o tijera con el bot o un usuario.",
                             aliases=["rockpaperscissors"],
                             usage="Rockpaperscissors")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _rps(self, ctx: Context, player: discord.Member = None):
        game = btn.BetaRockPaperScissors(player)
        await game.start(ctx, timeout=120)

    @commands.hybrid_command(name="tic-tac-toe",
                             help="Juega al tres en raya con un usuario.",
                             aliases=["ttt", "tictactoe"],
                             usage="Ticktactoe <member>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.user, wait=False)
    @commands.guild_only()
    async def _ttt(self, ctx: Context, player: discord.Member):
        if player == ctx.author:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar contra ti mismo!"))
        elif player.bot:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar con bots!"))
        else:
            game = btn.BetaTictactoe(cross=ctx.author, circle=player)
            await game.start(ctx, timeout=30)

    @commands.hybrid_command(name="wordle",
                             help="Juego de Wordle | Juega contra el bot.",
                             usage="Wordle")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _wordle(self, ctx: Context):
        game = games.Wordle()
        await game.start(ctx, timeout=120)

    @commands.hybrid_command(name="2048",
                             help="Juega al 2048 con el bot.",
                             aliases=["twenty48"],
                             usage="2048")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _2048(self, ctx: Context):
        game = btn.BetaTwenty48()
        await game.start(ctx, win_at=2048)

    @commands.hybrid_command(name="memory-game",
                             help="¿Qué tan buena es tu memoria?",
                             aliases=["memory"],
                             usage="memory-game")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _memory(self, ctx: Context):
        game = btn.MemoryGame()
        await game.start(ctx)

    @commands.hybrid_command(name="number-slider",
                             help="Desliza los números con el bot",
                             aliases=["slider"],
                             usage="slider")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _number_slider(self, ctx: Context):
        game = btn.NumberSlider()
        await game.start(ctx)

    @commands.hybrid_command(name="battleship",
                             help="Juega a hundir la flota con tu amigo.",
                             aliases=["battle-ship"],
                             usage="battleship <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _battle(self, ctx: Context, player: discord.Member):
        game = btn.BetaBattleShip(player1=ctx.author, player2=player)
        await game.start(ctx)

    @commands.group(name="country-guesser",
                    help="Adivina el nombre del país por su bandera.",
                    aliases=["guess", "guesser", "countryguesser"],
                    usage="country-guesser")
    @commands.guild_only()
    async def _country_guesser(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("country-guesser")

    @_country_guesser.command(name="start",
                              help="Inicia el juego de adivinar países. Es un juego de 100 segundos, así que se recomienda jugarlo en un CANAL ESPECÍFICO.")
    async def _start_country_guesser(self, ctx: Context):
        game = games.CountryGuesser(is_flags=True, hints=2)
        await game.start(ctx)

    """@_country_guesser.command(name="end",
                              help="Termina el juego de adivinar países.")
    async def _end_country_guesser(self, ctx: Context):
        await self.country_guesser_game.end_game_manually(ctx)"""

    @commands.hybrid_command(name="connectfour",
                             help="Juega al conecta 4 con un usuario.",
                             aliases=["c4", "connect-four", "connect4"],
                             usage="connectfour <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.guild_only()
    async def _connectfour(self, ctx: Context, player: discord.Member):
        if player == ctx.author:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar contra ti mismo!"))
        elif player.bot:
            await ctx.send(view=CV2("❌ Error", "¡No puedes jugar con bots!"))
        else:
            game = games.ConnectFour(red=ctx.author, blue=player)  
            await game.start(ctx, timeout=300)



    @commands.hybrid_command(name="lights-out",
                             help="Juega al juego de luces con el bot.",
                             aliases=["lightsout"],
                             usage="Lights-out")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _lights_show(self, ctx: Context):
        game = btn.LightsOut()
        await game.start(ctx)
