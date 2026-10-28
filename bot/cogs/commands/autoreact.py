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
from utils.emoji import CROSS, ICONS_WARNING, TICK
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, Container
import aiosqlite
import re
from utils.Tools import *
from utils.cv2 import CV2, build_container





class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'db/autoreact.db'
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS autoreact (
                    guild_id INTEGER,
                    trigger TEXT,
                    emojis TEXT
                )
            """)
            await db.commit()

    async def get_triggers(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT trigger, emojis FROM autoreact WHERE guild_id = ?", (guild_id,))
            return await cursor.fetchall()

    async def trigger_exists(self, guild_id, trigger):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT 1 FROM autoreact WHERE guild_id = ? AND trigger = ?", (guild_id, trigger))
            return await cursor.fetchone()

    @commands.group(name="react", aliases=["autoreact"], help="Muestra todos los subcomandos del grupo autoreact.", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @react.command(name="add", aliases=["set", "create"], help="Añade un disparador y sus emojis al autoreact.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, trigger: str, *, emojis: str):
        if len(trigger.split()) > 1:
            view = CV2(f"{CROSS} Disparador no válido", "Los disparadores solo pueden ser una palabra.")
            return await ctx.reply(view=view)

        
        emoji_list = re.findall(r"<a?:\w+:\d+>|[\u263a-\U0001f645]", emojis)
        if len(emoji_list) > 10:
            view = CV2(f"{CROSS} Demasiados emojis", "Solo puedes configurar hasta **10** emojis por disparador.")
            return await ctx.reply(view=view)

        triggers = await self.get_triggers(ctx.guild.id)
        if len(triggers) >= 10:
            view = CV2(f"{ICONS_WARNING} Límite de disparadores alcanzado", "Solo puedes configurar hasta 10 disparadores de autorreacción en este servidor.")
            return await ctx.reply(view=view)

        if await self.trigger_exists(ctx.guild.id, trigger):
            view = CV2(f"{ICONS_WARNING} El disparador ya existe", f"El disparador '{trigger}' ya existe. Elimínalo antes de volver a añadirlo.")
            return await ctx.reply(view=view)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO autoreact (guild_id, trigger, emojis) VALUES (?, ?, ?)", 
                             (ctx.guild.id, trigger, " ".join(emoji_list)))
            await db.commit()

        view = CV2(f"{TICK} Disparador añadido", f"Disparador '{trigger}' añadido correctamente con los emojis {', '.join(emoji_list)}.")
        await ctx.reply(view=view)

    @react.command(name="remove", aliases=["clear", "delete"], help="Quita un disparador y sus emojis del autoreact.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, trigger: str):
        if not await self.trigger_exists(ctx.guild.id, trigger):
            view = CV2(f"{CROSS} Disparador no encontrado", f"El disparador '{trigger}' no existe.")
            return await ctx.reply(view=view)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM autoreact WHERE guild_id = ? AND trigger = ?", (ctx.guild.id, trigger))
            await db.commit()

        view = CV2(f"{TICK} Disparador eliminado", f"Disparador '{trigger}' eliminado correctamente.")
        await ctx.reply(view=view)

    @react.command(name="list", aliases=["show", "config"], help="Muestra todos los disparadores y sus emojis del módulo autoreact.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        triggers = await self.get_triggers(ctx.guild.id)
        if not triggers:
            view = CV2("No hay disparadores configurados", "No hay disparadores de autorreacción configurados en este servidor.")
            return await ctx.reply(view=view)

        trigger_list = "\n".join([f"**{t[0]}:** {t[1]}" for t in triggers])
        view = CV2("Disparadores de autorreacción", trigger_list)
        await ctx.reply(view=view)

    @react.command(name="reset", help="Restablece todos los disparadores y sus emojis del módulo autoreact.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx):
        triggers = await self.get_triggers(ctx.guild.id)
        if not triggers:
            view = CV2(f"{CROSS} No hay disparadores configurados", "No hay disparadores de autorreacción configurados para restablecer.")
            return await ctx.reply(view=view)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM autoreact WHERE guild_id = ?", (ctx.guild.id,))
            await db.commit()

        view = CV2(f"{TICK} Todos los disparadores restablecidos", "Se eliminaron todos los disparadores de autorreacción correctamente.")
        await ctx.reply(view=view)

async def setup(bot):
    await bot.add_cog(AutoReaction(bot))
