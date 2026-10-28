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
import discord
from utils.emoji import CROSS, TICK, ZWARNING
from discord.ui import LayoutView, TextDisplay, Separator, Container
from discord.ext import commands
from core import *
from utils.Tools import *
from typing import Optional
import aiosqlite

color = 0xFF0000


class SuccessView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{TICK} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class ErrorView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{CROSS} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class WarningView(LayoutView):
    def __init__(self, title, description):
        super().__init__(timeout=None)
        self.add_item(
            Container(
                TextDisplay(f"**{ZWARNING} {title}**"),
                Separator(visible=True),
                TextDisplay(description),
            )
        )


class ListView(LayoutView):
    def __init__(self, title, items, empty_message, guild=None):
        super().__init__(timeout=None)

        if not items:
            self.add_item(
                Container(
                    TextDisplay(f"**{title}**"),
                    Separator(visible=True),
                    TextDisplay(empty_message),
                )
            )
        else:
            if guild:
                mentions = []
                for item in items:
                    if isinstance(item, int):
                        entity = guild.get_channel(item) or guild.get_member(item)
                        mentions.append(entity.mention if entity else f"ID {item}")
                    else:
                        mentions.append(f"`{item}`")
                description = "\n".join(mentions)
            else:
                description = "\n".join([f"`{item}`" for item in items])

            self.add_item(
                Container(
                    TextDisplay(f"**{title}**"),
                    Separator(visible=True),
                    TextDisplay(description),
                )
            )


