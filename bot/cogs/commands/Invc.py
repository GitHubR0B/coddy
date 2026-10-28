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
from discord.ext import commands
import aiosqlite
import asyncio
from utils.Tools import *
from utils.cv2 import CV2
from utils.config import *

class Invcrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'db/invc.db'
        self.bot.loop.create_task(self.create_table())

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS vcroles (
                    guild_id INTEGER PRIMARY KEY,
                    role_id INTEGER NOT NULL
                )
            ''')
            await db.commit()

    @commands.group(name='vcrole', help="Comandos de configuración de Vcrole", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def vcrole(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @vcrole.command(name='add', help="Añade un rol a la lista de vcrole")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT role_id FROM vcroles WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    await ctx.reply(view=CV2("⚠️ Acceso denegado", f"El rol de VC ya está configurado en este servidor con el rol {ctx.guild.get_role(row[0]).mention}.\nPor favor, **elimínalo** para añadir otro."))
                    return
            await db.execute('INSERT INTO vcroles (guild_id, role_id) VALUES (?, ?)', (ctx.guild.id, role.id))
            await db.commit()
            await ctx.reply(view=CV2("✅ Éxito", f"Rol de VC {role.mention} añadido para este servidor."))

    @vcrole.command(name='remove', aliases=["reset"], help="Elimina el rol de la lista de vcrole")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, role: discord.Role):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT role_id FROM vcroles WHERE guild_id = ? AND role_id = ?', (ctx.guild.id, role.id)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await ctx.send(view=CV2("❌ Error", "El rol indicado no está configurado como rol de VC."))
                    return
            await db.execute('DELETE FROM vcroles WHERE guild_id = ? AND role_id = ?', (ctx.guild.id, role.id))
            await db.commit()
            await ctx.send(view=CV2("✅ Éxito", f"Rol de VC {role.mention} eliminado de este servidor."))

    @vcrole.command(name='config', aliases=['view', 'show'], help="Muestra el vcrole actual en este servidor")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT role_id FROM vcroles WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await ctx.send(view=CV2("❌ Error", "El rol de VC no está configurado en este servidor."))
                    return
                role = ctx.guild.get_role(row[0])
                await ctx.send(view=CV2("Configuración del rol de VC", f"El rol de VC actual en este servidor es {role.mention}.\n\n*Asegúrate de colocar mi rol por encima del rol de VC*"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT role_id FROM vcroles WHERE guild_id = ?', (member.guild.id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return
                    role = member.guild.get_role(row[0])

                    if after.channel and role not in member.roles:
                        await self.add_role_with_retry(member, role, reason=f"Miembro se unió a un canal de voz | {BRAND_NAME} Invcrole")
                    elif not after.channel and role in member.roles:
                        await self.remove_role_with_retry(member, role, reason=f"Miembro salió de un canal de voz | {BRAND_NAME} Invcrole")
        except discord.Forbidden:
            print(f"Bot lacks permissions to maange role in a guild during Invc Event .")
        except Exception as e:
            print(f"Error in on_voice_state_update: {e}")

    async def add_role_with_retry(self, member, role, reason, retries=5):
        attempt = 0
        while attempt < retries:
            try:
                await member.add_roles(role, reason=reason)
                break
            except discord.errors.RateLimited as e:
                retry_after = e.retry_after if hasattr(e, 'retry_after') else 1
                await asyncio.sleep(retry_after)
            except discord.HTTPException as e:
                print(f"Error adding role: {e}")
                break
            attempt += 1

    async def remove_role_with_retry(self, member, role, reason, retries=5):
        attempt = 0
        while attempt < retries:
            try:
                await member.remove_roles(role, reason=reason)
                break
            except discord.errors.RateLimited as e:
                retry_after = e.retry_after if hasattr(e, 'retry_after') else 1
                await asyncio.sleep(retry_after)
            except discord.HTTPException as e:
                print(f"Error removing role: {e}")
                break
            attempt += 1

async def setup(bot):
    await bot.add_cog(Invcrole(bot))
