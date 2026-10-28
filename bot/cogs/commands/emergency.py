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
from utils.emoji import CROSS, CROSS_ALT, ML_CROSS, TICK, TICK_ALT, ZWARNING
from discord.ui import LayoutView, TextDisplay, Separator, Container, Button, ActionRow
from discord.ext import commands
import aiosqlite
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import OWNER_IDS_STR


class EmergencyRestoreConfirmView(LayoutView):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.value = None

        self.yes_btn = Button(label="Sí", style=discord.ButtonStyle.green)
        self.no_btn = Button(label="No", style=discord.ButtonStyle.danger)

        self.yes_btn.callback = self.confirm_callback
        self.no_btn.callback = self.cancel_callback

        self.add_item(
            build_container(
                TextDisplay("**Confirmar restauración**"),
                Separator(visible=True),
                TextDisplay(
                    "Esto restaurará los permisos desactivados previamente en los roles de emergencia. ¿Quieres continuar?"
                ),
                ActionRow(self.yes_btn, self.no_btn),
            )
        )

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message(
                "Solo el propietario del servidor puede usar este botón.", ephemeral=True
            )
        self.value = True
        await interaction.response.defer()
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message(
                "Solo el propietario del servidor puede usar este botón.", ephemeral=True
            )
        self.value = False
        await interaction.response.defer()
        self.stop()


class EmergencyMainView(LayoutView):
    def __init__(self, ctx, prefix):
        super().__init__(timeout=None)
        self.prefix = prefix
        self.add_item(
            build_container(
                TextDisplay("__Situación de emergencia__"),
                Separator(visible=True),
                TextDisplay(
                    f"El grupo de comandos `emergency` está diseñado para proteger tu servidor frente a actividades maliciosas o daños accidentales.\n\n"
                    f"**El grupo de comandos tiene varios subcomandos:**\n\n"
                    f"`{prefix}emergency enable` - Activa el modo de emergencia\n"
                    f"`{prefix}emergency disable` - Desactiva el modo de emergencia\n"
                    f"`{prefix}emergency authorise` - Gestiona los usuarios autorizados\n"
                    f"`{prefix}emergency role` - Gestiona los roles de la lista de emergencia\n"
                    f"`{prefix}emergency-situation` - Ejecuta la situación de emergencia"
                ),
            )
        )


class EnableSuccessView(LayoutView):
    def __init__(self, roles_added):
        super().__init__(timeout=None)
        content = (
            "\n".join([f"{r.mention}" for r in roles_added])
            if roles_added
            else "No se encontraron nuevos roles con permisos peligrosos."
        )
        self.add_item(
            build_container(
                TextDisplay(f"**{TICK} Éxito**"),
                Separator(visible=True),
                TextDisplay(content),
            )
        )


class EnableErrorView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{CROSS} Error**"),
                Separator(visible=True),
                TextDisplay("Solo el propietario del servidor puede activar el modo de emergencia."),
            )
        )


class DisableSuccessView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{TICK_ALT} Éxito**"),
                Separator(visible=True),
                TextDisplay(
                    "El modo de emergencia se ha desactivado y se han borrado todos los roles de emergencia."
                ),
            )
        )


class DisableErrorView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{CROSS_ALT} Error**"),
                Separator(visible=True),
                TextDisplay("Solo el propietario del servidor puede desactivar el modo de emergencia."),
            )
        )


class AuthoriseSuccessView(LayoutView):
    def __init__(self, member_name, action):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{TICK_ALT} Éxito**"),
                Separator(visible=True),
                TextDisplay(f"**{member_name}** ha sido {action}."),
            )
        )


class AuthoriseErrorView(LayoutView):
    def __init__(self, error_type):
        super().__init__(timeout=None)
        content = {
            "owner_add": "Solo el propietario del servidor puede añadir usuarios autorizados.",
            "owner_remove": "Solo el propietario del servidor puede eliminar usuarios autorizados.",
            "owner_list": "Solo el propietario del servidor puede ver la lista.",
            "limit": "Solo se pueden añadir hasta 5 usuarios autorizados.",
            "exists": "Este usuario ya está autorizado.",
            "not_found": "Este usuario no está autorizado.",
        }.get(error_type, "Ocurrió un error.")
        is_warning = error_type == "limit"
        self.add_item(
            build_container(
                TextDisplay(
                    f"**{ZWARNING} Acceso denegado**"
                    if is_warning
                    else f"**{CROSS_ALT} Error**"
                ),
                Separator(visible=True),
                TextDisplay(content),
            )
        )


