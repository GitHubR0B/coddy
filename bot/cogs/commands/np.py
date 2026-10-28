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

from discord.ext import commands, tasks
from discord import *
import discord
from utils.emoji import BOOST, ICONS_WARNING, INFO, MENTION, PREMIUM, TICK, TIME, TIMER_ALT1, U_ADMIN, ZDIL, ZHUMAN, ZYROXHAMMER, ZYROXSYS
import aiosqlite
from typing import Optional
from datetime import datetime, timedelta
from discord.ui import View, Button, Select
from utils.config import OWNER_IDS
from utils import Paginator, DescriptionEmbedPaginator
from utils.cv2 import CV2Embed, add_action_rows
from utils.config import *


def load_owner_ids():
    return OWNER_IDS


async def is_staff(user, staff_ids):
    return user.id in staff_ids


async def is_owner_or_staff(ctx):
    return await is_staff(ctx.author, ctx.cog.staff) or ctx.author.id in OWNER_IDS


class TimeSelect(Select):
    def __init__(self, user, db_path, author):
        super().__init__(placeholder="Selecciona la duración")
        self.user = user
        self.db_path = db_path
        self.author = author

        self.options = [
            SelectOption(
                label="10 minutos", description="Prueba por 10 minutos", value="10m"
            ),
            SelectOption(
                label="1 semana", description="Sin prefijo durante 1 semana", value="1w"
            ),
            SelectOption(
                label="3 semanas", description="Sin prefijo durante 3 semanas", value="3w"
            ),
            SelectOption(
                label="1 mes", description="Sin prefijo durante 1 mes", value="1m"
            ),
            SelectOption(
                label="3 meses", description="Sin prefijo durante 3 meses.", value="3m"
            ),
            SelectOption(
                label="6 meses", description="Sin prefijo durante 6 meses.", value="6m"
            ),
            SelectOption(
                label="1 año", description="Sin prefijo durante 1 año.", value="1y"
            ),
            SelectOption(
                label="3 años", description="Sin prefijo durante 3 años.", value="3y"
            ),
            SelectOption(
                label="De por vida", description="Sin prefijo de forma permanente.", value="lifetime"
            ),
        ]

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message(
                "No puedes seleccionar esta opción.", ephemeral=True
            )

        duration_mapping = {
            "10m": timedelta(minutes=10),
            "1w": timedelta(weeks=1),
            "3w": timedelta(weeks=3),
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "3y": timedelta(days=365 * 3),
            "lifetime": None,
        }

        selected_duration = self.values[0]
        expiry_time = None

        if selected_duration != "lifetime":
            expiry_time = datetime.utcnow() + duration_mapping[selected_duration]
            expiry_str = expiry_time.isoformat()
        else:
            expiry_str = None

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO np (id, expiry_time) VALUES (?, ?)",
                (self.user.id, expiry_str),
            )
            await db.commit()

        expiry_text = (
            "**De por vida**"
            if selected_duration == "lifetime"
            else f"{expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        expiry_timestamp = (
            "Ninguno (permanente)"
            if selected_duration == "lifetime"
            else f"<t:{int(expiry_time.timestamp())}:f>"
        )

        guild = interaction.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(self.user.id)
            if member:
                role = guild.get_role(1401134167873290311)
                if role:
                    await member.add_roles(role, reason="No prefix added")

        log_channel = interaction.client.get_channel(1396794297386532978)
        if log_channel:
            embed = CV2Embed(
                title="Usuario añadido a Sin prefijo",
                description=f"**Usuario**: [{self.user}](https://discord.com/users/{self.user.id})\n**Mención del usuario**: {self.user.mention}\n** ID**: {self.user.id}\n\n** Añadido por**: [{self.author.display_name}](https://discord.com/users/{self.author.id})\n{TIMER_ALT1}**Fecha de caducidad**: {expiry_text}\n{ZDIL} **Marca de tiempo**: {expiry_timestamp}\n\n{PREMIUM} **Nivel**: **{self.values[0].upper()}**",
                color=0xFF0000,
            )
            embed.set_thumbnail(
                url=self.user.avatar.url
                if self.user.avatar
                else self.user.default_avatar.url
            )
            await log_channel.send("<#1396794297386532978>", view=embed)

        embed = CV2Embed(
            description=f"**Sin prefijo global añadido**:\n{ZHUMAN} Usuario: **{self.user.mention}**\n{MENTION} Mención del usuario: {self.user.mention}\n{ZYROXSYS} ID del usuario: {self.user.id}\n\n__**Información adicional**__:\n{ZYROXHAMMER} Añadido por: **{self.author.display_name}**\n{TIME} Fecha de caducidad: {expiry_text}\n{BOOST} Marca de tiempo: {expiry_timestamp}",
            color=0xFF0000,
        )
        embed.set_author(
            name="Sin prefijo añadido",
            icon_url="https://cdn.discordapp.com/icons/1166303696263585852/eeb00b2cf541438e88cdf842394c5b30.png?size=1024",
        )
        embed.set_footer(
            text="Se enviará un mensaje directo al usuario en caso de que caduque el acceso sin prefijo."
        )
        await interaction.response.edit_message(view=embed)


