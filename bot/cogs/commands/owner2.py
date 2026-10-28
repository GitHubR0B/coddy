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
from discord.ui import Button, View
from discord import Member
from utils import Paginator, DescriptionEmbedPaginator
from datetime import timedelta
import asyncio

class Global(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.local_frozen_nicks = {}  
        self.client.frozen_nicknames = {}

    @commands.group(name="global", invoke_without_command=True)
    @commands.is_owner()
    async def global_command(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @commands.command(name="GB",help="Banea al usuario de todos los servidores en común.")
    @commands.is_owner()
    async def global_ban(self, ctx: commands.Context, user: discord.User, reason: str = "Violaciones graves de los términos de servicio de Discord."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres banear a {user.display_name} globalmente?",
            description=f"El usuario está en **{mutual_count}** servidores en común con el bot.\n\nSolicitante del baneo global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Procesando baneo global para {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.ban(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Éxito",
                description=f"Se baneó al usuario en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")
            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Baneos exitosos [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Baneos fallidos [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    @global_command.command(name="kick", help="Expulsa al usuario de todos los servidores en común.")
    @commands.is_owner()
    async def global_kick(self, ctx: commands.Context, user: discord.User, reason: str = "Violaciones graves de los términos de servicio de Discord."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres expulsar a {user.display_name} globalmente?",
            description=f"El usuario está en **{mutual_count}** servidores en común con el bot.\n\nSolicitante de la expulsión global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Procesando expulsión global para {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.kick(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Éxito",
                description=f"Se expulsó al usuario en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")
            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Expulsiones exitosas [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Expulsiones fallidas [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    @global_command.command(name="timeout", help="Aplica un tiempo de espera al usuario durante 28 días en todos los servidores en común.")
    @commands.is_owner()
    async def global_timeout(self, ctx: commands.Context, user: discord.User, reason: str = "Violaciones graves de los términos de servicio de Discord."):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres aplicar un tiempo de espera a {user.display_name} globalmente durante 28 días?",
            description=f"El usuario está en **{mutual_count}** servidores en común con el bot.\n\nSolicitante del tiempo de espera global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Procesando tiempo de espera global para {user.name}...")
            success, failure = [], []
            
            for guild in mutual_guilds:
                member = guild.get_member(user.id)
                time_delta =  (timedelta(days=28))
                if member:
                    try:
                        await member.edit(timed_out_until=discord.utils.utcnow() + time_delta, reason=reason)
                        success.append(guild.name)
                    except:
                        failure.append(guild.name)
            embed = discord.Embed(
                title="Éxito",
                description=f"Se aplicó el tiempo de espera al usuario en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")
            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Tiempos de espera exitosos [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Tiempos de espera fallidos [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="nick", help="Cambia el apodo de un usuario en todos los servidores en común.")
    @commands.is_owner()
    async def global_nick(self, ctx: commands.Context, user: discord.User, *, name: str):
        if len(name) > 32:
            return await ctx.send("El apodo no puede superar los 32 caracteres. Proporciona un apodo más corto.")

        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres cambiar el apodo de {user.display_name} globalmente?",
            description=f"El usuario está en **{mutual_count}** servidores en común con el bot.\n\nSolicitante del cambio de apodo global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Procesando cambio de apodo global para {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Éxito",
                description=f"Se estableció el apodo de {user.name} en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")
            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Cambios de apodo exitosos [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Cambios de apodo fallidos [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="clearnick", help="Borra el apodo de un usuario en todos los servidores en común.")
    @commands.is_owner()
    async def global_clearnick(self, ctx: commands.Context, user: discord.User):
        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres borrar el apodo de {user.display_name} globalmente?",
            description=f"El usuario está en **{mutual_count}** servidores en común con el bot.\n\nSolicitante del borrado de apodo global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=view)
            await ctx.send(f"Procesando borrado de apodo global para {user.name}...")
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=None)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            embed = discord.Embed(
                title="Éxito",
                description=f"Se borró el apodo de {user.name} en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")
            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            new_view = View()
            new_view.add_item(success_button)
            new_view.add_item(failure_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Borrados de apodo exitosos [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Borrados de apodo fallidos [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            success_button.callback = list_success
            failure_button.callback = list_failure
            await ctx.send(embed=embed, view=new_view)

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)


    @global_command.command(name="freezenick", help="Congela el apodo de un usuario en todos los servidores en común.")
    @commands.is_owner()
    async def global_freezenick(self, ctx: commands.Context, user: discord.User, *, name: str):
        if len(name) > 32:
            return await ctx.send("El apodo no puede superar los 32 caracteres. Proporciona un apodo más corto.")

        if not hasattr(self.client, "frozen_nicknames"):
            self.client.frozen_nicknames = {}

        mutual_guilds = [guild for guild in self.client.guilds if guild.get_member(user.id)]
        mutual_count = len(mutual_guilds)

        confirm_embed = discord.Embed(
            title=f"¿Seguro que quieres congelar el apodo de {user.display_name} globalmente?",
            description=f"El usuario está en {mutual_count} servidores en común con el bot.\n\nSolicitante de la congelación de apodo global: {ctx.author.mention}",
            color=0xFF0000
        )
        yes_button = Button(label="Sí", style=discord.ButtonStyle.green)
        no_button = Button(label="No", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        async def confirm(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            view.clear_items()
            await interaction.response.edit_message(view=None)

            self.client.frozen_nicknames[user.id] = {
                "name": name,
                "guild_ids": [guild.id for guild in mutual_guilds],
            }

            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)

            embed = discord.Embed(
                title="Resultados",
                description=f"Se congeló el apodo de {user.name} en {len(success)} de {mutual_count} servidores en común.",
                color=0xFF0000
            )
            embed.add_field(name="Cantidad de éxitos", value=f"{len(success)} servidores")
            embed.add_field(name="Cantidad de fallos", value=f"{len(failure)} servidores")

            success_button = Button(label="Ver exitosos", style=discord.ButtonStyle.green)
            failure_button = Button(label="Ver fallidos", style=discord.ButtonStyle.red)
            stop_button = Button(label="Detener congelación", style=discord.ButtonStyle.red)
            result_view = View()
            result_view.add_item(success_button)
            result_view.add_item(failure_button)
            result_view.add_item(stop_button)

            async def list_success(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Congelaciones exitosas [{len(success)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def list_failure(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Congelaciones fallidas [{len(failure)}]", color=0xFF0000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()

            async def stop_freeze(interaction):
                if interaction.user != ctx.author:
                    return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                self.client.frozen_nicknames.pop(user.id, None)
                await interaction.response.send_message(f"Se detuvo la congelación del apodo de {user.name}.", ephemeral=True)

            success_button.callback = list_success
            failure_button.callback = list_failure
            stop_button.callback = stop_freeze

            await ctx.send(embed=embed, view=result_view)
            self.client.loop.create_task(self.nickname_freeze_task(user.id))

        async def cancel(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
            await interaction.message.delete()
            await ctx.send("Congelación de apodo cancelada.")

        yes_button.callback = confirm
        no_button.callback = cancel
        await ctx.send(embed=confirm_embed, view=view)

    async def nickname_freeze_task(self, user_id: int):
        while user_id in self.client.frozen_nicknames:
            user_data = self.client.frozen_nicknames[user_id]
            frozen_name = user_data["name"]
            guild_ids = user_data["guild_ids"]

            for guild_id in guild_ids:
                guild = self.client.get_guild(guild_id)
                if not guild:
                    continue
                member = guild.get_member(user_id)
                if member and member.nick != frozen_name:
                    try:
                        await member.edit(nick=frozen_name)
                    except:
                        pass

            await asyncio.sleep(10)

 

    @global_command.command(name="unfreezenick", help="Descongela el apodo de un usuario en todos los servidores en común.")
    @commands.is_owner()
    async def global_unfreezenick(self, ctx: commands.Context, user: discord.User):
        if not hasattr(self.client, "frozen_nicknames"):
            self.client.frozen_nicknames = {}

        if user.id not in self.client.frozen_nicknames:
            return await ctx.send(f"❌ | El apodo de {user.name} no está congelado.")

        del self.client.frozen_nicknames[user.id]
        await ctx.send(f"✅ | Se detuvo la congelación del apodo de {user.name}.")


    @commands.command(name="freezenick", help="Congela el apodo de un miembro en el servidor actual.")
    @commands.has_permissions(manage_nicknames=True)
    async def freeze_nickname(self, ctx: commands.Context, member: Member, *, nickname: str):
        guild_id = ctx.guild.id
        if guild_id not in self.local_frozen_nicks:
            self.local_frozen_nicks[guild_id] = {}

        if member.id in self.local_frozen_nicks[guild_id]:
            return await ctx.send(f"El apodo de {member.mention} ya está congelado.")

        
        try:
            await member.edit(nick=nickname)
            self.local_frozen_nicks[guild_id][member.id] = nickname
            await ctx.send(f"Congelando el apodo de {member.mention} como '{nickname}'.")
        except:
            return await ctx.send(f"No se pudo cambiar el apodo de {member.mention} por permisos insuficientes.")

        async def monitor_nickname():
            while member.id in self.local_frozen_nicks.get(guild_id, {}):
                if member.nick != nickname:
                    try:
                        await member.edit(nick=nickname)
                    except:
                        self.local_frozen_nicks[guild_id].pop(member.id, None)
                        await ctx.send(f"Se dejó de monitorear el apodo de {member.mention} por permisos insuficientes.")
                        break
                await asyncio.sleep(10)

            if not self.local_frozen_nicks[guild_id]:
                del self.local_frozen_nicks[guild_id]

        self.client.loop.create_task(monitor_nickname())

    @commands.command(name="unfreezenick", help="Descongela el apodo de un miembro en el servidor actual.")
    @commands.has_permissions(manage_nicknames=True)
    async def unfreeze_nickname(self, ctx: commands.Context, member: Member):
        guild_id = ctx.guild.id
        if guild_id in self.local_frozen_nicks and member.id in self.local_frozen_nicks[guild_id]:
            self.local_frozen_nicks[guild_id].pop(member.id, None)
            if not self.local_frozen_nicks[guild_id]:
                del self.local_frozen_nicks[guild_id]
            await ctx.send(f"✅ | Se dejó de congelar el apodo de {member.mention}.")
        else:
            await ctx.send(f"❌ | El apodo de {member.mention} no está congelado actualmente.")