class AuthoriseListView(LayoutView):
    def __init__(self, ctx, users, is_owner):
        super().__init__(timeout=None)
        if not is_owner:
            self.add_item(
                build_container(
                    TextDisplay(f"**{ZWARNING} Acceso denegado**"),
                    Separator(visible=True),
                    TextDisplay("Solo el propietario del servidor puede ver la lista."),
                )
            )
        elif not users:
            self.add_item(
                build_container(
                    TextDisplay("**Usuarios autorizados**"),
                    Separator(visible=True),
                    TextDisplay("No se encontraron usuarios autorizados."),
                )
            )
        else:
            desc = "\n".join(
                [
                    f"{i + 1}. [{ctx.guild.get_member(u[0]).name}](https://discord.com/users/{u[0]}) - {u[0]}"
                    for i, u in enumerate(users)
                ]
            )
            self.add_item(
                build_container(
                    TextDisplay("**Usuarios autorizados**"),
                    Separator(visible=True),
                    TextDisplay(desc),
                )
            )


class RoleSuccessView(LayoutView):
    def __init__(self, role_name, action):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{TICK_ALT} Éxito**"),
                Separator(visible=True),
                TextDisplay(f"**{role_name}** ha sido {action} la lista de emergencia."),
            )
        )


class RoleErrorView(LayoutView):
    def __init__(self, error_type):
        super().__init__(timeout=None)
        content = {
            "owner_add": "Solo el propietario del servidor puede añadir roles para la situación de emergencia.",
            "owner_remove": "Solo el propietario del servidor puede eliminar roles de la lista de emergencia.",
            "owner_list": "No estás autorizado para ver la lista de roles.",
            "limit": "Solo se pueden añadir hasta 25 roles.",
            "exists": "Este rol ya está en la lista de emergencia.",
            "not_found": "Este rol no está en la lista de emergencia.",
        }.get(error_type, "Ocurrió un error.")
        is_warning = error_type == "limit"
        self.add_item(
            build_container(
                TextDisplay(
                    f"**{ZWARNING} Error**"
                    if is_warning
                    else f"**{CROSS_ALT} Error**"
                ),
                Separator(visible=True),
                TextDisplay(content),
            )
        )


class RoleListView(LayoutView):
    def __init__(self, roles, is_authorised):
        super().__init__(timeout=None)
        if not is_authorised:
            self.add_item(
                build_container(
                    TextDisplay(f"**{ZWARNING} Acceso denegado**"),
                    Separator(visible=True),
                    TextDisplay("No estás autorizado para ver la lista de roles."),
                )
            )
        elif not roles:
            self.add_item(
                build_container(
                    TextDisplay("**Roles de emergencia**"),
                    Separator(visible=True),
                    TextDisplay("No hay roles añadidos para la situación de emergencia."),
                )
            )
        else:
            desc = "\n".join(
                [f"{i + 1}. <@&{r[0]}> - {r[0]}" for i, r in enumerate(roles)]
            )
            self.add_item(
                build_container(
                    TextDisplay("**Roles de emergencia**"),
                    Separator(visible=True),
                    TextDisplay(desc),
                )
            )


class EmergencySituationErrorView(LayoutView):
    def __init__(self, error_type):
        super().__init__(timeout=None)
        content = (
            "No estás autorizado para ejecutar la situación de emergencia."
            if error_type == "access"
            else "No se han añadido roles para la situación de emergencia."
        )
        self.add_item(
            build_container(
                TextDisplay(
                    f"**{ZWARNING} Acceso denegado**"
                    if error_type == "access"
                    else f"**{CROSS_ALT} Error**"
                ),
                Separator(visible=True),
                TextDisplay(content),
            )
        )


class EmergencySituationResultView(LayoutView):
    def __init__(
        self,
        success_msg,
        error_msg,
        moved_role=None,
        move_failed=False,
        move_error=None,
    ):
        super().__init__(timeout=None)
        desc = f"**{TICK_ALT} Roles modificados**:\n{success_msg}\n\n"
        if moved_role:
            desc += f"**{ZWARNING} Rol movido**: {moved_role.mention} se movió debajo del rol más alto del bot.\n\n"
        elif move_failed:
            desc += "**ℹ️ No se pudo mover el rol**: Error de permisos.\n\n"
        elif move_error:
            desc += f"**ℹ️ No se pudo mover el rol**: {move_error}\n\n"
        desc += f"**Errores**: {error_msg}"
        self.add_item(
            build_container(
                TextDisplay("**Situación de emergencia**"),
                Separator(visible=True),
                TextDisplay(desc),
            )
        )


