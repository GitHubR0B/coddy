# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from utils.emoji import ICONS_CHANNEL, ICONS_PLUS, TICK, ZTICK
from discord.ext import commands
from discord.ui import View, Select, Button
from discord import app_commands
import aiosqlite
import asyncio
import re
import json
from utils.Tools import *

class VariableButton(Button):
    def __init__(self, author):
        super().__init__(label="Variables", style=discord.ButtonStyle.secondary)
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("Solo el autor del comando puede usar este botón.", ephemeral=True)
            return

        variables = {
            "{user}": "Menciona al usuario (por ejemplo, @NombreDeUsuario).",
            "{user_avatar}": "La URL del avatar del usuario.",
            "{user_name}": "El nombre de usuario del usuario.",
            "{user_id}": "El número de ID del usuario.",
            "{user_nick}": "El apodo del usuario en el servidor.",
            "{user_joindate}": "La fecha de ingreso del usuario al servidor (con formato Día, Mes Día, Año).",
            "{user_createdate}": "La fecha de creación de la cuenta del usuario (con formato Día, Mes Día, Año).",
            "{server_name}": "El nombre del servidor.",
            "{server_id}": "El número de ID del servidor.",
            "{server_membercount}": "El número total de miembros del servidor.",
            "{server_icon}": "La URL del icono del servidor."
        }
        
        embed = discord.Embed(
            title="Marcadores disponibles",
            description="Usa estos marcadores en tu mensaje de bienvenida:",
            color=discord.Color(0xFF0000)
        )

        for var, desc in variables.items():
            embed.add_field(name=var, value=desc, inline=False)

        embed.set_footer(text="Añade los marcadores directamente en el mensaje de bienvenida o en los campos del embed.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self._create_table())

    # Slash command descriptions with emoji | descripcion pattern
    greet_slash_description = "Configura el mensaje de bienvenida para nuevos miembros"
    greet_setup_slash_description = "Configura el mensaje de bienvenida simple"
    greet_reset_slash_description = "Restablece el mensaje de bienvenida"

    async def _create_table(self):
        async with aiosqlite.connect("db/welcome.db") as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS welcome (
                guild_id INTEGER PRIMARY KEY,
                welcome_type TEXT,
                welcome_message TEXT,
                channel_id INTEGER,
                embed_data TEXT,
                auto_delete_duration INTEGER
            )
            """)
            await db.commit()

    @commands.hybrid_group(invoke_without_command=True, name="greet", help="Muestra todos los comandos de saludos.")
    @app_commands.describe(accion="Acción a realizar")
    @blacklist_check()
    @ignore_check()
    async def greet(self, ctx: commands.Context, accion: str = None):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @greet.command(name="setup", help="Configura un mensaje de bienvenida para los nuevos miembros que se unan al servidor. ")
    @app_commands.describe(tipo="Tipo de mensaje: simple o embed")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def greet_setup(self, ctx: commands.Context, tipo: str = None):
        async with aiosqlite.connect("db/welcome.db") as db:
            async with db.execute("SELECT * FROM welcome WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()
        
        if row:
            error = discord.Embed(description=f"Ya se ha configurado un mensaje de bienvenida en {ctx.guild.name}. Usa `{ctx.prefix}bienvenida restablecer` para reconfigurarlo.", color=0xFF0000)
            error.set_author(name="Error", icon_url="https://cdn.discordapp.com/emojis/1294218790082711553.png")
            return await ctx.send(embed=error)
            
        options_view = View(timeout=600)

        async def option_callback(interaction: discord.Interaction, button: Button):
            if interaction.user != ctx.author:
                await interaction.response.send_message("No puedes interactuar con esta configuración.", ephemeral=True)
                return
            await interaction.response.defer()

            if button.custom_id == "simple":
                await interaction.message.delete()
                await self.simple_setup(ctx)
                
            elif button.custom_id == "embed":
                await interaction.message.delete()
                await self.embed_setup(ctx)
            elif button.custom_id == "cancel":
                await interaction.message.delete()

        button_simple = Button(label="Simple", style=discord.ButtonStyle.success, custom_id="simple")
        button_simple.callback = lambda interaction: option_callback(interaction, button_simple)
        options_view.add_item(button_simple)

        button_embed = Button(label="Embed", style=discord.ButtonStyle.success, custom_id="embed")
        button_embed.callback = lambda interaction: option_callback(interaction, button_embed)
        options_view.add_item(button_embed)

        button_cancel = Button(label="Cancelar", style=discord.ButtonStyle.danger, custom_id="cancel")
        button_cancel.callback = lambda interaction: option_callback(interaction, button_cancel)
        options_view.add_item(button_cancel)

        embed = discord.Embed(
            title="Configuración del mensaje de bienvenida",
            description="Elige el tipo de mensaje de bienvenida que quieres crear:",
            color=0xFF0000
        )

        embed.add_field(
            name=" Simple",
            value="Envía un mensaje de bienvenida en texto plano. Puedes usar marcadores para personalizarlo.\n\n", 
            inline=False
        )
        embed.add_field(
            name=" Embed",
            value="Envía un mensaje de bienvenida en formato embed. Puedes personalizar el embed con título, descripción, imagen, etc.",
            inline=False
        )

        embed.set_footer(text="Haz clic en los botones de abajo para elegir el tipo de mensaje de bienvenida.", icon_url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed, view=options_view)

    async def simple_setup(self, ctx):
        setup_view = View(timeout=600)
        first = View(timeout=600)
        message_content = []

        placeholders = {
            "{user}": ctx.author.mention,
            "{user_avatar}": ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url,
            "{user_name}": ctx.author.name,
            "{user_id}": ctx.author.id,
            "{user_nick}": ctx.author.display_name,
            "{user_joindate}": ctx.author.joined_at.strftime("%a, %b %d, %Y"),
            "{user_createdate}": ctx.author.created_at.strftime("%a, %b %d, %Y"),
            "{server_name}": ctx.guild.name,
            "{server_id}": ctx.guild.id,
            "{server_membercount}": ctx.guild.member_count,
            "{server_icon}": ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
            "{timestamp}": discord.utils.format_dt(ctx.message.created_at)
        }

        def safe_format(text):
            placeholders_lower = {k.lower(): v for k, v in placeholders.items()}

            def replace_var(match):
                var_name = match.group(1).lower()
                return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))

            return re.sub(r"\{(\w+)\}", replace_var, text or "")
        
        # Default welcome message with panel link (professional version)
        default_welcome_msg = (
            f"¡Bienvenido/a {{{user}}} a {{{server_name}}}! 🎉\n\n"
            f"Nos alegra tenerte como nuevo miembro de nuestra comunidad.\n\n"
            f"📋 **Sobre nosotros:** Somos un servidor dedicado a proporcionar una experiencia\n"
            f"                 entretenida y organizada para todos nuestros miembros.\n\n"
            f"🌐 **Web:** https://soycoddy.es/ | **Dashboard:** https://soycoddy.es/dashboard\n"
            f"   Gestiona tu bienvenida, niveles, tickets y más desde aquí.\n\n"
            f"💡 **Recomendación:** Revisa el canal #{canal} para obtener información\n"
            f"   sobre reglas y recursos disponibles.\n\n"
            f"¡Esperamos que te quedes y disfrutes tu estadía con nosotros!"
        )

        async def update_preview(content):
            preview = safe_format(content)
            await preview_message.edit(content=f"**Vista previa:** {preview}", view=setup_view)

        first.add_item(VariableButton(ctx.author))

        # Set default message content
        preview_message = await ctx.send("__**Configuración de mensaje simple**__ \nEscribe tu mensaje de bienvenida aquí:\n```\n" + default_welcome_msg + "\n```", view=first)

    async def embed_setup(self, ctx):
        setup_view = View(timeout=600)
        embed_data = {
            "message": None,
            "title": None,
            "description": None,
            "color": None,
            "footer_text": None,
            "footer_icon": None,
            "author_name": None,
            "author_icon": None,
            "thumbnail": None,
            "image": None,
        }

        placeholders = {
            "{user}": ctx.author.mention,
            "{user_avatar}": ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url,
            "{user_name}": ctx.author.name,
            "{user_id}": ctx.author.id,
            "{user_nick}": ctx.author.display_name,
            "{user_joindate}": ctx.author.joined_at.strftime("%a, %b %d, %Y"),
            "{user_createdate}": ctx.author.created_at.strftime("%a, %b %d, %Y"),
            "{server_name}": ctx.guild.name,
            "{server_id}": ctx.guild.id,
            "{server_membercount}": ctx.guild.member_count,
            "{server_icon}": ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png",
            "{timestamp}": discord.utils.format_dt(ctx.message.created_at)
        }

        def safe_format(text):
            placeholders_lower = {k.lower(): v for k, v in placeholders.items()}  
            def replace_var(match):
                var_name = match.group(1).lower()
                return str(placeholders_lower.get(var_name, f"{{{var_name}}}"))
            return re.sub(r"\{(\w+)\}", replace_var, text or "")
        
        # Default embed welcome message with panel link (professional version)
        default_embed_title = "¡Bienvenido/a!"
        default_embed_description = (
            f"¡Hola {{{user}}}! 🎉\n"
            f"Nos alegra tenerte como nuevo miembro de nuestra comunidad.\n\n"
            f"📋 **Sobre nosotros:** Somos un servidor dedicado a proporcionar una experiencia\n"
            f"                 entretenida y organizada para todos nuestros miembros.\n\n"
            f"🌐 **Web:** https://soycoddy.es/ | **Dashboard:** https://soycoddy.es/dashboard\n"
            f"   Gestiona tu bienvenida, niveles, tickets y más desde aquí.\n"
            f"   ¡Explora y disfruta tu estadía!\n"
        )

        async def update_preview():
            content = safe_format(embed_data["message"]) or "Contenido del mensaje."
            embed = discord.Embed(
    title=safe_format(embed_data["title"]) or default_embed_title,
    description=safe_format(embed_data["description"]) or default_embed_description,
    color=discord.Color(embed_data["color"]) if embed_data["color"] else discord.Color(0x2f3136)
            )

            if embed_data["footer_text"]:
                embed.set_footer(text=safe_format(embed_data["footer_text"]), icon_url=safe_format(embed_data["footer_icon"]) or None)
            if embed_data["author_name"]:
                embed.set_author(name=safe_format(embed_data["author_name"]), icon_url=safe_format(embed_data["author_icon"]) or None)
            if embed_data["thumbnail"]:
                embed.set_thumbnail(url=safe_format(embed_data["thumbnail"]))
            if embed_data["image"]:
                embed.set_image(url=safe_format(embed_data["image"]))
            
            preview_content = "**Vista previa del embed:** " + (content or "Sin descripción")
            await preview_message.edit(content=preview_content, embed=embed, view=setup_view)

        preview_message = await ctx.send("Configurando el mensaje de bienvenida en embed...")

        select_menu = Select(
            placeholder="Selecciona un estilo de embed...",
            options=[
                discord.SelectOption(label="Estilo 1", description="Estilo clásico"),
                discord.SelectOption(label="Estilo 2", description="Estilo moderno"),
                discord.SelectOption(label="Estilo 3", description="Estilo minimalista"),
            ]
        )

        async def handle_selection(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("No puedes interactuar con esta configuración.", ephemeral=True)
                return
            await interaction.response.defer()
            # Handle selection...

        setup_view.add_item(select_menu)
        setup_view.add_item(VariableButton(ctx.author))
        
        cancel_button = Button(emoji=ICONS_PLUS, style=discord.ButtonStyle.secondary)
        cancel_button.callback = lambda interaction: None  # Placeholder
        setup_view.add_item(cancel_button)

        try:
            msg = await self.bot.wait_for("message", timeout=600, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            # Process the message...
        except asyncio.TimeoutError:
            await ctx.send("Se agotó el tiempo de configuración.")