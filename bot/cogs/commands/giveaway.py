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
import datetime, pytz, time as t
from discord.ui import Button, Select, View
import aiosqlite, random, typing
import sqlite3
import asyncio
import discord, logging
from utils.emoji import ARROWRED, TADAA, TICK
from discord.utils import get
from utils.Tools import *
import os
import aiohttp
from utils.cv2 import CV2

db_folder = 'db'
db_file = 'giveaways.db'
db_path = os.path.join(db_folder, db_file)
connection = sqlite3.connect(db_path)

cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Giveaway (
                    guild_id INTEGER,
                    host_id INTEGER,
                    start_time TIMESTAMP,
                    ends_at TIMESTAMP,
                    prize TEXT,
                    winners INTEGER,
                    message_id INTEGER,
                    channel_id INTEGER,
                    PRIMARY KEY (guild_id, message_id)
                )''')

connection.commit()
connection.close()

def convert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 86400 , "f" : 259200}
    unit = time[-1]
    if unit not in pos:
        return
    try:
        val = int(time[:-1])
    except ValueError:
        return
    return val * time_dict[unit]

def WinnerConverter(winner):
    try:
        int(winner)
    except ValueError:
        try:
           return int(winner[:-1])
        except:
            return -4
    return winner

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.connection = await aiosqlite.connect(db_path)
        self.cursor = await self.connection.cursor()
        await self.check_for_ended_giveaways() 
        self.GiveawayEnd.start()

    async def cog_unload(self) -> None:
        await self.connection.close()

    async def check_for_ended_giveaways(self):
        await self.cursor.execute("SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE ends_at <= ?", (datetime.datetime.now().timestamp(),))
        ended_giveaways = await self.cursor.fetchall()
        for giveaway in ended_giveaways:
            await self.end_giveaway(giveaway)

    async def end_giveaway(self, giveaway):
        try:
            current_time = datetime.datetime.now().timestamp()
            guild = self.bot.get_guild(int(giveaway[1]))
            if guild is None:
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
                await self.connection.commit()
                return

            channel = self.bot.get_channel(int(giveaway[6]))
            if channel is not None:
                try:
                    retries = 3
                    for attempt in range(retries):
                        try:
                            message = await channel.fetch_message(int(giveaway[2]))
                            break
                        except discord.NotFound:
                            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
                            await self.connection.commit()
                            return
                        except aiohttp.ClientResponseError as e:
                            if e.status == 503:
                                if attempt < retries - 1:
                                    await asyncio.sleep(2 ** attempt)
                                    continue
                                else:
                                    raise
                            else:
                                raise

                    users = [i.id async for i in message.reactions[0].users()]
                    if self.bot.user.id in users:
                        users.remove(self.bot.user.id)

                    if len(users) < 1:
                        await message.reply(f"Nadie ganó el sorteo de **{giveaway[5]}** porque no hubo suficientes participantes.")
                        await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                        await self.connection.commit()
                        return

                    winners_count = min(len(users), int(giveaway[4]))
                    winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=winners_count))

                    desc = f"Finalizó <t:{int(current_time)}:R>\nOrganizado por <@{int(giveaway[3])}>\nGanador(es): {winner}"
                    view = CV2(f"{giveaway[5]}", desc)

                    await message.edit(content=f"{TADAA} **SORTEO FINALIZADO** {TADAA}", view=view)
                    await message.reply(f"{TADAA} ¡Felicidades {winner}, ganaste **{giveaway[5]}!**, organizado por <@{int(giveaway[3])}>")
                    await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                    await self.connection.commit()

                except (discord.HTTPException, aiohttp.ClientResponseError) as e:
                    logging.error(f"Error ending giveaway: {e}")

        except IndexError:
            logging.error(f"Giveaway data is corrupted or missing: {giveaway}")
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
            await self.connection.commit()

    @tasks.loop(seconds=5)
    async def GiveawayEnd(self):
        await self.cursor.execute("SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE ends_at <= ?", (datetime.datetime.now().timestamp(),))
        ends_raw = await self.cursor.fetchall()
        for giveaway in ends_raw:
            await self.end_giveaway(giveaway)




    @commands.hybrid_command(description="Inicia un nuevo sorteo.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def gstart(self, ctx,
                      time,
                      winners: int,
                      *,
                      prize: str):

        await self.cursor.execute("SELECT message_id, channel_id FROM Giveaway WHERE guild_id = ?", (ctx.guild.id,))
        re = await self.cursor.fetchall()

        if winners >=  15:
            message = await ctx.send(view=CV2("⚠️ Acceso denegado", "No se puede superar los 15 ganadores."))
            await asyncio.sleep(5)
            await message.delete()
            return

        g_list = [i[0] for i in re]
        if len(g_list) >= 5:
            message = await ctx.send(view=CV2("⚠️ Acceso denegado", "Solo puedes organizar hasta 5 sorteos en este servidor."))
            await asyncio.sleep(5)
            await message.delete()
            return

        converted = self.convert(time)
        if converted / 60 >= 50400:
            message = await ctx.send(view=CV2("⚠️ Acceso denegado", "¡El tiempo no puede superar los 31 días!"))
            await asyncio.sleep(5)
            await message.delete()
            return

        if converted == -1:
            message = await ctx.send(view=CV2("❌ Error", "Formato de tiempo inválido"))
            await asyncio.sleep(5)
            await message.delete()
            return
        if converted == -2:
            message = await ctx.send(view=CV2("❌ Error", "Formato de tiempo inválido. Proporciona el tiempo en números."))
            await asyncio.sleep(5)
            await message.delete()
            return

        ends = (datetime.datetime.now().timestamp() + converted)

        desc = (
            f"{ARROWRED} Ganador(es): **{winners}**\n"
            f"{ARROWRED} Organizado por {ctx.author.mention}\n"
            f"{ARROWRED} Finaliza <t:{round(ends)}:R> (<t:{round(ends)}:f>)\n\n"
            f"{ARROWRED} ¡Reacciona con {TADAA} para participar!"
        )
        
        view = CV2(f"{TADAA} {prize}", desc)

        message = await ctx.send(f"{TADAA} **SORTEO** {TADAA}", view=view)
        try:
           await ctx.message.delete()
        except:
            pass

        await self.cursor.execute("INSERT INTO Giveaway(guild_id, host_id, start_time, ends_at, prize, winners, message_id, channel_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, ctx.author.id, datetime.datetime.now(), ends, prize, winners, message.id, ctx.channel.id))

        await message.add_reaction(TADAA)
        await self.connection.commit()

    
                                    

    @commands.Cog.listener("on_message_delete")
    async def GiveawayMessageDelete(self, message):
        await self.cursor.execute("SELECT message_id FROM Giveaway WHERE guild_id = ?", (message.guild.id,))
        re = await self.cursor.fetchone()

        if message.author != self.bot.user:
            return

        if re is not None:
            if message.id == int(re[0]):
                await self.cursor.execute("DELETE FROM Giveaway WHERE channel_id = ? AND message_id = ? AND guild_id = ?", (message.channel.id, message.id, message.guild.id))

                print(f"Giveaway message deleted in {message.guild.name} - {message.guild.id}")
                await self.connection.commit()

    @commands.hybrid_command(name="gend", description="Finaliza un sorteo antes de su hora de cierre.", help="Finaliza un sorteo antes de su hora de cierre.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def gend(self, ctx, message_id = None):
        if message_id:
            try:
                int(message_id)
            except ValueError:
                message = await ctx.send(view=CV2("⚠️ Acceso denegado", "El ID de mensaje proporcionado no es válido."))
                await asyncio.sleep(5)
                await message.delete()
                return

        if message_id is not None:
            current_time = datetime.datetime.now().timestamp()
            await self.cursor.execute('SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE message_id = ?', (int(message_id),))
            re = await self.cursor.fetchone()

            if re is None:
                message = await ctx.send(view=CV2("❌ Error", "No se encontró el sorteo."))
                await asyncio.sleep(5)
                await message.delete()
                return

            ch = self.bot.get_channel(int(re[6]))
            message = await ch.fetch_message(int(message_id))

            users = [i.id async for i in message.reactions[0].users()]
            users.remove(self.bot.user.id)

            if len(users) < 1:
                await ctx.send(f"{TICK} Sorteo finalizado correctamente en <#{int(re[6])}>")
                await message.reply(f"Nadie ganó el sorteo de **{re[5]}** porque no hubo suficientes participantes.")
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                return

            winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=int(re[4])))

            desc = f"Finalizó <t:{int(current_time)}:R>\nOrganizado por <@{int(re[3])}>\nGanador(es): {winner}"
            view = CV2(f"🎁 {re[5]}", desc)

            await message.edit(content="🎁 **SORTEO FINALIZADO** 🎁", view=view)

            if int(ctx.channel.id) != int(re[6]):
                await ctx.send(f"{TADAA} Sorteo finalizado correctamente en <#{int(re[6])}>")

            await message.reply(f" ¡Felicidades {winner}, ganaste **{re[5]}!**, organizado por <@{int(re[3])}>")
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))

        elif ctx.message.reference:
            await self.cursor.execute('SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE message_id = ?', (ctx.message.reference.resolved.id,))
            re = await self.cursor.fetchone()

            if re is None:
                return await ctx.send(f"No se encontró el sorteo.")

            current_time = datetime.datetime.now().timestamp()

            message = await ctx.fetch_message(ctx.message.reference.message_id)

            users = [i.id async for i in message.reactions[0].users()]
            try: users.remove(self.bot.user.id)
            except: pass

            if len(users) < 1:
                await message.reply(f"Nadie ganó el sorteo de **{re[5]}** porque no hubo suficientes participantes.")
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                return

            winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=int(re[4])))

            desc = f"Finalizó <t:{int(current_time)}:R>\nOrganizado por <@{int(re[3])}>\nGanador(es): {winner}"
            view = CV2(f"🎁 {re[5]}", desc)

            await message.edit(content="🎁 **SORTEO FINALIZADO** 🎁", view=view)

            await message.reply(f"💐 ¡Felicidades {winner}, ganaste **{re[5]}!**, organizado por <@{int(re[3])}>")
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))

        else:
            await ctx.send("Responde al mensaje del sorteo o proporciona el ID del sorteo.")
        await self.connection.commit()

    @commands.hybrid_command(description="Vuelve a sortear un ganador respondiendo al mensaje del sorteo.", help="Vuelve a sortear un ganador respondiendo al mensaje del sorteo.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def greroll(self, ctx, message_id: typing.Optional[int] = None):
        if not ctx.message.reference:
            message = await ctx.reply("Responde a este comando con el mensaje de Sorteo Finalizado para volver a sortear.")
            await asyncio.sleep(5)
            await message.delete()
            return

        if ctx.message.reference:
            message_id = ctx.message.reference.resolved.id

        message = await ctx.fetch_message(message_id)

        if ctx.message.reference.resolved.author.id != self.bot.user.id :
            msg = await ctx.send(view=CV2("⚠️ Acceso denegado", "No se encontró el sorteo."))
            await asyncio.sleep(5)
            await msg.delete()
            return


        await self.cursor.execute(f"SELECT message_id FROM Giveaway WHERE message_id = ?", (message.id,))
        re = await self.cursor.fetchone()

        if re is not None:
            msg = await ctx.send(view=CV2("⚠️ Acceso denegado", "El sorteo está en curso. Usa el comando `gend` para finalizarlo."))
            await asyncio.sleep(5)
            await msg.delete()
            return

        users = [i.id async for i in message.reactions[0].users()]
        users.remove(self.bot.user.id)

        if len(users) < 1:
            await message.reply(f"Nadie ganó el sorteo de **{re[5]}** porque no hubo suficientes participantes.")
            return

        winners = random.sample(users, k=1)
        await message.reply(f" El nuevo ganador es "+", ".join(f"<@{i}>" for i in winners)+". ¡Felicidades!")
        await self.connection.commit()

    def convert(self, time):
        pos = ["s", "m", "h", "d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "f": 259200}

        unit = time[-1]
        if unit not in pos:
            return -1

        try:
            val = int(time[:-1])
        except ValueError:
            return -2

        return val * time_dict[unit]


    @commands.hybrid_command(name="glist", description="Muestra todos los sorteos en curso.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def glist(self, ctx):
        await self.cursor.execute("SELECT prize, ends_at, winners, message_id FROM Giveaway WHERE guild_id = ?", (ctx.guild.id,))
        giveaways = await self.cursor.fetchall()

        if not giveaways:
            await ctx.send(view=CV2("Sorteos en curso", "No hay sorteos en curso."))
            return

        desc = ""
        for giveaway in giveaways:
            prize, ends_at, winners, message_id = giveaway
            desc += f"**{prize}**\nFinaliza: <t:{int(ends_at)}:R> (<t:{int(ends_at)}:f>)\nGanadores: {winners}\n[Ir al mensaje](https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message_id})\n\n"

        await ctx.send(view=CV2("Sorteos en curso", desc))

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
