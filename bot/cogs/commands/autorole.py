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
from utils.emoji import CROSS, ICONS_WARNING, TICK
import aiosqlite
import logging
from discord.ext import commands
from typing import List, Dict
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import OWNER_IDS



logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)

DATABASE_PATH = 'db/autorole.db'

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("¡Vaya! Ese mensaje no te pertenece.\nDebes ejecutar este comando para interactuar con él.", ephemeral=True)
            return False
        return True


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_table())
        self.color = 0xFF0000

    async def create_table(self):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS autorole (
                guild_id INTEGER PRIMARY KEY,
                bots TEXT NOT NULL,
                humans TEXT NOT NULL
            )
            """)
            await db.commit()

    async def get_autorole(self, guild_id: int) -> Dict[str, List[int]]:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT bots, humans FROM autorole WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    bots, humans = row
                    
                    bots = [int(role_id) for role_id in bots.replace('[', '').replace(']', '').replace(' ', '').split(',') if role_id]
                    humans = [int(role_id) for role_id in humans.replace('[', '').replace(']', '').replace(' ', '').split(',') if role_id]
                      
                    return {"bots": bots, "humans": humans}
                else:
                    return {"bots": [], "humans": []}

    

    async def update_autorole(self, guild_id: int, data: Dict[str, List[int]]):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            bots = ','.join(map(str, data['bots']))
            humans = ','.join(map(str, data['humans']))
            
            await db.execute("INSERT OR REPLACE INTO autorole (guild_id, bots, humans) VALUES (?, ?, ?)",
                             (guild_id, bots, humans))
            await db.commit()


        
                
    @commands.group(name="autorole", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            

    @_autorole.command(name="config", help="Muestra la configuración actual de autoroles")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _ar_config(self, ctx):
        
        data = await self.get_autorole(ctx.guild.id)
        if data:
            fetched_humans = [ctx.guild.get_role(role_id) for role_id in data["humans"] if ctx.guild.get_role(role_id)]
            fetched_bots = [ctx.guild.get_role(role_id) for role_id in data["bots"] if ctx.guild.get_role(role_id)]

            hums = "\n".join(role.mention for role in fetched_humans) or "Ninguno"
            bos = "\n".join(role.mention for role in fetched_bots) or "Ninguno"

            view = CV2(
                f"Configuración de autoroles de {ctx.guild.name}",
                f"__Humanos__\n{hums}",
                f"__Bots__\n{bos}"
            )
            await ctx.send(view=view)
        else:
            view = CV2("Configuración de autoroles", "No se encontró ninguna configuración de autoroles en este servidor.")
            await ctx.reply(view=view)



    @_autorole.group(name="reset", help="Borra la configuración de autoroles del servidor")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _autorole_reset(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_autorole_reset.command(name="humans", help="Borra la configuración de autoroles para humanos")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _autorole_humans_reset(self, ctx):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT humans FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()

        if data and data[0]:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("UPDATE autorole SET humans = ? WHERE guild_id = ?", ('[]', ctx.guild.id))
                await db.commit()
            view = CV2(f"{TICK} Éxito", "Se borraron todos los autoroles para humanos en este servidor.")
        else:
            view = CV2(f"{CROSS} Error", "No hay autoroles configurados para humanos en este servidor.")

        await ctx.reply(view=view)

    @_autorole_reset.command(name="bots", help="Borra la configuración de autoroles para bots")
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def _autorole_bots_reset(self, ctx):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT bots FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()

        if data and data[0]:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("UPDATE autorole SET bots = ? WHERE guild_id = ?", ('[]', ctx.guild.id))
                await db.commit()
            view = CV2(f"{TICK} Éxito", "Se borraron todos los autoroles para bots en este servidor.")
        else:
            view = CV2(f"{CROSS} Error", "No hay autoroles configurados para bots en este servidor.")

        await ctx.reply(view=view)

    @_autorole_reset.command(name="all", help="Borra toda la configuración de autoroles del servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_reset_all(self, ctx):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT humans, bots FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()

        if data and (data[0] or data[1]):
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("UPDATE autorole SET humans = ?, bots = ? WHERE guild_id = ?", ('[]', '[]', ctx.guild.id))
                await db.commit()
            view = CV2(f"{TICK} Éxito", "Se borraron todos los autoroles en este servidor.")
        else:
            view = CV2(f"{CROSS} Error", "No hay autoroles configurados en este servidor.")

        await ctx.reply(view=view)

    @_autorole.group(name="humans", help="Configura autoroles para humanos")
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_humans(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_autorole_humans.command(name="add", help="Añade un rol a la lista de autoroles para humanos.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_humans_add(self, ctx, *, role: discord.Role):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT humans FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()
        
        if data:
            humans = eval(data[0])
            if role.id in humans:
                view = CV2(f"{ICONS_WARNING} Acceso denegado", f"{role.mention} ya está en los autoroles para humanos.")
            elif len(humans) >= 10:
                view = CV2(f"{ICONS_WARNING} Acceso denegado", "Solo puedes añadir hasta 10 autoroles para humanos.")
            else:
                humans.append(role.id)
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("UPDATE autorole SET humans = ? WHERE guild_id = ?", (str(humans), ctx.guild.id))
                    await db.commit()
                view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido añadido a los autoroles para humanos.")
        else:
            humans = [role.id]
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("INSERT INTO autorole (guild_id, humans, bots) VALUES (?, ?, ?)", (ctx.guild.id, str(humans), '[]'))
                await db.commit()
            view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido añadido a los autoroles para humanos.")

        await ctx.reply(view=view)

    @_autorole_humans.command(name="remove", help="Quita un rol de los autoroles para humanos.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_humans_remove(self, ctx, *, role: discord.Role):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT humans FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()

        if data:
            humans = eval(data[0])
            if role.id not in humans:
                view = CV2(f"{CROSS} Error", f"{role.mention} no está en los autoroles para humanos.")
            else:
                humans.remove(role.id)
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("UPDATE autorole SET humans = ? WHERE guild_id = ?", (str(humans), ctx.guild.id))
                    await db.commit()
                view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido quitado de los autoroles para humanos.")
        else:
            view = CV2(f"{CROSS} Error", "No hay autoroles configurados para humanos en este servidor.")

        await ctx.reply(view=view)

    @_autorole.group(name="bots", help="Configura autoroles para bots")
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_bots(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_autorole_bots.command(name="add", help="Añade un rol a los autoroles para bots.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_bots_add(self, ctx, *, role: discord.Role):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT bots FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()
        
        if data:
            bots = eval(data[0])
            if role.id in bots:
                view = CV2(f"{ICONS_WARNING} Acceso denegado", f"{role.mention} ya está en los autoroles para bots.")
            elif len(bots) >= 10:
                view = CV2(f"{ICONS_WARNING} Acceso denegado", "Solo puedes añadir hasta 10 autoroles para bots")
            else:
                bots.append(role.id)
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("UPDATE autorole SET bots = ? WHERE guild_id = ?", (str(bots), ctx.guild.id))
                    await db.commit()
                view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido añadido a los autoroles para bots.")
        else:
            bots = [role.id]
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("INSERT INTO autorole (guild_id, humans, bots) VALUES (?, ?, ?)", (ctx.guild.id, '[]', str(bots)))
                await db.commit()
            view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido añadido a los autoroles para bots.")

        await ctx.reply(view=view)

    @_autorole_bots.command(name="remove", help="Quita un rol de los autoroles para bots.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _autorole_bots_remove(self, ctx, *, role: discord.Role):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT bots FROM autorole WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                data = await cursor.fetchone()

        if data:
            bots = eval(data[0])
            if role.id not in bots:
                view = CV2(f"{CROSS} Error", f"{role.mention} no está en los autoroles para bots.")
            else:
                bots.remove(role.id)
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("UPDATE autorole SET bots = ? WHERE guild_id = ?", (str(bots), ctx.guild.id))
                    await db.commit()
                view = CV2(f"{TICK} Éxito", f"{role.mention} ha sido quitado de los autoroles para bots.")
        else:
            view = CV2(f"{CROSS} Error", "No hay autoroles configurados para bots en este servidor.")

        await ctx.reply(view=view)
        

