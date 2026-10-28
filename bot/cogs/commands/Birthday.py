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
from discord.ext import commands, tasks
import json
import datetime
import asyncio
import os
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container

class CV2(LayoutView):
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for s in sections:
            if s:
                items.append(Separator(visible=True))
                items.append(TextDisplay(str(s)))
        self.add_item(build_container(*items))

def read_db(filename):
    """Read the JSON database file."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def write_db(filename, data):
    """Write data to the JSON database file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

class Birthdays(commands.Cog):
    """Gestiona las notificaciones y la configuración de cumpleaños."""

    def __init__(self, client: commands.Bot):
        self.client = client
        self.check_birthdays.start()

    @commands.command(
        name="birthdaysetup",
        help="Configura el canal de registro de cumpleaños y el rol.")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def birthday_setup(self, ctx: commands.Context, channel: discord.TextChannel, role: discord.Role):
        db = read_db('jsondb/birthday_logs.json')
        guild_id = str(ctx.guild.id)
        
        if guild_id not in db:
            db[guild_id] = {"birthday_channel_id": channel.id, "birthday_role_id": role.id}
        else:
            db[guild_id]["birthday_channel_id"] = channel.id
            db[guild_id]["birthday_role_id"] = role.id
        
        write_db('jsondb/birthday_logs.json', db)
        
        await ctx.send(view=CV2("Configuración de cumpleaños", f"Canal de registro de cumpleaños establecido en {channel.mention} y rol de cumpleaños establecido en {role.mention}."))

    @commands.command(
        name="setbirthday",
        help="Establece tu cumpleaños.")
    @commands.guild_only()
    async def set_birthday(self, ctx: commands.Context):
        def check(msg):
            return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

        await ctx.send(view=CV2("Configuración de cumpleaños", "Por favor, ingresa el día de tu nacimiento (DD):"))

        try:
            msg = await self.client.wait_for('message', timeout=60.0, check=check)
            day = msg.content.strip().zfill(2)
            
            if not day.isdigit() or int(day) not in range(1, 32):
                await ctx.send(view=CV2("Error", "Día inválido. Ingresa un número entre 01 y 31."))
                return

            await ctx.send(view=CV2("Configuración de cumpleaños", "Por favor, ingresa el mes de tu nacimiento (MM):"))
            msg = await self.client.wait_for('message', timeout=60.0, check=check)
            month = msg.content.strip().zfill(2)
            
            if not month.isdigit() or int(month) not in range(1, 13):
                await ctx.send(view=CV2("Error", "Mes inválido. Ingresa un número entre 01 y 12."))
                return

            await ctx.send(view=CV2("Configuración de cumpleaños", "Por favor, ingresa el año de tu nacimiento (AAAA):"))
            msg = await self.client.wait_for('message', timeout=60.0, check=check)
            year = msg.content.strip()
            
            if not year.isdigit() or len(year) != 4:
                await ctx.send(view=CV2("Error", "Año inválido. Ingresa un año válido en formato AAAA."))
                return

            date = f"{month}-{day}-{year}"
            db = read_db('jsondb/birthdays.json')
            db[str(ctx.author.id)] = date
            write_db('jsondb/birthdays.json', db)
            
            await ctx.send(view=CV2("Éxito", f"Tu cumpleaños se ha establecido el {date}."))
        except asyncio.TimeoutError:
            await ctx.send(view=CV2("Error", "Tardaste demasiado en responder. Inténtalo de nuevo."))

    @commands.command(
        name="removebirthday",
        help="Elimina tu cumpleaños.")
    @commands.guild_only()
    async def remove_birthday(self, ctx: commands.Context):
        db = read_db('jsondb/birthdays.json')
        
        if str(ctx.author.id) in db:
            del db[str(ctx.author.id)]
            write_db('jsondb/birthdays.json', db)
            await ctx.send(view=CV2("Éxito", "Tu cumpleaños ha sido eliminado."))
        else:
            await ctx.send(view=CV2("Error", "No tienes un cumpleaños establecido."))

    @commands.command(
        name="listbirthdays",
        help="Muestra todos los miembros que cumplen años hoy.")
    @commands.guild_only()
    async def list_birthdays(self, ctx: commands.Context):
        now = datetime.datetime.now()
        today_date = now.strftime("%m-%d")
        db = read_db('jsondb/birthdays.json')

        members_with_birthday = [ctx.guild.get_member(int(user_id)) for user_id, date in db.items() if date.startswith(today_date)]

        if members_with_birthday:
            mentions = ', '.join(member.mention for member in members_with_birthday if member)
            await ctx.send(view=CV2("Cumpleaños de hoy", f"Miembros que cumplen años hoy: {mentions}"))
        else:
            await ctx.send(view=CV2("Cumpleaños", "No hay cumpleaños hoy."))

    @commands.command(
        name="birthday",
        help="Consulta tu cumpleaños.")
    @commands.guild_only()
    async def check_birthday(self, ctx: commands.Context):
        db = read_db('jsondb/birthdays.json')
        
        if str(ctx.author.id) in db:
            date = db[str(ctx.author.id)]
            await ctx.send(view=CV2("Tu cumpleaños", f"Tu cumpleaños está establecido el {date}."))
        else:
            await ctx.send(view=CV2("Tu cumpleaños", "Aún no has establecido tu cumpleaños."))

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        now = datetime.datetime.now()
        today_date = now.strftime("%m-%d")
        db = read_db('jsondb/birthdays.json')
        guild_settings = read_db('jsondb/birthday_logs.json')

        for user_id, birthday in db.items():
            if birthday.startswith(today_date):
                user = self.client.get_user(int(user_id))
                if user:
                    for guild_id, settings in guild_settings.items():
                        channel_id = settings.get("birthday_channel_id")
                        role_id = settings.get("birthday_role_id")
                        if channel_id:
                            channel = self.client.get_channel(channel_id)
                            if channel:
                                await channel.send(view=CV2("¡Feliz cumpleaños! 🎉", f"¡Le deseamos a {user.mention} un cumpleaños fantástico!"))
                                role = discord.utils.get(channel.guild.roles, id=role_id)
                                if role:
                                    await user.add_roles(role)
                                break

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.client.wait_until_ready()
        now = datetime.datetime.now()
        first_run = datetime.datetime.combine(now.date(), datetime.time(hour=0, minute=0))
        if now > first_run:
            first_run += datetime.timedelta(days=1)
        await asyncio.sleep((first_run - now).total_seconds())

async def setup(client: commands.Bot):
    await client.add_cog(Birthdays(client))
