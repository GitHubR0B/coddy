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
from utils.emoji import ARROWRED, CROSS, NEXT_ALT1, REDRULESBOOK, RED_BUTTON, RED_PIN, STAR, TICK, ZBACK, ZPAUSE, ZPLAY, ZWARNING
from discord.ext import commands
import json
import os
import asyncio
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container



# Emoji Variables
CROSS = CROSS
TICK = TICK
WARNING = ZWARNING
WARNING = ZWARNING
BOOK = REDRULESBOOK
PLAY = ZPLAY
PAUSE = ZPAUSE
STOP = RED_BUTTON
NEXT = NEXT_ALT1
BACK = ZBACK
ARROW = ARROWRED
PIN = RED_PIN
STAR = STAR

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "db/counting.json"
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({}, f)
        with open(self.data_file, 'r') as f:
            self.counting_data = json.load(f)

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.counting_data, f, indent=4)

    def is_enabled(self, guild_id):
        guild_id = str(guild_id)
        return self.counting_data.get(guild_id, {}).get("enabled", False)

    async def not_enabled_embed(self, ctx):
        await ctx.send(view=CV2(
            f"{BOOK} Configuración de conteo de {ctx.guild.name}",
            f"**Estado actual:** {CROSS} Desactivado",
            "**Cómo activar:** Usa `counting enable` para activar el conteo."
        ))

    async def send_help_embed(self, ctx):
        await ctx.send(view=CV2(
            f"{BOOK} Comandos de conteo",
            "Administra y controla la configuración del juego de conteo.\n\n"
            "**counting enable/disable** — Activa o desactiva el conteo en el servidor\n"
            "**counting channel #channel** — Establece el canal de conteo\n"
            "**counting config reset/continue** — Define el modo de reinicio al equivocarse\n"
            "**counting reset** — Reinicia el conteo a 0\n"
            "**counting stats** — Consulta las estadísticas actuales del conteo"
        ))

    @commands.group(name="counting", invoke_without_command=True)
    async def counting(self, ctx):
        if not self.is_enabled(ctx.guild.id):
            await self.not_enabled_embed(ctx)
        else:
            await self.send_help_embed(ctx)

    @counting.command(name="enable")
    @commands.has_permissions(manage_channels=True)
    async def enable(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.counting_data:
            self.counting_data[guild_id] = {"enabled": True, "channel": None, "count": 0, "reset_on_fail": False}
        else:
            self.counting_data[guild_id]["enabled"] = True
        self.save_data()
        await ctx.send(view=CV2("Conteo", f"{TICK} ¡El conteo ha sido activado!"))

    @counting.command(name="disable")
    @commands.has_permissions(manage_channels=True)
    async def disable(self, ctx):
        guild_id = str(ctx.guild.id)
        if guild_id not in self.counting_data:
            await self.not_enabled_embed(ctx)
            return
        self.counting_data[guild_id]["enabled"] = False
        self.save_data()
        await ctx.send(view=CV2("Conteo", f"{STOP} ¡El conteo ha sido desactivado!"))

    @counting.command(name="channel")
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        if not self.is_enabled(guild_id):
            await self.not_enabled_embed(ctx)
            return
        self.counting_data[guild_id]["channel"] = channel.id
        self.save_data()
        await ctx.send(view=CV2("Conteo", f"{PIN} Canal de conteo establecido en {channel.mention}"))

    @counting.command(name="config")
    @commands.has_permissions(manage_channels=True)
    async def config(self, ctx, mode: str):
        guild_id = str(ctx.guild.id)
        if not self.is_enabled(guild_id):
            await self.not_enabled_embed(ctx)
            return
        if mode.lower() in ["reset", "true", "on"]:
            self.counting_data[guild_id]["reset_on_fail"] = True
            msg = f"{TICK} El conteo ahora se reiniciará al cometer errores."
        elif mode.lower() in ["continue", "false", "off"]:
            self.counting_data[guild_id]["reset_on_fail"] = False
            msg = f"{TICK} El conteo ahora continuará al cometer errores."
        else:
            await ctx.send(f"{CROSS} ¡Modo inválido! Usa `reset` o `continue`.")
            return
        self.save_data()
        await ctx.send(view=CV2("Conteo", msg))

    @counting.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def reset(self, ctx):
        guild_id = str(ctx.guild.id)
        if not self.is_enabled(guild_id):
            await self.not_enabled_embed(ctx)
            return
        self.counting_data[guild_id]["count"] = 0
        self.save_data()
        await ctx.send(view=CV2("Conteo", f"{NEXT} ¡El conteo se ha reiniciado a 0!"))

    @counting.command(name="stats")
    async def stats(self, ctx):
        guild_id = str(ctx.guild.id)
        if not self.is_enabled(guild_id):
            await self.not_enabled_embed(ctx)
            return
        data = self.counting_data[guild_id]
        channel = ctx.guild.get_channel(data["channel"]) if data["channel"] else None
        channel_str = channel.mention if channel else "No establecido"
        reset_str = f"{TICK} Sí" if data["reset_on_fail"] else f"{CROSS} No"
        await ctx.send(view=CV2(
            f"{BOOK} Estadísticas de conteo",
            f"**Conteo actual:** {data['count']}\n"
            f"**Canal:** {channel_str}\n"
            f"**Reiniciar al equivocarse:** {reset_str}"
        ))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        if guild_id not in self.counting_data:
            return

        data = self.counting_data[guild_id]
        if not data.get("enabled", False):
            return

        if message.channel.id != data.get("channel"):
            return

        content = message.content.strip()

        if not content.isdigit():
            msg = await message.channel.send(f"{WARNING} ¡No se permiten letras!")
            await asyncio.sleep(3)
            await msg.delete()
            await message.delete()
            return

        number = int(content)
        expected_number = data.get("count", 0) + 1

        if number != expected_number:
            msg = await message.channel.send(f"{CROSS} ¡Número incorrecto! El número esperado es **{expected_number}**")
            await asyncio.sleep(3)
            await msg.delete()
            await message.delete()
            if data.get("reset_on_fail", False):
                self.counting_data[guild_id]["count"] = 0
                self.save_data()
            return

        # Correct number
        self.counting_data[guild_id]["count"] = number
        self.save_data()
        await message.add_reaction(TICK)

def setup(bot):
    bot.add_cog(Counting(bot))