class Ignore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/ignore.db"
        self.color = 0xFF0000
        bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_commands (guild_id INTEGER, command_name TEXT)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_channels (guild_id INTEGER, channel_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS ignored_users (guild_id INTEGER, user_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS bypassed_users (guild_id INTEGER, user_id INTEGER)"
            )
            await db.commit()

    @commands.group(
        name="ignore",
        help="Gestiona comandos, canales y usuarios ignorados, además de los usuarios con omisión.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _ignore(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_ignore.group(
        name="command",
        help="Gestiona los comandos ignorados en este servidor.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _command(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_command.command(name="add", help="Añade un comando a la lista de ignorados.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def command_add(self, ctx: commands.Context, command_name: str):
        command_name_normalized = command_name.strip().lower()
        command = self.bot.get_command(command_name_normalized)
        if not command:
            await ctx.reply(
                view=ErrorView("Error", f"`{command_name}` no es un comando válido.")
            )
            return

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_commands WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()
            if count[0] >= 25:
                await ctx.reply(
                    view=WarningView(
                        "Acceso denegado",
                        "Solo puedes añadir hasta 25 comandos a la lista de ignorados.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                (ctx.guild.id, command_name_normalized),
            )
            result = await cursor.fetchone()
            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"`{command_name}` ya está en la lista de comandos ignorados.",
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_commands (guild_id, command_name) VALUES (?, ?)",
                    (ctx.guild.id, command_name_normalized),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se añadió `{command_name}` a la lista de comandos ignorados.",
                    )
                )

    @_command.command(name="remove", help="Quita un comando de la lista de ignorados.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def command_remove(self, ctx: commands.Context, command_name: str):
        command_name_normalized = command_name.strip().lower()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                (ctx.guild.id, command_name_normalized),
            )
            result = await cursor.fetchone()
            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"`{command_name}` no está en la lista de comandos ignorados."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_commands WHERE guild_id = ? AND command_name = ?",
                    (ctx.guild.id, command_name_normalized),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se quitó `{command_name}` de la lista de comandos ignorados.",
                    )
                )

    @_command.command(name="show", help="Muestra la lista de comandos ignorados.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def command_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT command_name FROM ignored_commands WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            commands = await cursor.fetchall()
            if not commands:
                await ctx.reply(
                    view=ListView(
                        "Comandos ignorados",
                        [],
                        "No hay comandos ignorados actualmente en este servidor.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView("Comandos ignorados", [c[0] for c in commands], "")
                )

    @_ignore.group(
        name="channel",
        help="Gestiona los canales ignorados en este servidor.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_channel.command(name="add", help="Añade un canal a la lista de ignorados.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def channel_add(self, ctx: commands.Context, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_channels WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Acceso denegado",
                        "Solo puedes añadir hasta 30 canales a la lista de ignorados.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, channel.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"{channel.mention} ya está en la lista de canales ignorados.",
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_channels (guild_id, channel_id) VALUES (?, ?)",
                    (ctx.guild.id, channel.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se añadió {channel.mention} a la lista de canales ignorados.",
                    )
                )

    @_channel.command(name="remove", help="Quita un canal de la lista de ignorados.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def channel_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, channel.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error",
                        f"{channel.mention} no está en la lista de canales ignorados.",
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_channels WHERE guild_id = ? AND channel_id = ?",
                    (ctx.guild.id, channel.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se quitó {channel.mention} de la lista de canales ignorados.",
                    )
                )

    @_channel.command(name="show", help="Muestra la lista de canales ignorados.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def channel_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT channel_id FROM ignored_channels WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            channels = await cursor.fetchall()

            if not channels:
                await ctx.reply(
                    view=ListView(
                        "Canales ignorados",
                        [],
                        "No hay canales ignorados actualmente en este servidor.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView(
                        "Canales ignorados", [c[0] for c in channels], "", ctx.guild
                    )
                )

    @_ignore.group(
        name="user",
        help="Gestiona los usuarios ignorados en este servidor.",
        invoke_without_command=True,
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _user(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_user.command(name="add", help="Añade un usuario a la lista de ignorados.")
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def user_add(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM ignored_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Acceso denegado",
                        "Solo puedes añadir hasta 30 usuarios a la lista de ignorados.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} ya está en la lista de usuarios ignorados."
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO ignored_users (guild_id, user_id) VALUES (?, ?)",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se añadió {user.mention} a la lista de usuarios ignorados.",
                    )
                )

    @_user.command(name="remove", help="Quita un usuario de la lista de ignorados.")
    @blacklist_check()
    @commands.has_permissions(administrator=True)
    async def user_remove(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} no está en la lista de usuarios ignorados."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM ignored_users WHERE guild_id = ? AND user_id = ?",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.send(
                    view=SuccessView(
                        "Éxito",
                        f"Se quitó {user.mention} de la lista de usuarios ignorados.",
                    )
                )

    @_user.command(name="show", help="Muestra la lista de usuarios ignorados.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def user_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM ignored_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            users = await cursor.fetchall()

            if not users:
                await ctx.reply(
                    view=ListView(
                        "Usuarios ignorados",
                        [],
                        "No hay usuarios ignorados actualmente en este servidor.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView("Usuarios ignorados", [u[0] for u in users], "", ctx.guild)
                )

    @_ignore.group(
        name="bypass",
        help="Gestiona los usuarios con omisión en este servidor.",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _bypass(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_bypass.command(name="add", help="Añade un usuario a la lista de omisión.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_add(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM bypassed_users WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            count = await cursor.fetchone()

            if count[0] >= 30:
                await ctx.reply(
                    view=WarningView(
                        "Acceso denegado",
                        "Solo puedes añadir hasta 30 usuarios a la lista de omisión.",
                    )
                )
                return

            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} ya está en la lista de usuarios con omisión."
                    )
                )
            else:
                await db.execute(
                    "INSERT INTO bypassed_users (guild_id, user_id) VALUES (?, ?)",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se añadió {user.mention} a la lista de usuarios con omisión.",
                    )
                )

    @_bypass.command(name="remove", help="Quita un usuario de la lista de omisión.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_remove(self, ctx: commands.Context, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, user.id),
            )
            result = await cursor.fetchone()

            if not result:
                await ctx.reply(
                    view=ErrorView(
                        "Error", f"{user.mention} no está en la lista de usuarios con omisión."
                    )
                )
            else:
                await db.execute(
                    "DELETE FROM bypassed_users WHERE guild_id = ? AND user_id = ?",
                    (ctx.guild.id, user.id),
                )
                await db.commit()
                await ctx.reply(
                    view=SuccessView(
                        "Éxito",
                        f"Se quitó {user.mention} de la lista de usuarios con omisión.",
                    )
                )

    @_bypass.command(
        name="show", aliases=["list"], help="Muestra la lista de usuarios con omisión."
    )
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def bypass_show(self, ctx: commands.Context):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM bypassed_users WHERE guild_id = ?", (ctx.guild.id,)
            )
            users = await cursor.fetchall()

            if not users:
                await ctx.reply(
                    view=ListView(
                        "Usuarios con omisión",
                        [],
                        "No hay usuarios con omisión actualmente en este servidor.",
                    )
                )
            else:
                await ctx.reply(
                    view=ListView(
                        "Usuarios con omisión", [u[0] for u in users], "", ctx.guild
                    )
                )
