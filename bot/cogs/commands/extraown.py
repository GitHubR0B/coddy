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
from discord.ext import commands
from discord.ui import LayoutView, TextDisplay, Separator, Container, ActionRow, Button
import aiosqlite
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import OWNER_IDS_STR





class ConfirmView(LayoutView):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.value = None

        self.yes_btn = Button(label="Confirmar", style=discord.ButtonStyle.green)
        self.no_btn = Button(label="Cancelar", style=discord.ButtonStyle.red)

        self.yes_btn.callback = self.confirm_callback
        self.no_btn.callback = self.cancel_callback

        container = build_container(
            TextDisplay("**Confirmar acción**"),
            Separator(visible=True),
            TextDisplay(self._desc),
            ActionRow(self.yes_btn, self.no_btn),
        )
        self.add_item(container)

    @property
    def _desc(self):
        return ""

    async def confirm_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("No puedes interactuar con esta confirmación.", ephemeral=True)
        self.value = True
        await interaction.response.defer()
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("No puedes interactuar con esta confirmación.", ephemeral=True)
        self.value = False
        await interaction.response.defer()
        self.stop()


class SetConfirmView(ConfirmView):
    def __init__(self, ctx, user):
        self._user = user
        super().__init__(ctx)

    @property
    def _desc(self):
        return f"**¿Seguro que quieres establecer a {self._user.mention} como propietario extra?**"


class ResetConfirmView(ConfirmView):
    @property
    def _desc(self):
        return "**¿Seguro que quieres restablecer el propietario extra?**"


class Extraowner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initialize_db())

    async def initialize_db(self):
        self.db = await aiosqlite.connect('db/anti.db')
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS extraowners (
                guild_id INTEGER PRIMARY KEY,
                owner_id INTEGER
            )
        ''')
        await self.db.commit()

    @commands.hybrid_command(name='extraowner', aliases=["owner"], help="Añade un propietario extra al servidor")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def extraowner(self, ctx, option: str = None, user: discord.Member = None):
        guild_id = ctx.guild.id

        if ctx.guild.member_count < 2:
            return await ctx.send(view=CV2(f"{CROSS} Error", "Tu servidor no cumple con mi criterio de 30 miembros"))

        Ray = OWNER_IDS_STR
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in Ray:
            return await ctx.send(view=CV2(f"{ZWARNING} Acceso denegado", "Solo el propietario del servidor puede ejecutar este comando"))

        if option is None:
            pre = ctx.prefix
            info_text = (
                "Los propietarios extra pueden ajustar la configuración de Antinuke del servidor y gestionar los eventos de la lista blanca, "
                "así que piénsalo bien antes de asignarlo a alguien.\n\n"
                f"**Establecer propietario extra** — `{pre}extraowner set @user`\n"
                f"**Restablecer propietario extra** — `{pre}extraowner reset`\n"
                f"**Ver propietario extra** — `{pre}extraowner view`"
            )
            return await ctx.reply(view=CV2("__Propietario extra__", info_text))

        if option.lower() == 'set':
            if user is None or user.bot:
                return await ctx.reply(view=CV2(f"{CROSS} Error", "¡Proporciona una mención o ID de usuario válido para establecerlo como propietario extra!"))

            view = SetConfirmView(ctx, user)
            message = await ctx.reply(view=view)
            await view.wait()

            if view.value is None:
                await message.edit(view=CV2("⏰ Tiempo agotado", "La confirmación expiró."))
            elif view.value:
                await self.db.execute('INSERT OR REPLACE INTO extraowners (guild_id, owner_id) VALUES (?, ?)', (guild_id, user.id))
                await self.db.commit()
                await message.edit(view=CV2(f"{TICK} Éxito", f"Se añadió a {user.mention} como propietario extra"))
            else:
                await message.edit(view=CV2(f"{CROSS} Cancelado", "Acción cancelada."))

        elif option.lower() == 'reset':
            async with self.db.execute('SELECT owner_id FROM extraowners WHERE guild_id = ?', (guild_id,)) as cursor:
                row = await cursor.fetchone()

            if not row:
                await ctx.reply(view=CV2(f"{CROSS} Error", "No se ha designado ningún propietario extra para este servidor."))
            else:
                view = ResetConfirmView(ctx)
                message = await ctx.reply(view=view)
                await view.wait()

                if view.value is None:
                    await message.edit(view=CV2("⏰ Tiempo agotado", "La confirmación expiró."))
                elif view.value:
                    await self.db.execute('DELETE FROM extraowners WHERE guild_id = ?', (guild_id,))
                    await self.db.commit()
                    await message.edit(view=CV2(f"{TICK} Éxito", "¡Configuración de propietario extra deshabilitada!"))
                else:
                    await message.edit(view=CV2(f"{CROSS} Cancelado", "Acción cancelada."))

        elif option.lower() == 'view':
            async with self.db.execute('SELECT owner_id FROM extraowners WHERE guild_id = ?', (guild_id,)) as cursor:
                row = await cursor.fetchone()

            if not row:
                await ctx.reply(view=CV2(f"{CROSS} Error", "No hay ningún propietario extra asignado actualmente."))
            else:
                await ctx.reply(view=CV2("Propietario extra", f"El propietario extra actual es <@{row[0]}>"))
