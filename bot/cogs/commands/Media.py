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
import aiosqlite
from discord.ext import commands
from utils.Tools import blacklist_check, ignore_check
from collections import defaultdict
import time
from utils.cv2 import CV2

class Media(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.infractions = defaultdict(list)
        

    async def set_db(self):
        async with aiosqlite.connect('db/media.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS media_channels (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS media_bypass (
                    guild_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            await db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.set_db()

    @commands.hybrid_group(name="media", help="Configura el canal de medios; el canal de medios no permitirá a los usuarios enviar mensajes que no sean archivos multimedia.", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def media(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @media.command(name="setup", aliases=["set", "add"], help="Configura un canal exclusivo para multimedia en el servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, *, channel: discord.TextChannel):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    await ctx.reply(view=CV2("❌ Error", "Ya hay un canal de medios configurado. Elimínalo antes de configurar uno nuevo."))
                    return

            await db.execute('INSERT INTO media_channels (guild_id, channel_id) VALUES (?, ?)', (ctx.guild.id, channel.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Éxito", f"{channel.mention} se configuró correctamente como canal exclusivo para multimedia.\n\n*Asegúrate de darme el permiso \"Gestionar mensajes\" para que el canal de medios funcione.*"))

    @media.command(name="remove", aliases=["reset", "delete"], help="Elimina el canal exclusivo para multimedia actual")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", "No hay ningún canal exclusivo para multimedia configurado en este servidor."))
                    return

            await db.execute('DELETE FROM media_channels WHERE guild_id = ?', (ctx.guild.id,))
            await db.commit()

        await ctx.reply(view=CV2("✅ Éxito", "Se eliminó correctamente el canal exclusivo para multimedia."))

    @media.command(name="config", aliases=["settings", "show"], help="Muestra el canal exclusivo para multimedia configurado")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", "No hay ningún canal exclusivo para multimedia configurado en este servidor."))
                    return

        channel = self.client.get_channel(result[0])
        await ctx.reply(view=CV2("Canal exclusivo para multimedia", f"El canal exclusivo para multimedia configurado es {channel.mention}."))

    @media.group(name="bypass", help="Añade o quita usuarios de la lista de exentos del canal exclusivo para multimedia; los usuarios exentos pueden enviar mensajes en el canal de medios.", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @bypass.command(name="add", help="Añade un usuario a la lista de exentos")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_add(self, ctx, user: discord.Member):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT COUNT(*) FROM media_bypass WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                count = await cursor.fetchone()
                if count[0] >= 25:
                    await ctx.reply(view=CV2("❌ Error", "La lista de exentos solo puede tener hasta 25 usuarios."))
                    return

            async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
                if result:
                    await ctx.reply(view=CV2("❌ Error", f"{user.mention} ya está en la lista de exentos."))
                    return

            await db.execute('INSERT INTO media_bypass (guild_id, user_id) VALUES (?, ?)', (ctx.guild.id, user.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Éxito", f"{user.mention} se añadió a la lista de exentos."))

    @bypass.command(name="remove", help="Quita un usuario de la lista de exentos")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_remove(self, ctx, user: discord.Member):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    await ctx.reply(view=CV2("❌ Error", f"{user.mention} no está en la lista de exentos."))
                    return

            await db.execute('DELETE FROM media_bypass WHERE guild_id = ? AND user_id = ?', (ctx.guild.id, user.id))
            await db.commit()

        await ctx.reply(view=CV2("✅ Éxito", f"{user.mention} se quitó de la lista de exentos."))

    @bypass.command(name="show", aliases=["list", "view"], help="Muestra la lista de exentos")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bypass_show(self, ctx):
        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT user_id FROM media_bypass WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                result = await cursor.fetchall()
                if not result:
                    await ctx.reply(view=CV2("Lista de exentos", "No hay usuarios en la lista de exentos."))
                    return

        users = [self.client.get_user(user_id).mention for user_id, in result]
        user_mentions = "\n".join(users)

        await ctx.reply(view=CV2("Lista de exentos", user_mentions))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        async with aiosqlite.connect('db/media.db') as db:
            async with db.execute('SELECT channel_id FROM media_channels WHERE guild_id = ?', (message.guild.id,)) as cursor:
                media_channel = await cursor.fetchone()

        if media_channel and message.channel.id == media_channel[0]:
            async with aiosqlite.connect('db/block.db') as block_db:
                async with block_db.execute('SELECT 1 FROM user_blacklist WHERE user_id = ?', (message.author.id,)) as cursor:
                    blacklisted = await cursor.fetchone()

            async with aiosqlite.connect('db/media.db') as db:
                async with db.execute('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?', (message.guild.id, message.author.id)) as cursor:
                    bypassed = await cursor.fetchone()

            if blacklisted or bypassed:
                return

            if not message.attachments:
                try:
                    await message.delete()
                    msg = await message.channel.send(view=CV2("⚠️ Advertencia", f"{message.author.mention} Este canal está configurado solo para multimedia. Envía únicamente archivos multimedia."))
                    await msg.delete(delay=5)
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
                except Exception:
                    pass

                current_time = time.time()
                self.infractions[message.author.id].append(current_time)

                
                self.infractions[message.author.id] = [
                    infraction for infraction in self.infractions[message.author.id]
                    if current_time - infraction <= 5
                ]

                if len(self.infractions[message.author.id]) >= 5:  
                    async with aiosqlite.connect('db/block.db') as block_db:
                        await block_db.execute('INSERT OR IGNORE INTO user_blacklist (user_id) VALUES (?)', (message.author.id,))
                        
                        await block_db.commit()

                    desc = (
                        "⚠️ Has sido bloqueado para usar mis comandos por hacer spam en el canal de medios. "
                        "Si crees que es un error, contacta con el servidor de soporte y aporta pruebas."
                    )
                    await message.channel.send(f"{message.author.mention}", view=CV2("Has sido bloqueado", desc))
                    del self.infractions[message.author.id]

async def setup(bot):
    await bot.add_cog(Media(bot))