class EmergencyRestoreAccessErrorView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{ZWARNING} Acceso denegado**"),
                Separator(visible=True),
                TextDisplay(
                    "Solo el propietario del servidor puede ejecutar el comando de restauración de emergencia."
                ),
            )
        )


class EmergencyRestoreNoRolesView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay(f"**{CROSS_ALT} Error**"),
                Separator(visible=True),
                TextDisplay(
                    "No se encontraron roles con permisos desactivados para restaurar."
                ),
            )
        )


class EmergencyRestoreResultView(LayoutView):
    def __init__(self, success_msg, error_msg):
        super().__init__(timeout=None)
        self.add_item(
            build_container(
                TextDisplay("**Restauración de emergencia**"),
                Separator(visible=True),
                TextDisplay(
                    f"**{TICK_ALT} Permisos restaurados**:\n{success_msg}\n\n**{ML_CROSS} Errores**:\n{error_msg}\n\nBase de datos borrada."
                ),
            )
        )


class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "db/emergency.db"
        self.bot.loop.create_task(self.initialize_database())

    async def initialize_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS authorised_users (guild_id INTEGER, user_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS emergency_roles (guild_id INTEGER, role_id INTEGER)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS restore_roles (guild_id INTEGER NOT NULL, role_id INTEGER NOT NULL, disabled_perms TEXT NOT NULL, PRIMARY KEY (guild_id, role_id))"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS role_positions (guild_id INTEGER, role_id INTEGER, previous_position INTEGER)"
            )
            await db.commit()

    async def is_guild_owner(self, ctx):
        return ctx.guild and ctx.author.id == ctx.guild.owner_id

    async def is_guild_owner_or_authorised(self, ctx):
        if await self.is_guild_owner(ctx):
            return True
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM authorised_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, ctx.author.id),
            ) as cursor:
                return await cursor.fetchone() is not None

    @commands.group(name="emergency", aliases=["emg"], invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.guild_only()
    async def emergency(self, ctx):
        await ctx.reply(view=EmergencyMainView(ctx, ctx.prefix))

    @emergency.command(name="enable")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.guild_only()
    async def enable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in OWNER_IDS_STR:
            return await ctx.reply(view=EnableErrorView())
        dangerous_perms = [
            "administrator",
            "ban_members",
            "kick_members",
            "manage_channels",
            "manage_roles",
            "manage_guild",
        ]
        roles_added = []
        async with aiosqlite.connect(self.db_path) as db:
            for role in ctx.guild.roles:
                if (
                    role.managed
                    or role.is_bot_managed()
                    or role.position >= ctx.guild.me.top_role.position
                ):
                    continue
                if any(getattr(role.permissions, p, False) for p in dangerous_perms):
                    async with db.execute(
                        "SELECT 1 FROM emergency_roles WHERE guild_id = ? AND role_id = ?",
                        (ctx.guild.id, role.id),
                    ) as cursor:
                        if not await cursor.fetchone():
                            await db.execute(
                                "INSERT INTO emergency_roles (guild_id, role_id) VALUES (?, ?)",
                                (ctx.guild.id, role.id),
                            )
                            roles_added.append(role)
            await db.commit()
        await ctx.reply(view=EnableSuccessView(roles_added))

    @emergency.command(name="disable")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.guild_only()
    async def disable(self, ctx):
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in OWNER_IDS_STR:
            return await ctx.reply(view=DisableErrorView())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM emergency_roles WHERE guild_id = ?", (ctx.guild.id,)
            )
            await db.commit()
        await ctx.reply(view=DisableSuccessView())

    @emergency.group(name="authorise", aliases=["ath"], invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def authorise(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @authorise.command(name="add")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def authorise_add(self, ctx, member: discord.Member):
        if not await self.is_guild_owner(ctx):
            return await ctx.reply(view=AuthoriseErrorView("owner_add"))
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM authorised_users WHERE guild_id = ?",
                (ctx.guild.id,),
            ) as cursor:
                if (await cursor.fetchone())[0] >= 5:
                    return await ctx.reply(view=AuthoriseErrorView("limit"))
            async with db.execute(
                "SELECT 1 FROM authorised_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, member.id),
            ) as cursor:
                if await cursor.fetchone():
                    return await ctx.reply(view=AuthoriseErrorView("exists"))
            await db.execute(
                "INSERT INTO authorised_users (guild_id, user_id) VALUES (?, ?)",
                (ctx.guild.id, member.id),
            )
            await db.commit()
        await ctx.reply(view=AuthoriseSuccessView(member.display_name, "autorizado"))

    @authorise.command(name="remove")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def authorise_remove(self, ctx, member: discord.Member):
        if not await self.is_guild_owner(ctx):
            return await ctx.reply(view=AuthoriseErrorView("owner_remove"))
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM authorised_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, member.id),
            ) as cursor:
                if not await cursor.fetchone():
                    return await ctx.reply(view=AuthoriseErrorView("not_found"))
            await db.execute(
                "DELETE FROM authorised_users WHERE guild_id = ? AND user_id = ?",
                (ctx.guild.id, member.id),
            )
            await db.commit()
        await ctx.reply(view=AuthoriseSuccessView(member.display_name, "eliminado"))

    @authorise.command(name="list", aliases=["view"])
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def list_authorized(self, ctx):
        is_owner = await self.is_guild_owner(ctx)
        if not is_owner:
            return await ctx.reply(view=AuthoriseErrorView("owner_list"))
        async with aiosqlite.connect("db/emergency.db") as db:
            cursor = await db.execute(
                "SELECT user_id FROM authorised_users WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            users = await cursor.fetchall()
        await ctx.reply(view=AuthoriseListView(ctx, users, is_owner))

    @emergency.group(name="role", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def role(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @role.command(name="add")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def role_add(self, ctx, role: discord.Role):
        if not await self.is_guild_owner(ctx):
            return await ctx.reply(view=RoleErrorView("owner_add"))
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM emergency_roles WHERE guild_id = ?",
                (ctx.guild.id,),
            ) as cursor:
                if (await cursor.fetchone())[0] >= 25:
                    return await ctx.reply(view=RoleErrorView("limit"))
            async with db.execute(
                "SELECT 1 FROM emergency_roles WHERE guild_id = ? AND role_id = ?",
                (ctx.guild.id, role.id),
            ) as cursor:
                if await cursor.fetchone():
                    return await ctx.reply(view=RoleErrorView("exists"))
            await db.execute(
                "INSERT INTO emergency_roles (guild_id, role_id) VALUES (?, ?)",
                (ctx.guild.id, role.id),
            )
            await db.commit()
        await ctx.reply(view=RoleSuccessView(role.name, "añadido a"))

    @role.command(name="remove")
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def role_remove(self, ctx, role: discord.Role):
        if not await self.is_guild_owner(ctx):
            return await ctx.reply(view=RoleErrorView("owner_remove"))
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM emergency_roles WHERE guild_id = ? AND role_id = ?",
                (ctx.guild.id, role.id),
            ) as cursor:
                if not await cursor.fetchone():
                    return await ctx.reply(view=RoleErrorView("not_found"))
            await db.execute(
                "DELETE FROM emergency_roles WHERE guild_id = ? AND role_id = ?",
                (ctx.guild.id, role.id),
            )
            await db.commit()
        await ctx.reply(view=RoleSuccessView(role.name, "eliminado de"))

    @role.command(name="list", aliases=["view"])
    @blacklist_check()
    @ignore_check()
    @commands.guild_only()
    async def list_roles(self, ctx):
        is_auth = await self.is_guild_owner_or_authorised(ctx)
        if not is_auth:
            return await ctx.reply(view=RoleErrorView("owner_list"))
        async with aiosqlite.connect("db/emergency.db") as db:
            cursor = await db.execute(
                "SELECT role_id FROM emergency_roles WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            roles = await cursor.fetchall()
        await ctx.reply(view=RoleListView(roles, is_auth))

    @commands.command(name="emergencysituation", aliases=["emgs"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 40, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def emergencysituation(self, ctx):
        if not await self.is_guild_owner_or_authorised(ctx) and str(
            ctx.author.id
        ) not in OWNER_IDS_STR:
            return await ctx.reply(view=EmergencySituationErrorView("access"))

        proc_msg = await ctx.reply(
            view=LayoutView(build_container(TextDisplay("Procesando situación de emergencia...")))
        )
        guild_id = ctx.guild.id

        antinuke_enabled = False
        async with aiosqlite.connect("db/anti.db") as anti:
            cursor = await anti.execute(
                "SELECT status FROM antinuke WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()
            if row:
                antinuke_enabled = True
                await anti.execute(
                    "DELETE FROM antinuke WHERE guild_id = ?", (guild_id,)
                )
                await anti.commit()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM restore_roles WHERE guild_id = ?", (ctx.guild.id,)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT role_id FROM emergency_roles WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            emergency_roles = await cursor.fetchall()

        if not emergency_roles:
            await proc_msg.delete()
            return await ctx.reply(view=EmergencySituationErrorView("no_roles"))

        bot_top = ctx.guild.me.top_role
        dangerous_perms = [
            "administrator",
            "ban_members",
            "kick_members",
            "manage_channels",
            "manage_roles",
            "manage_guild",
        ]
        modified, unchanged = [], []

        async with aiosqlite.connect(self.db_path) as db:
            for (role_id,) in emergency_roles:
                role = ctx.guild.get_role(role_id)
                if not role or role.position >= bot_top.position or role.managed:
                    unchanged.append(role) if role else None
                    continue
                perms = role.permissions
                disabled = []
                for p in dangerous_perms:
                    if getattr(perms, p, False):
                        setattr(perms, p, False)
                        disabled.append(p)
                if disabled:
                    try:
                        await role.edit(permissions=perms, reason="Emergency Situation")
                        modified.append(role)
                        await db.execute(
                            "INSERT INTO restore_roles VALUES (?, ?, ?)",
                            (ctx.guild.id, role.id, ",".join(disabled)),
                        )
                        await db.commit()
                    except:
                        unchanged.append(role)

        success = "\n".join([r.mention for r in modified]) or "No se modificó ningún rol."
        errors = "\n".join([r.mention for r in unchanged]) or "Sin errores."

        most_mem = max(
            [
                r
                for r in ctx.guild.roles
                if not r.managed
                and r.position < bot_top.position
                and r != ctx.guild.default_role
            ],
            key=lambda r: len(r.members),
            default=None,
        )

        if most_mem:
            try:
                await most_mem.edit(
                    position=bot_top.position - 1, reason="Emergency Situation"
                )
                result_view = EmergencySituationResultView(
                    success, errors, moved_role=most_mem
                )
            except discord.Forbidden:
                result_view = EmergencySituationResultView(
                    success, errors, move_failed=True
                )
            except Exception as e:
                result_view = EmergencySituationResultView(
                    success, errors, move_error=str(e)
                )
        else:
            result_view = EmergencySituationResultView(success, errors)

        await ctx.reply(view=result_view)

        if antinuke_enabled:
            async with aiosqlite.connect("db/anti.db") as anti:
                await anti.execute("INSERT INTO antinuke VALUES (?, 1)", (guild_id,))
                await anti.commit()
        await proc_msg.delete()

    @commands.command(name="emergencyrestore", aliases=["emgrestore"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    async def emergencyrestore(self, ctx):
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in OWNER_IDS_STR:
            return await ctx.reply(view=EmergencyRestoreAccessErrorView())

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT role_id, disabled_perms FROM restore_roles WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            restore_roles = await cursor.fetchall()

        if not restore_roles:
            return await ctx.reply(view=EmergencyRestoreNoRolesView())

        view = EmergencyRestoreConfirmView(ctx)
        await ctx.send(view=view)
        await view.wait()

        if view.value is None:
            return await ctx.reply(
                view=LayoutView(
                    build_container(TextDisplay("**Restauración cancelada** - Tiempo agotado."))
                )
            )
        if view.value is False:
            return await ctx.reply(
                view=LayoutView(build_container(TextDisplay("**Restauración cancelada**")))
            )

        modified, unchanged = [], []
        async with aiosqlite.connect(self.db_path) as db:
            for role_id, perms in restore_roles:
                role = ctx.guild.get_role(role_id)
                if not role:
                    continue
                rp = role.permissions
                restored = False
                for p in perms.split(","):
                    if hasattr(rp, p):
                        setattr(rp, p, True)
                        restored = True
                if restored:
                    try:
                        await role.edit(permissions=rp, reason="Emergency Restore")
                        modified.append(role)
                    except:
                        unchanged.append(role)
            await db.execute(
                "DELETE FROM restore_roles WHERE guild_id = ?", (ctx.guild.id,)
            )
            await db.commit()

        success = "\n".join([r.mention for r in modified]) or "No se restauró ningún rol."
        errors = "\n".join([r.mention for r in unchanged]) or "Sin errores."
        await ctx.reply(view=EmergencyRestoreResultView(success, errors))


async def setup(bot):
    await bot.add_cog(Emergency(bot))
