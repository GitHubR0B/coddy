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
from utils.emoji import CROSS, TICK
from discord.ext import commands
import aiosqlite
import asyncio
from utils.config import *

class TopCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/topcheck.db"
        self.bot.loop.create_task(self.setup())

    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS topcheck (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER
                )
            """)
            await db.commit()

    async def is_topcheck_enabled(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT enabled FROM topcheck WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0] == 1
                return False

    async def enable_topcheck(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR REPLACE INTO topcheck (guild_id, enabled) VALUES (?, 1)", (guild_id,))
            await db.commit()

    async def disable_topcheck(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE topcheck SET enabled = 0 WHERE guild_id = ?", (guild_id,))
            await db.commit()

    @commands.group(
        name="topcheck",
        help="Gestiona la configuración de topcheck para el servidor.",
        invoke_without_command=True)
    @commands.guild_only()
    async def topcheck(self, ctx):
        embed = discord.Embed(title="Sistema Top Check",
                              description=(
        "Este sistema garantiza que el rol del bot esté por encima del rol más alto del usuario antes de ejecutar ciertos comandos.\n\n"
        f"Cuando topcheck está activado, solo los usuarios con roles por encima del rol del bot ({BRAND_NAME}) pueden realizar ciertas acciones de moderación. "
        "Si topcheck está desactivado, cualquier usuario con los permisos necesarios para un comando puede ejecutarlo.\n\n"
        "**Acciones de moderación afectadas por topcheck:**\n"
        "- BANEAR\n"
        "- EXPULSAR\n"
        "- ELIMINAR ROL\n"
        "- CREAR ROL\n"
        "- ACTUALIZAR MIEMBRO\n\n"
        "__**Subcomandos:**__\n"
        f"• `{ctx.prefix}topcheck enable` - Activa top check para el servidor.\n"
        f"• `{ctx.prefix}topcheck disable` - Desactiva top check para el servidor."
    ),
                              color=0xFF0000)
        embed.set_footer(text=f"Solicitado por {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @topcheck.command(
        name="enable",
        help="Activa topcheck para el servidor")
    @commands.guild_only()
    async def topcheck_enable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.reply(f"{CROSS} Solo el **dueño del servidor** puede activar topcheck.")
        if await self.is_topcheck_enabled(ctx.guild.id):
            return await ctx.reply(f"{CROSS} Topcheck ya está activado en este servidor.")
        await self.enable_topcheck(ctx.guild.id)
        await ctx.reply(f"{TICK} Topcheck se activó correctamente en este servidor.")

    @topcheck.command(
        name="disable",
        help="Desactiva topcheck para el servidor")
    @commands.guild_only()
    async def topcheck_disable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            return await ctx.reply("Solo el **dueño del servidor** puede desactivar topcheck.")
        if not await self.is_topcheck_enabled(ctx.guild.id):
            return await ctx.reply(f"{CROSS} Topcheck no está activado en este servidor.")
        await self.disable_topcheck(ctx.guild.id)
        await ctx.reply(f"{TICK} Topcheck se desactivó correctamente en este servidor.")

 