class TimeSelectView(View):
    def __init__(self, user, db_path, author):
        super().__init__()
        self.user = user
        self.db_path = db_path
        self.author = author
        self.add_item(TimeSelect(user, db_path, author))


from utils.config import BotName

class NoPrefix(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.staff = set()
        self.db_path = "db/np.db"
        self.client.loop.create_task(self.load_staff())
        self.client.loop.create_task(self.setup_database())
        self.expiry_check.start()

    async def setup_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS np (
                    id INTEGER PRIMARY KEY
                )
            """)

            async with db.execute("PRAGMA table_info(np);") as cursor:
                columns = [info[1] for info in await cursor.fetchall()]

            if "expiry_time" not in columns:
                await db.execute("""
                    ALTER TABLE np ADD COLUMN expiry_time TEXT NULL;
                """)

            await db.execute("""
                UPDATE np
                SET expiry_time = NULL
                WHERE expiry_time IS NULL;
            """)
            await db.execute("""
    CREATE TABLE IF NOT EXISTS autonp (
        guild_id INTEGER PRIMARY KEY
    )
    """)

            await db.commit()

    async def load_staff(self):
        await self.client.wait_until_ready()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM staff") as cursor:
                self.staff = {row[0] for row in await cursor.fetchall()}

    @tasks.loop(minutes=10)
    async def expiry_check(self):
        async with aiosqlite.connect(self.db_path) as db:
            now = datetime.utcnow().isoformat()
            async with db.execute(
                "SELECT id FROM np WHERE expiry_time IS NOT NULL AND expiry_time <= ?",
                (now,),
            ) as cursor:
                expired_users = [row[0] for row in await cursor.fetchall()]

            if expired_users:
                async with db.execute(
                    "DELETE FROM np WHERE id IN ({})".format(
                        ",".join("?" * len(expired_users))
                    ),
                    expired_users,
                ):
                    await db.commit()

                for user_id in expired_users:
                    user = self.client.get_user(user_id)
                    if user:
                        log_channel = self.client.get_channel(1396794297386532978)
                        if log_channel:
                            embed_log = CV2Embed(
                                title="Sin prefijo caducado",
                                description=(
                    f"**Usuario**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**Mención del usuario**: {user.mention}\n"
                    f"**ID**: {user.id}\n\n"
                    f"**Eliminado por**: **{BotName}**\n"
                ),
                                color=0xFF0000,
                            )
                            embed_log.set_thumbnail(
                                url=user.display_avatar.url
                                if user.avatar
                                else user.default_avatar.url
                            )
                            embed_log.set_footer(text="Registro de eliminación de Sin prefijo")
                            await log_channel.send(
                                "<#1396794297386532978>", view=embed_log
                            )
                        bot = self.client
                        guild = bot.get_guild(1401125905677553716)
                        if guild:
                            member = guild.get_member(user.id)
                            if member:
                                role = guild.get_role(1401134167873290311)
                                if role in member.roles:
                                    await member.remove_roles(role)

                        embed = CV2Embed(
                            description=f"{ICONS_WARNING} Tu estado de Sin prefijo ha **caducado**. Ahora necesitarás el prefijo para usar comandos.",
                            color=0xFF0000,
                        )
                        embed.set_author(
                            name="Sin prefijo caducado",
                            icon_url=user.avatar.url
                            if user.avatar
                            else user.default_avatar.url,
                        )

                        embed.set_footer(
                            text=f"{BRAND_NAME}  - Sin prefijo. Únete al soporte para recuperar el acceso."
                        )
                        support = Button(
                            label="Soporte",
                            style=discord.ButtonStyle.link,
                            url=f"https://discord.gg/codexdev",
                        )
                        view = View()
                        view.add_item(support)

                        try:
                            add_action_rows(embed, view.children)
                            await user.send(f"{user.mention}", view=embed)
                        except discord.Forbidden:
                            pass
                        except discord.HTTPException:
                            pass

    @expiry_check.before_loop
    async def before_expiry_check(self):
        await self.client.wait_until_ready()

    @commands.group(
        name="np",
        help="Te permite añadir a alguien a la lista de sin prefijo (comando solo para propietarios)",
    )
    @commands.check(is_owner_or_staff)
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list", help="Lista de usuarios sin prefijo")
    @commands.check(is_owner_or_staff)
    async def np_list(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id FROM np") as cursor:
                ids = [row[0] for row in await cursor.fetchall()]
                if not ids:
                    await ctx.reply(
                        f"No hay usuarios en la lista de sin prefijo.", mention_author=False
                    )
                    return
                entries = [
                    f"`#{no + 1}`  [Perfil](https://discord.com/users/{mem}) (ID: {mem})"
                    for no, mem in enumerate(ids, start=0)
                ]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(
                        entries=entries,
                        title=f"Usuarios sin prefijo [{len(ids)}]",
                        description="",
                        per_page=10,
                        color=0xFF0000,
                    ),
                    ctx=ctx,
                )
                await paginator.paginate()

    @_np.command(name="add", help="Añade un usuario a sin prefijo con opciones de duración")
    @commands.check(is_owner_or_staff)
    async def np_add(self, ctx, user: discord.User):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()
            if result:
                embed = CV2Embed(
                    description=f"**{user}** ya está en la lista de sin prefijo\n\n **Solicitado por**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                embed.set_author(name="Error")
                await ctx.reply(view=embed)
                return

        view = TimeSelectView(user, self.db_path, ctx.author)
        from discord.ui import ActionRow

        embed = CV2Embed(
            title="Selecciona la duración de Sin prefijo",
            description="**Elige cuánto tiempo debe estar activado sin prefijo para este usuario:**",
            color=0xFF0000,
        )
        for item in view.children:
            embed.children[0].add_item(ActionRow(item))
        await ctx.reply(view=embed)

    @_np.command(name="remove", help="Elimina un usuario de sin prefijo")
    @commands.check(is_owner_or_staff)
    async def np_remove(self, ctx, user: discord.User):
        async with aiosqlite.connect("db/np.db") as db:
            async with db.execute(
                "SELECT id FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()
            if not result:
                embed = CV2Embed(
                    description=f"**{user}** no está en la lista de Sin prefijo\n\n{U_ADMIN} **Solicitado por**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                embed.set_author(name="Error")
                await ctx.reply(view=embed)
                return

            await db.execute("DELETE FROM np WHERE id = ?", (user.id,))
            await db.commit()

        guild = ctx.bot.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member:
                role = guild.get_role(1401134167873290311)
                if role in member.roles:
                    await member.remove_roles(role)

        embed = CV2Embed(
            description=(
                f"**Usuario**: [{user}](https://discord.com/users/{user.id})\n"
                f"**Mención del usuario**: {user.mention}\n"
                f"** ID**: {user.id}\n\n"
                f"** Eliminado por**: **{BotName}**\n"
            ),
            color=0xFF0000,
        )
        embed.set_author(name="Sin prefijo eliminado")
        await ctx.reply(view=embed)

        log_channel = ctx.bot.get_channel(1396794297386532978)
        if log_channel:
            embed_log = CV2Embed(
                title="Sin prefijo eliminado",
                description=(
                    f"**Usuario**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**Mención del usuario**: {user.mention}\n"
                    f"** ID**: {user.id}\n\n"
                    f"**Eliminado por**: **{BotName}**\n"
                ),
                color=0xFF0000,
            )
            embed_log.set_thumbnail(
                url=user.display_avatar.url if user.avatar else user.default_avatar.url
            )
            embed_log.set_footer(text="Registro de eliminación de Sin prefijo")
            await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed_log)

    @_np.command(
        name="status", help="Comprueba si un usuario está en la lista de Sin prefijo y muestra los detalles."
    )
    @commands.check(is_owner_or_staff)
    async def np_status(self, ctx, user: discord.User):
        async with aiosqlite.connect("db/np.db") as db:
            async with db.execute(
                "SELECT id, expiry_time FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                result = await cursor.fetchone()

            if not result:
                embed = CV2Embed(
                    title="Estado de Sin prefijo",
                    description=f"**{user}** no está en la lista de Sin prefijo\n\n"
                    f"**Solicitado por**: "
                    f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0xFF0000,
                )
                await ctx.reply(view=embed)
                return

            user_id, expires = result

            if expires and expires != "Null":
                expire_time = datetime.fromisoformat(expires)
                expire_timestamp = f"<t:{int(expire_time.timestamp())}:F>"
            else:
                expire_time = "De por vida"
                expire_timestamp = "De por vida"

            embed = CV2Embed(
                title="Estado de Sin prefijo",
                description=(
                    f"**Usuario**: [{user}](https://discord.com/users/{user.id})\n"
                    f"**ID del usuario**: {user.id}\n\n"
                    f"{TIME} Caducidad: {expire_time} ({expire_timestamp})"
                ),
                color=0xFF0000,
            )

            embed.set_thumbnail(
                url=user.display_avatar.url if user.avatar else user.default_avatar.url
            )

        await ctx.reply(view=embed)

    @commands.group(name="autonp", help="Administra el sin prefijo automático para servidores asociados.")
    @commands.is_owner()
    async def autonp(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @autonp.group(name="guild", help="Administra los servidores asociados para el sin prefijo automático.")
    async def autonp_guild(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @autonp_guild.command(name="add", help="Añade un servidor al sin prefijo automático.")
    async def add_guild(self, ctx, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                if await cursor.fetchone():
                    await ctx.reply("El servidor ya está añadido.")
                    return
            await db.execute("INSERT INTO autonp (guild_id) VALUES (?)", (guild_id,))
            await db.commit()
        await ctx.reply(f"Servidor {guild_id} añadido al sin prefijo automático.")

    @autonp_guild.command(name="remove", help="Elimina un servidor del sin prefijo automático.")
    async def remove_guild(self, ctx, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                if not await cursor.fetchone():
                    await ctx.reply("El servidor no está en el sin prefijo automático.")
                    return
            await db.execute("DELETE FROM autonp WHERE guild_id = ?", (guild_id,))
            await db.commit()
        await ctx.reply(f"Servidor {guild_id} eliminado del sin prefijo automático.")

    @autonp_guild.command(name="list", help="Muestra todos los servidores con sin prefijo automático.")
    @commands.check(is_owner_or_staff)
    async def list_guilds(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT guild_id FROM autonp") as cursor:
                guilds = [row[0] for row in await cursor.fetchall()]
                if not guilds:
                    await ctx.reply(
                        "No hay servidores con sin prefijo automático.", mention_author=False
                    )
                    return
                await ctx.reply(
                    f"Servidores con sin prefijo automático:\n" + "\n".join(str(g) for g in guilds),
                    mention_author=False,
                )

    async def is_user_in_np(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM np WHERE id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone() is not None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is None and after.premium_since is not None:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT 1 FROM autonp WHERE guild_id = ?", (after.guild.id,)
                ) as cursor:
                    if not await cursor.fetchone():
                        return
            if not await self.is_user_in_np(after.id):
                await self.add_np(after, timedelta(days=60))
                log_channel = self.client.get_channel(1406566123234787378)
                embed = CV2Embed(
                    title="Sin prefijo añadido por impulsar un servidor asociado",
                    description=f"**Usuario**: **[{after}](https://discord.com/users/{after.id})** (ID: {after.id})\n**Servidor**: {after.guild.name}",
                    color=0xFF0000,
                )
                message = await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed)
                await message.publish()

        elif before.premium_since is not None and after.premium_since is None:
            await self.handle_boost_removal(after)

    # @commands.Cog.listener()
    # async def on_member_remove(self, member):
    # await self.handle_boost_removal(member)

    async def handle_boost_removal(self, user):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT 1 FROM autonp WHERE guild_id = ?", (user.guild.id,)
            ) as cursor:
                if not await cursor.fetchone():
                    return
        if await self.is_user_in_np(user.id):
            await self.remove_np(user)
            log_channel = self.client.get_channel(1406566257070964756)
            embed = CV2Embed(
                title="Sin prefijo eliminado por dejar de impulsar un servidor asociado",
                description=f"**Usuario**: **[{user}](https://discord.com/users/{user.id})** (ID: {user.id})\n**Servidor**: {user.guild.name}",
                color=0xFF0000,
            )
            message = await log_channel.send(" ".join(f"<@{oid}>" for oid in OWNER_IDS), view=embed)
            await message.publish()

    async def add_np(self, user, duration):
        expiry_time = datetime.utcnow() + duration
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO np (id, expiry_time) VALUES (?, ?)",
                (user.id, expiry_time.isoformat()),
            )
            await db.commit()

        embed = CV2Embed(
            title="¡Felicidades, obtuviste 2 meses de Sin prefijo!",
            description=f"Se te han acreditado 2 meses de Sin prefijo global por impulsar nuestros servidores asociados. Ahora puedes usar mis comandos sin prefijo. Si deseas eliminarlo, contacta con el [servidor de soporte](https://discord.gg/codexdev).",
            color=0xFF0000,
        )
        try:
            await user.send(view=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        guild = self.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member is not None:
                role = guild.get_role(1401134167873290311)
                if role:
                    await member.add_roles(role)

    async def remove_np(self, user):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT expiry_time FROM np WHERE id = ?", (user.id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None or row[0] is None:
                    return

            await db.execute("DELETE FROM np WHERE id = ?", (user.id,))
            await db.commit()

        embed = CV2Embed(
            title=f"{ICONS_WARNING} Sin prefijo global caducado",
            description=f"¡Hola {user.mention}, tu sin prefijo global ha caducado!\n\n__**Motivo:**__ Dejaste de impulsar nuestro servidor asociado.\nSi crees que es un error, contacta con el [servidor de soporte](https://discord.gg/codexdev).",
            color=0xFF0000,
        )

        try:
            await user.send(view=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        guild = self.client.get_guild(1401125905677553716)
        if guild:
            member = guild.get_member(user.id)
            if member is not None:
                role = guild.get_role(1401134167873290311)
                if role and role in member.roles:
                    await member.remove_roles(role)

    @_np.command(name="reset", help="Restablece o vacía todos los usuarios de la lista de sin prefijo")
    @commands.is_owner()
    async def np_reset(self, ctx):
        # Confirmation message
        embed = CV2Embed(
            title="Confirmar restablecimiento",
            description="¿Seguro que quieres eliminar a **TODOS** los usuarios de la lista de sin prefijo? Esta acción no se puede deshacer.",
            color=0xFF0000,
        )

        # Create confirmation buttons
        yes_button = Button(label="Sí", style=discord.ButtonStyle.danger)
        no_button = Button(label="No", style=discord.ButtonStyle.secondary)

        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        # Define button callbacks
        async def yes_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    "Esta interacción no es para ti.", ephemeral=True
                )

            # Remove all users from no-prefix list
            async with aiosqlite.connect(self.db_path) as db:
                # Get count of users before deletion
                async with db.execute("SELECT COUNT(*) FROM np") as cursor:
                    count = (await cursor.fetchone())[0]

                # Delete all entries
                await db.execute("DELETE FROM np")
                await db.commit()

            # Remove roles from all members in the main guild
            guild = self.client.get_guild(1401125905677553716)
            if guild:
                role = guild.get_role(1401134167873290311)
                if role:
                    members_with_role = [
                        member for member in guild.members if role in member.roles
                    ]
                    for member in members_with_role:
                        try:
                            await member.remove_roles(
                                role, reason="Global no-prefix reset"
                            )
                        except discord.HTTPException:
                            pass

            # Send success message
            success_embed = CV2Embed(
                title=f"{TICK} Restablecimiento de Sin prefijo completado",
                description=f"Se eliminaron correctamente {count} usuarios de la lista de sin prefijo.",
                color=0xFF0000,
            )
            await interaction.response.edit_message(view=success_embed)

            # Log the action
            log_channel = self.client.get_channel(1396794297386532978)
            if log_channel:
                log_embed = CV2Embed(
                    title="Lista de Sin prefijo restablecida",
                    description=f"**Restablecido por**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n{INFO} Usuarios eliminados: {count}",
                    color=0xFF0000,
                )
                log_embed.set_footer(text="Registro de restablecimiento de Sin prefijo")
                await log_channel.send("<#1396794297386532978>", view=log_embed)

        async def no_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    "Esta interacción no es para ti.", ephemeral=True
                )

            cancel_embed = CV2Embed(
                title="Restablecimiento cancelado",
                description="No se han realizado cambios en la lista de sin prefijo.",
                color=0xFF0000,
            )
            await interaction.response.edit_message(view=cancel_embed)

        yes_button.callback = yes_callback
        no_button.callback = no_callback

        add_action_rows(embed, view.children)
        await ctx.reply(view=embed)
