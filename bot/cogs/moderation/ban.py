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
from utils.emoji import TICK, ZWARNING
from discord.ext import commands
from discord import ui
from utils.Tools import *

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="ban",
        help="Banea a un usuario del servidor",
        usage="ban <member>",
        aliases=["fuckban", "hackban","kuttaban"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):

        member = ctx.guild.get_member(user.id)
        if not member:
            try:
                user = await self.bot.fetch_user(user.id)
            except discord.NotFound:
                # User not found container
                container = ui.Container()
                container.add_item(ui.TextDisplay(f"❌ **Usuario no encontrado**\nNo se encontró el usuario con ID {user.id}."))
                view = ui.LayoutView()
                view.add_item(container)
                await ctx.send(view=view)
                return

        bans = [entry async for entry in ctx.guild.bans()]
        if any(ban_entry.user.id == user.id for ban_entry in bans):
            # Already banned container
            container = ui.Container()
            container.add_item(ui.TextDisplay(f"⚠️ **¡{user.name} ya está baneado!**"))
            container.add_item(ui.TextDisplay("**El usuario solicitado ya está baneado en este servidor.**"))
            container.add_item(ui.TextDisplay(f"*Solicitado por {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            await ctx.send(view=view)
            return

        if member == ctx.guild.owner:
            # Server owner error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error al banear al usuario**"))
            container.add_item(ui.TextDisplay("¡No puedo banear al dueño del servidor!"))
            container.add_item(ui.TextDisplay(f"*Solicitado por {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member) and member.top_role >= ctx.guild.me.top_role:
            # Role hierarchy error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error al banear al usuario**"))
            container.add_item(ui.TextDisplay("¡No puedo banear a un usuario con un rol igual o superior!"))
            container.add_item(ui.TextDisplay(f"*Solicitado por {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member):
            if ctx.author != ctx.guild.owner:
                if member.top_role >= ctx.author.top_role:
                    # Author role hierarchy error container
                    container = ui.Container()
                    container.add_item(ui.TextDisplay("❌ **Error al banear al usuario**"))
                    container.add_item(ui.TextDisplay("¡No puedes banear a un usuario con un rol igual o superior!"))
                    container.add_item(ui.TextDisplay(f"*Solicitado por {ctx.author}*"))
                    view = ui.LayoutView()
                    view.add_item(container)
                    return await ctx.send(view=view)

        # Try to DM the user
        try:
            await user.send(f"{ZWARNING} Has sido baneado de **{ctx.guild.name}** por **{ctx.author}**. Razón: {reason or 'No se proporcionó una razón'}")
            dm_status = "Sí"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        # Ban the user
        await ctx.guild.ban(user, reason=f"Baneo solicitado por {ctx.author} por la razón: {reason or 'No se proporcionó una razón'}")

        # Success container with Components V2
        container = ui.Container()
        container.add_item(ui.TextDisplay(f"✅ **{user.name} fue baneado correctamente**"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**{TICK} | [{user}](https://discord.com/users/{user.id}) Fue baneado correctamente**"
            f"\n**Razón:** {reason or 'No se proporcionó una razón'}"
            f"\n**MD enviado:** {dm_status}"
            f"\n**Moderador:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"*Solicitado por {ctx.author} • {discord.utils.format_dt(discord.utils.utcnow(), 'R')}*"))
        
        view = ui.LayoutView()
        view.add_item(container)
        
        message = await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Ban(bot))