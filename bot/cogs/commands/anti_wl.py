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
from utils.emoji import ARROWRED, CROSS, DISABLE, ENABLE, MANAGER, TICK
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, Container
import aiosqlite
from utils.Tools import *
from utils.cv2 import CV2, build_container





class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    
    #@commands.Cog.listener()
    async def initialize_db(self):
        self.db = await aiosqlite.connect('db/anti.db')
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS whitelisted_users (
                guild_id INTEGER,
                user_id INTEGER,
                ban BOOLEAN DEFAULT FALSE,
                kick BOOLEAN DEFAULT FALSE,
                prune BOOLEAN DEFAULT FALSE,
                botadd BOOLEAN DEFAULT FALSE,
                serverup BOOLEAN DEFAULT FALSE,
                memup BOOLEAN DEFAULT FALSE,
                chcr BOOLEAN DEFAULT FALSE,
                chdl BOOLEAN DEFAULT FALSE,
                chup BOOLEAN DEFAULT FALSE,
                rlcr BOOLEAN DEFAULT FALSE,
                rlup BOOLEAN DEFAULT FALSE,
                rldl BOOLEAN DEFAULT FALSE,
                meneve BOOLEAN DEFAULT FALSE,
                mngweb BOOLEAN DEFAULT FALSE,
                mngstemo BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        await self.db.commit()

    @commands.hybrid_command(name='whitelist', aliases=['wl'], help="Añade un usuario a la lista blanca de Antinuke para una acción específica.")

    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)

    async def whitelist(self, ctx, member: discord.Member = None):
        if ctx.guild.member_count < 2:
            view = CV2(f"{CROSS} Error", "Tu servidor no cumple con mi criterio de 30 miembros")
            return await ctx.send(view=view)

        prefix=ctx.prefix

        async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

        async with self.db.execute(
            "SELECT status FROM antinuke WHERE guild_id = ?",
            (ctx.guild.id,)
        ) as cursor:
            antinuke = await cursor.fetchone()

        is_owner = ctx.author.id == ctx.guild.owner_id
        if not is_owner and not check:
            view = CV2(f"{CROSS} Acceso denegado", "¡Solo el propietario del servidor o un propietario extra puede ejecutar este comando!")
            return await ctx.send(view=view)

        if not antinuke or not antinuke[0]:
            view = CV2(
                f"Ajustes de seguridad de {ctx.guild.name} {MANAGER}",
                f"¡Vaya! Parece que tu servidor no tiene Antinuke activado\n\nEstado actual: {CROSS}\n\nPara activarlo usa `{prefix}antinuke enable`"
            )
            return await ctx.send(view=view)

        if not member:
            view = CV2(
                "__Comandos de lista blanca__",
                "**Añadir un usuario a la lista blanca significa que no se tomarán acciones contra él si activa el módulo Anti-Nuke.**",
                f"**Uso**\n{ARROWRED} `{prefix}whitelist @user/id`\n{ARROWRED} `{prefix}wl @user`"
            )
            return await ctx.send(view=view)

        async with self.db.execute(
            "SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id)
        ) as cursor:
            data = await cursor.fetchone()

        if data:
            view = CV2(f"{CROSS} Error", f"<@{member.id}> ya está en la lista blanca; usa **unwhitelist** con el usuario y vuelve a intentarlo.")
            return await ctx.send(view=view)

        await self.db.execute(
            "INSERT INTO whitelisted_users (guild_id, user_id) VALUES (?, ?)",
            (ctx.guild.id, member.id)
        )
        await self.db.commit()

        options = [
            discord.SelectOption(label="Banear", description="Añade a la lista blanca a un miembro con permiso de banear", value="ban"),
            discord.SelectOption(label="Expulsar", description="Añade a la lista blanca a un miembro con permiso de expulsar", value="kick"),
            discord.SelectOption(label="Purgar", description="Añade a la lista blanca a un miembro con permiso de purgar", value="prune"),
            discord.SelectOption(label="Añadir bots", description="Añade a la lista blanca a un miembro con permiso de añadir bots", value="botadd"),
            discord.SelectOption(label="Actualización del servidor", description="Añade a la lista blanca a un miembro con permiso de actualizar el servidor", value="serverup"),
            discord.SelectOption(label="Actualización de miembros", description="Añade a la lista blanca a un miembro con permiso de actualizar miembros", value="memup"),
            discord.SelectOption(label="Creación de canales", description="Añade a la lista blanca a un miembro con permiso de crear canales", value="chcr"),
            discord.SelectOption(label="Eliminación de canales", description="Añade a la lista blanca a un miembro con permiso de eliminar canales", value="chdl"),
            discord.SelectOption(label="Actualización de canales", description="Añade a la lista blanca a un miembro con permiso de actualizar canales", value="chup"),
            discord.SelectOption(label="Creación de roles", description="Añade a la lista blanca a un miembro con permiso de crear roles", value="rlcr"),
            discord.SelectOption(label="Actualización de roles", description="Añade a la lista blanca a un miembro con permiso de actualizar roles", value="rlup"),
            discord.SelectOption(label="Eliminación de roles", description="Añade a la lista blanca a un miembro con permiso de eliminar roles", value="rldl"),
            discord.SelectOption(label="Mencionar a todos", description="Añade a la lista blanca a un miembro con permiso de mencionar a todos", value="meneve"),
            discord.SelectOption(label="Gestionar webhook", description="Añade a la lista blanca a un miembro con permiso de gestionar webhooks", value="mngweb")
        ]

        select = discord.ui.Select(placeholder="Elige tus opciones", min_values=1, max_values=len(options), options=options, custom_id="wl")
        button = discord.ui.Button(label="Añadir este usuario a todas las categorías", style=discord.ButtonStyle.primary, custom_id="catWl")

        action_view = discord.ui.View()
        action_view.add_item(select)
        action_view.add_item(button)

        disabled_list = (
            f"{DISABLE} : **Banear**\n"
            f"{DISABLE} : **Expulsar**\n"
            f"{DISABLE} : **Purgar**\n"
            f"{DISABLE} : **Añadir bots**\n"
            f"{DISABLE} : **Actualización del servidor**\n"
            f"{DISABLE} : **Actualización de miembros**\n"
            f"{DISABLE} : **Creación de canales**\n"
            f"{DISABLE} : **Eliminación de canales**\n"
            f"{DISABLE} : **Actualización de canales**\n"
            f"{DISABLE} : **Creación de roles**\n"
            f"{DISABLE} : **Eliminación de roles**\n"
            f"{DISABLE} : **Actualización de roles**\n"
            f"{DISABLE} : **Mención** @everyone\n"
            f"{DISABLE} : **Gestión de webhooks**"
        )

        wl_view = CV2(
            ctx.guild.name,
            disabled_list,
            f"**Ejecutor:** <@!{ctx.author.id}> │ **Objetivo:** <@!{member.id}>"
        )

        msg = await ctx.send(view=action_view)

        def check(interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == msg.id

        try:
            interaction = await self.bot.wait_for("interaction", check=check, timeout=60.0)
            if interaction.data["custom_id"] == "catWl":
                
                await self.db.execute(
                    "UPDATE whitelisted_users SET ban = ?, kick = ?, prune = ?, botadd = ?, serverup = ?, memup = ?, chcr = ?, chdl = ?, chup = ?, rlcr = ?, rldl = ?, rlup = ?, meneve = ?, mngweb = ?, mngstemo = ? WHERE guild_id = ? AND user_id = ?",
                    (True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, ctx.guild.id, member.id)
                )
                await self.db.commit()

                enabled_list = (
                    f"{ENABLE} : **Banear**\n"
                    f"{ENABLE} : **Expulsar**\n"
                    f"{ENABLE} : **Purgar**\n"
                    f"{ENABLE} : **Añadir bots**\n"
                    f"{ENABLE} : **Actualización del servidor**\n"
                    f"{ENABLE} : **Actualización de miembros**\n"
                    f"{ENABLE} : **Creación de canales**\n"
                    f"{ENABLE} : **Eliminación de canales**\n"
                    f"{ENABLE} : **Actualización de canales**\n"
                    f"{ENABLE} : **Creación de roles**\n"
                    f"{ENABLE} : **Eliminación de roles**\n"
                    f"{ENABLE} : **Actualización de roles**\n"
                    f"{ENABLE} : **Mención** @everyone\n"
                    f"{ENABLE} : **Gestión de webhooks**"
                )

                result = CV2(
                    ctx.guild.name,
                    enabled_list,
                    f"**Ejecutor:** <@!{ctx.author.id}> │ **Objetivo:** <@!{member.id}>"
                )
                await interaction.response.edit_message(view=result)
            else:
                
                fields = {
                    'ban': 'Banear',
                    'kick': 'Expulsar',
                    'prune': 'Purgar',
                    'botadd': 'Añadir bots',
                    'serverup': 'Actualización del servidor',
                    'memup': 'Actualización de miembros',
                    'chcr': 'Creación de canales',
                    'chdl': 'Eliminación de canales',
                    'chup': 'Actualización de canales',
                    'rlcr': 'Creación de roles',
                    'rldl': 'Eliminación de roles',
                    'rlup': 'Actualización de roles',
                    'meneve': 'Mencionar a todos',
                    'mngweb': 'Gestionar webhooks'
                }

                
                status_lines = []
                selected_values = interaction.data["values"]
                for key, name in fields.items():
                    if key in selected_values:
                        status_lines.append(f"{ENABLE} : **{name}**")
                    else:
                        status_lines.append(f"{DISABLE} : **{name}**")

                for value in selected_values:
                    await self.db.execute(
                        f"UPDATE whitelisted_users SET {value} = ? WHERE guild_id = ? AND user_id = ?",
                        (True, ctx.guild.id, member.id)
                    )

                await self.db.commit()

                result = CV2(
                    ctx.guild.name,
                    "\n".join(status_lines),
                    f"**Ejecutor:** <@!{ctx.author.id}> │ **Objetivo:** <@!{member.id}>"
                )
                await interaction.response.edit_message(view=result)
        except TimeoutError:
            await msg.edit(view=None)


    @commands.hybrid_command(name='whitelisted', aliases=['wlist'], help="Muestra la lista de usuarios en la lista blanca.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelisted(self, ctx):
        if ctx.guild.member_count < 2:
            view = CV2(f"{CROSS} Error", "Tu servidor no cumple con mi criterio de 30 miembros")
            return await ctx.send(view=view)

        pre=ctx.prefix

        async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

        async with self.db.execute(
            "SELECT status FROM antinuke WHERE guild_id = ?",
            (ctx.guild.id,)
        ) as cursor:
            antinuke = await cursor.fetchone()

        is_owner = ctx.author.id == ctx.guild.owner_id
        if not is_owner and not check:
            view = CV2(f"{CROSS} Acceso denegado", "¡Solo el propietario del servidor o un propietario extra puede ejecutar este comando!")
            return await ctx.send(view=view)

        if not antinuke or not antinuke[0]:
            view = CV2(
                f"Ajustes de seguridad de {ctx.guild.name} {MANAGER}",
                f"¡Vaya! Parece que tu servidor no tiene la seguridad activada\n\nEstado actual: {CROSS}\n\nPara activarla usa `{pre}antinuke enable`"
            )
            return await ctx.send(view=view)


        async with self.db.execute(
            "SELECT user_id FROM whitelisted_users WHERE guild_id = ?",
            (ctx.guild.id,)
        ) as cursor:
            data = await cursor.fetchall()

        if not data:
            view = CV2(f"{CROSS} Error", "No se encontraron usuarios en la lista blanca.")
            return await ctx.send(view=view)

        whitelisted_users = [self.bot.get_user(user_id[0]) for user_id in data]
        whitelisted_users_str = ", ".join(f"<@!{user.id}>" for user in whitelisted_users if user)

        view = CV2(f"__Usuarios en la lista blanca de {ctx.guild.name}__", whitelisted_users_str)
        await ctx.send(view=view)


    @commands.hybrid_command(name="whitelistreset", aliases=['wlreset'], help="Restablece los usuarios en la lista blanca.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def whitelistreset(self, ctx):
        if ctx.guild.member_count < 2:
            view = CV2(f"{CROSS} Error", "Tu servidor no cumple con mi criterio de 30 miembros")
            return await ctx.send(view=view)

        pre=ctx.prefix

        async with self.db.execute(
            "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
            (ctx.guild.id, ctx.author.id)
        ) as cursor:
            check = await cursor.fetchone()

        async with self.db.execute(
            "SELECT status FROM antinuke WHERE guild_id = ?",
            (ctx.guild.id,)
        ) as cursor:
            antinuke = await cursor.fetchone()

        is_owner = ctx.author.id == ctx.guild.owner_id
        if not is_owner and not check:
            view = CV2(f"{CROSS} Acceso denegado", "¡Solo el propietario del servidor o un propietario extra puede ejecutar este comando!")
            return await ctx.send(view=view)

        if not antinuke or not antinuke[0]:
            view = CV2(
                f"Ajustes de seguridad de {ctx.guild.name} {MANAGER}",
                f"¡Vaya! Parece que tu servidor no tiene la seguridad activada\n\nEstado actual: {CROSS}\n\nPara activarla usa `{pre}antinuke enable`"
            )
            return await ctx.send(view=view)

        async with self.db.execute(
            "SELECT user_id FROM whitelisted_users WHERE guild_id = ?",
            (ctx.guild.id,)
        ) as cursor:
            data = await cursor.fetchall()


        if not data:
            view = CV2(f"{CROSS} Error", "No se encontraron usuarios en la lista blanca.")
            return await ctx.send(view=view)

        await self.db.execute("DELETE FROM whitelisted_users WHERE guild_id = ?", (ctx.guild.id,))
        await self.db.commit()
        view = CV2(f"{TICK} Éxito", f"Se quitaron todos los miembros de la lista blanca de {ctx.guild.name}")
        await ctx.send(view=view)

 