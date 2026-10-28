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
from utils.emoji import CROSS, TICK, ZWARNING
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import aiosqlite
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from typing import List, Tuple
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.config import *



DATABASE_PATH = 'db/customrole.db'
DATABASE_PATH2 = 'db/np.db'


class Customrole(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cooldown = {}
        self.rate_limit = {}
        self.rate_limit_timeout = 5


        self.bot.loop.create_task(self.create_tables())


    async def reset_rate_limit(self, user_id):
        await asyncio.sleep(self.rate_limit_timeout)
        self.rate_limit.pop(user_id, None)
        



    async def add_role(self, *, role_id: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=role_id)
            await member.add_roles(role, reason=f"{BRAND_NAME} Customrole | Rol añadido")
        else:
            raise discord.Forbidden("El bot no tiene permiso para gestionar roles.")



    async def remove_role(self, *, role_id: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=role_id)
            await member.remove_roles(role, reason=f"{BRAND_NAME} Customrole | Rol quitado")
        else:
            raise discord.Forbidden("El bot no tiene permiso para gestionar roles.")
            


    async def add_role2(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.add_roles(role, reason=f"{BRAND_NAME} Customrole | Rol añadido")

    async def remove_role2(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.remove_roles(role, reason=f"{BRAND_NAME} Customrole| Rol quitado")

    

    async def handle_role_command(self, context: Context, member: discord.Member, role_type: str):
        async with aiosqlite.connect('db/customrole.db') as db:
            async with db.execute(f"SELECT reqrole, {role_type} FROM roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                data = await cursor.fetchone()
                if data:
                    reqrole_id, role_id = data
                    reqrole = context.guild.get_role(reqrole_id)
                    role = context.guild.get_role(role_id)

                    if reqrole:
                        if context.author == context.guild.owner or reqrole in context.author.roles:
                            if role:
                                if role not in member.roles:
                                    await self.add_role2(role=role_id, member=member)
                                    await context.reply(view=CV2(f"{TICK} Éxito", f"**Otorgado** <@&{role.id}> a {member.mention}"))
                                else:
                                    await self.remove_role2(role=role_id, member=member)
                                    await context.reply(view=CV2(f"{TICK} Éxito", f"**Quitado** <@&{role.id}> de {member.mention}"))
                            else:
                                await context.reply(view=CV2(f"{CROSS} Error", f"El rol {role_type.capitalize()} no está configurado en {context.guild.name}"))
                        else:
                            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", f"Necesitas {reqrole.mention} para ejecutar este comando."))
                    else:
                        await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", f"El rol requerido no está configurado en {context.guild.name}"))
                else:
                    await context.reply(view=CV2(f"{CROSS} Error", f"La configuración de roles no está establecida en {context.guild.name}"))

    


    async def create_tables(self):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    guild_id INTEGER PRIMARY KEY,
                    staff INTEGER,
                    girl INTEGER,
                    vip INTEGER,
                    guest INTEGER,
                    frnd INTEGER,
                    reqrole INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS custom_roles (
                    guild_id INTEGER,
                    name TEXT,
                    role_id INTEGER,
                    PRIMARY KEY (guild_id, name)
                )
            ''')
            await db.commit()

    
    @commands.hybrid_group(name="setup",
                           description="Configura los roles personalizados del servidor.",
                           help="Configura los roles personalizados del servidor.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set(self, context: Context):
        if context.subcommand_passed is None:
            await context.send_help(context.command)
            context.command.reset_cooldown(context)

    async def fetch_role_data(self, guild_id):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT staff, girl, vip, guest, frnd, reqrole FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()




    async def update_role_data(self, guild_id, column, value):
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute(f"INSERT OR REPLACE INTO roles (guild_id, {column}) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET {column} = ?",
                                 (guild_id, value, value))
                await db.commit()
        except Exception as e:
            print(f"Error updating role data: {e}")
            

    async def fetch_custom_role_data(self, guild_id):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT name, role_id FROM custom_roles WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchall()


    @set.command(name="staff",
                 description="Configura el rol de Staff en el servidor",
                 help="Configura el rol de Staff en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def staff(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'staff', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} al rol `Staff`\n\n__**¿Cómo usarlo?**__\nUsa el comando `staff <usuario>` para **añadir el rol {role.mention}** al usuario y úsalo de nuevo con el mismo usuario para **quitarle el rol**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    @set.command(name="girl",
                 description="Configura el rol de Girl en el servidor",
                 help="Configura el rol de Girl en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def girl(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'girl', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} al rol `Girl`\n\n__**¿Cómo usarlo?**__\nUsa el comando `girl <usuario>` para **añadir el rol {role.mention}** al usuario y úsalo de nuevo con el mismo usuario para **quitarle el rol**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    @set.command(name="vip",
                 description="Configura el rol VIP en el servidor",
                 help="Configura el rol VIP en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def vip(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'vip', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} al rol `VIP`\n\n__**¿Cómo usarlo?**__\nUsa el comando `vip <usuario>` para **añadir el rol {role.mention}** al usuario y úsalo de nuevo con el mismo usuario para **quitarle el rol**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    @set.command(name="guest",
                 description="Configura el rol de Guest en el servidor",
                 help="Configura el rol de Guest en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def guest(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'guest', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} al rol `Guest`\n\n__**¿Cómo usarlo?**__\nUsa el comando `guest <usuario>` para **añadir el rol {role.mention}** al usuario y úsalo de nuevo con el mismo usuario para **quitarle el rol**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    @set.command(name="friend",
                 description="Configura el rol de Friend en el servidor",
                 help="Configura el rol de Friend en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def friend(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'frnd', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} al rol `Friend`\n\n__**¿Cómo usarlo?**__\nUsa el comando `friend <usuario>` para **añadir el rol {role.mention}** al usuario y úsalo de nuevo con el mismo usuario para **quitarle el rol**."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    @set.command(name="reqrole",
                 description="Configura el rol requerido para los comandos de roles personalizados",
                 help="Configura el rol requerido para los comandos de roles personalizados")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="Rol que se añadirá")
    async def req_role(self, context: Context, role: discord.Role) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            await self.update_role_data(context.guild.id, 'reqrole', role.id)
            await context.reply(view=CV2(f"{TICK} Éxito", f"Añadido {role.mention} como rol requerido para ejecutar los comandos de roles personalizados en {context.guild.name}"))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

    

    @set.command(name="config",
                 description="Muestra la configuración actual de roles personalizados en el servidor.",
                 help="Muestra la configuración actual de roles personalizados en el servidor.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def config(self, context: Context) -> None:
        role_data = await self.fetch_role_data(context.guild.id)
        if role_data:
            staff = context.guild.get_role(role_data[0]).mention if role_data[0] else "Ninguno"
            girl = context.guild.get_role(role_data[1]).mention if role_data[1] else "Ninguno"
            vip = context.guild.get_role(role_data[2]).mention if role_data[2] else "Ninguno"
            guest = context.guild.get_role(role_data[3]).mention if role_data[3] else "Ninguno"
            friend = context.guild.get_role(role_data[4]).mention if role_data[4] else "Ninguno"
            reqrole = context.guild.get_role(role_data[5]).mention if role_data[5] else "Ninguno"
            config_text = (
                f"**Rol Staff:** {staff}\n"
                f"**Rol Girl:** {girl}\n"
                f"**Rol VIP:** {vip}\n"
                f"**Rol Guest:** {guest}\n"
                f"**Rol Friend:** {friend}\n"
                f"**Rol requerido:** {reqrole}\n\n"
                "Usa los comandos para asignar el rol y úsalos de nuevo con el mismo usuario para quitarlo."
            )
            await context.reply(view=CV2("Configuración de roles personalizados", config_text))
        else:
            await context.reply(view=CV2(f"{CROSS} Error", "No se encontró ninguna configuración de roles personalizados en este servidor."))



            


    @set.command(name="create",
                 description="Crea un comando de rol personalizado.",
                 help="Crea un comando de rol personalizado")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(name="Nombre del comando", role="Rol que se asignará")
    async def create(self, context: Context, name: str, role: discord.Role) -> None:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT COUNT(*) FROM custom_roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                count = await cursor.fetchone()
                if count[0] >= 56:
                    await context.reply(view=CV2(f"{ZWARNING} Límite alcanzado", "Has alcanzado el límite máximo de 56 comandos de rol personalizados en este servidor."))
                    return

            async with db.execute("SELECT name FROM custom_roles WHERE guild_id = ?", (context.guild.id,)) as cursor:
                existing_role = await cursor.fetchall()
                if any(name == row[0] for row in existing_role):
                    await context.reply(view=CV2(f"{CROSS} Error", f"Ya existe un comando de rol personalizado con el nombre `{name}` en este servidor. Elimínalo antes de crear uno nuevo."))
                    return

            await db.execute("INSERT INTO custom_roles (guild_id, name, role_id) VALUES (?, ?, ?)",
                             (context.guild.id, name, role.id))
            await db.commit()

        await context.reply(view=CV2(f"{TICK} Éxito", f"Comando de rol personalizado `{name}` creado para asignar el rol {role.mention}.\n\n__**¿Cómo usarlo?**__\nUsa el comando `{name} <usuario>` para asignar o quitar el rol {role.mention} al usuario.\n> Esto funcionará para los usuarios con permisos de `Gestionar roles`."))
        

    @set.command(name="delete", aliases=["remove"],
                 description="Elimina un comando de rol personalizado.",
                 help="Elimina un comando de rol personalizado.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(name="Nombre del comando que se eliminará")
    async def delete(self, context: Context, name: str) -> None:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT name FROM custom_roles WHERE guild_id = ? AND name = ?", (context.guild.id, name)) as cursor:
                existing_role = await cursor.fetchone()

        if not existing_role:
            await context.reply(view=CV2(f"{CROSS} Error", f"No se encontró ningún comando de rol personalizado con el nombre `{name}` en este servidor."))
            return

        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("DELETE FROM custom_roles WHERE guild_id = ? AND name = ?", (context.guild.id, name))
            await db.commit()

        await context.reply(view=CV2(f"{TICK} Éxito", f"El comando de rol personalizado `{name}` ha sido eliminado."))
        

    @set.command(
        name="list",
        description="Muestra todos los roles personalizados configurados en el servidor.",
        help="Muestra todos los roles personalizados configurados en el servidor."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def list(self, context: Context) -> None:
        custom_roles = await self.fetch_custom_role_data(context.guild.id)

        if not custom_roles:
            await context.reply(view=CV2(f"{CROSS} Error", "No se han creado roles personalizados en este servidor."))
            return

        
        def chunk_list(data: List[Tuple[str, int]], chunk_size: int):
            """Yield successive chunks of `chunk_size` from `data`."""
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]

        
        chunks = list(chunk_list(custom_roles, 7))

        for i, chunk in enumerate(chunks):
            roles_text = ""
            for name, role_id in chunk:
                role = context.guild.get_role(role_id)
                if role:
                    roles_text += f"**{name}** → {role.mention}\n"
            footer = f"Página {i+1}/{len(chunks)} | Estos comandos pueden usarlos los miembros con permisos de Gestionar roles."
            await context.reply(view=CV2("Roles personalizados", roles_text, footer))


    @set.command(name="reset",
         description="Restablece la configuración de roles personalizados del servidor.",
         help="Restablece la configuración de roles personalizados del servidor.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def reset(self, context: Context) -> None:
        if context.author == context.guild.owner or context.author.top_role.position > context.guild.me.top_role.position:
            removed_roles = []
            role_data = await self.fetch_role_data(context.guild.id)
            if role_data:
                roles = ["staff", "girl", "vip", "guest", "frnd", "reqrole"]
                for i, role_name in enumerate(roles):
                    role_id = role_data[i]
                    if role_id:
                        role = context.guild.get_role(role_id)
                        if role:
                            removed_roles.append(f"**{role_name.capitalize()}:** {role.mention}")
                            await self.update_role_data(context.guild.id, role_name, None)
                            
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("DELETE FROM custom_roles WHERE guild_id = ?", (context.guild.id,))
                    await db.commit()
                    reset_desc = f"Se eliminaron todos los comandos de rol personalizado {TICK}\n\n**Roles eliminados:**\n" + "\n".join(removed_roles) if removed_roles else "No había roles configurados previamente."
                    await context.reply(view=CV2("Configuración de roles personalizados restablecida", reset_desc))
            else:
                await context.reply(view=CV2("Información", "No se encontró ninguna configuración en este servidor."))
        else:
            await context.reply(view=CV2(f"{ZWARNING} Acceso denegado", "Tu rol debe estar por encima de mi rol más alto."))

        
            

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot or not message.content:
            return

        prefixes = await self.bot.get_prefix(message)

        
        if not prefixes:
            return

        
        if not any(message.content.startswith(prefix) for prefix in prefixes):
            return

        
        for prefix in prefixes:
            if message.content.startswith(prefix):
                command_name = message.content[len(prefix):].split()[0] 
                break
        else:
            return

        guild_id = message.guild.id

        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT role_id FROM custom_roles WHERE guild_id = ? AND name = ?", (guild_id, command_name)) as cursor:
                result = await cursor.fetchone()

        if result:
            role_id = result[0]
            role = message.guild.get_role(role_id)

            
            async with aiosqlite.connect(DATABASE_PATH) as db:
                async with db.execute("SELECT reqrole FROM roles WHERE guild_id = ?", (guild_id,)) as cursor:
                    reqrole_result = await cursor.fetchone()

            reqrole_id = reqrole_result[0] if reqrole_result else None
            reqrole = message.guild.get_role(reqrole_id) if reqrole_id else None

            
            if reqrole is None:
                await message.channel.send(f"{ZWARNING} El rol requerido no está configurado en este servidor. Configúralo usando `setup reqrole`.")
                return

            
            if reqrole not in message.author.roles:
                await message.channel.send(view=CV2(f"{ZWARNING} Acceso denegado", f"Necesitas el rol {reqrole.mention} para usar este comando."))
                return

            
            member = message.mentions[0] if message.mentions else None
            if not member:
                await message.channel.send("Menciona a un usuario para asignarle el rol.")
                return

            
            now = asyncio.get_event_loop().time()
            if guild_id not in self.cooldown or now - self.cooldown[guild_id] >= 10:
                self.cooldown[guild_id] = now
            else:
                await message.channel.send("Tienes un tiempo de espera de 5 segundos. Espera antes de enviar otro comando.", delete_after=5)
                return

            try:
                if role in member.roles:
                    await self.remove_role(role_id=role_id, member=member)
                    await message.channel.send(view=CV2(f"{TICK} Éxito", f"**Quitado** el rol {role.mention} a {member.mention}."))
                else:
                    await self.add_role(role_id=role_id, member=member)
                    await message.channel.send(view=CV2(f"{TICK} Éxito", f"**Añadido** el rol {role.mention} a {member.mention}."))
            except discord.Forbidden as e:
                await message.channel.send("No tengo permiso para gestionar este rol para el usuario indicado.")
                print(f"Error: {e}")
        else:
            return

    

    @commands.hybrid_command(name="staff",
         description="Otorga el rol de Staff al usuario.",
         aliases=['official'],
         help="Otorga el rol de Staff al usuario.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _staff(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'staff')

    @commands.hybrid_command(name="girl",
         description="Otorga el rol de Girl al usuario.",
         aliases=['qt'],
         help="Otorga el rol de Girl al usuario.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _girl(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'girl')

    @commands.hybrid_command(name="vip",
         description="Otorga el rol VIP al usuario.",
         help="Otorga el rol VIP al usuario.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _vip(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'vip')

    @commands.hybrid_command(name="guest",
         description="Otorga el rol de Guest al usuario.",
         help="Otorga el rol de Guest al usuario.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _guest(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'guest')

    @commands.hybrid_command(name="friend",
         description="Otorga el rol de Friend al usuario.",
         aliases=['frnd'],
         help="Otorga el rol de Friend al usuario.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    #@commands.has_permissions(manage_roles=True)
    async def _friend(self, context: Context, member: discord.Member) -> None:
        await self.handle_role_command(context, member, 'frnd')


 