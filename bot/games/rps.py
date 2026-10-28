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

from __future__ import annotations

import asyncio
import random
from typing import ClassVar, Optional

import discord
from discord.ext import commands

from .utils import DiscordColor, DEFAULT_COLOR


class RockPaperScissors:
    message: discord.Message

    OPTIONS: ClassVar[tuple[str, str, str]] = ("\U0001faa8", "\U00002702", "\U0001f4f0")
    BEATS: ClassVar[dict[str, str]] = {
        OPTIONS[0]: OPTIONS[1],
        OPTIONS[1]: OPTIONS[2],
        OPTIONS[2]: OPTIONS[0],
    }

    def check_win(self, bot_choice: str, user_choice: str) -> bool:
        return self.BEATS[user_choice] == bot_choice

    async def wait_for_choice(
        self, ctx: commands.Context[commands.Bot], *, timeout: float
    ) -> str:
        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                str(reaction.emoji) in self.OPTIONS
                and user == ctx.author
                and reaction.message == self.message
            )

        reaction, _ = await ctx.bot.wait_for(
            "reaction_add", timeout=timeout, check=check
        )
        return str(reaction.emoji)

    async def start(
        self,
        ctx: commands.Context[commands.Bot],
        *,
        timeout: Optional[float] = None,
        embed_color: DiscordColor = DEFAULT_COLOR,
    ) -> discord.Message:
        """
        Starts the Rock Paper Scissors game.

        Parameters
        ----------
        ctx : commands.Context
            The context of the invoking command.
        timeout : Optional[float], optional
            The timeout for waiting, by default None.
        embed_color : DiscordColor, optional
            The color of the game embed, by default DEFAULT_COLOR.

        Returns
        -------
        discord.Message
            Returns the game message.
        """
        embed = discord.Embed(
            title="Piedra, papel o tijera",
            description="¡Reacciona para jugar!",
            color=discord.Color.random(),
        )
        self.message = await ctx.send(embed=embed)

        for option in self.OPTIONS:
            await self.message.add_reaction(option)

        bot_choice = random.choice(self.OPTIONS)

        try:
            user_choice = await self.wait_for_choice(ctx, timeout=timeout)
        except asyncio.TimeoutError:
            embed.description = "¡Tardaste demasiado en responder!"
            await self.message.edit(embed=embed)
            return self.message

        if user_choice == bot_choice:
            embed.description = f"**¡Empate!**\nAmbos elegimos {user_choice}"
        elif self.check_win(bot_choice, user_choice):
            embed.description = (
                f"**¡Ganaste!**\nElegiste {user_choice} y yo elegí {bot_choice}."
            )
        else:
            embed.description = f"**¡Perdiste!**\nElegí {bot_choice} y tú elegiste {user_choice}."

        await self.message.edit(embed=embed)
        return self.message
