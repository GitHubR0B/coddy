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
from discord import ui, SelectOption
from discord.ui import LayoutView, TextDisplay, Separator, ActionRow
import aiosqlite
import asyncio
from typing import Dict, List, Optional
from utils.cv2 import CV2, build_container

class JoinToCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_channels: Dict[int, Dict] = {}
        self.category_name = "J2C"
        self.setup_data: Dict[int, Dict] = {}
        self.db_path = "j2c_data.db"
        self.blocked_users: Dict[int, List[int]] = {}  # {vc_id: [user_ids]}
        self.creating_vc = set()

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_setup (
                    guild_id INTEGER PRIMARY KEY,
                    join_channel_id INTEGER,
                    control_channel_id INTEGER,
                    control_message_id INTEGER,
                    category_id INTEGER
                )
            """)
            try:
                await db.execute("ALTER TABLE guild_setup ADD COLUMN category_id INTEGER")
            except aiosqlite.OperationalError:
                pass
            await db.execute("""
                CREATE TABLE IF NOT EXISTS private_channels (
                    vc_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    owner_id INTEGER,
                    member_limit INTEGER DEFAULT 2,
                    region TEXT DEFAULT '',
                    is_locked BOOLEAN DEFAULT FALSE,
                    has_waiting_room BOOLEAN DEFAULT FALSE,
                    has_thread BOOLEAN DEFAULT FALSE
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS blocked_users (
                    vc_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (vc_id, user_id)
                )
            """)
            await db.commit()

    async def load_data(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Load guild setups
            async with db.execute("SELECT guild_id, join_channel_id, control_channel_id, control_message_id, category_id FROM guild_setup") as cursor:
                async for row in cursor:
                    guild_id, join_channel_id, control_channel_id, control_message_id, category_id = row
                    self.setup_data[guild_id] = {
                        "join_channel_id": join_channel_id,
                        "control_channel_id": control_channel_id,
                        "control_message_id": control_message_id,
                        "category_id": category_id
                    }

            # Load private channels
            async with db.execute("SELECT * FROM private_channels") as cursor:
                async for row in cursor:
                    vc_id, guild_id, owner_id, member_limit, region, is_locked, has_waiting_room, has_thread = row
                    self.private_channels[vc_id] = {
                        "owner": owner_id,
                        "limit": member_limit,
                        "region": region,
                        "is_locked": bool(is_locked),
                        "has_waiting_room": bool(has_waiting_room),
                        "has_thread": bool(has_thread),
                        "guild_id": guild_id
                    }

            # Load blocked users
            async with db.execute("SELECT * FROM blocked_users") as cursor:
                async for row in cursor:
                    vc_id, user_id = row
                    if vc_id not in self.blocked_users:
                        self.blocked_users[vc_id] = []
                    self.blocked_users[vc_id].append(user_id)

    async def save_guild_setup(self, guild_id: int, data: Dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO guild_setup (guild_id, join_channel_id, control_channel_id, control_message_id, category_id)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, data["join_channel_id"], data["control_channel_id"], data["control_message_id"], data.get("category_id")))
            await db.commit()

    async def save_private_channel(self, vc_id: int, guild_id: int, data: Dict):
        try:
            if vc_id not in self.private_channels:
                self.private_channels[vc_id] = data
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO private_channels 
                    (vc_id, guild_id, owner_id, member_limit, region, is_locked, has_waiting_room, has_thread)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vc_id, guild_id, 
                    data["owner"], 
                    data.get("limit", 2),
                    data.get("region", ""),
                    data.get("is_locked", False),
                    data.get("has_waiting_room", False),
                    data.get("has_thread", False)
                ))
                await db.commit()
        except Exception as e:
            print(f"Error saving private channel: {e}")

    async def delete_private_channel(self, vc_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM private_channels WHERE vc_id = ?", (vc_id,))
            await db.execute("DELETE FROM blocked_users WHERE vc_id = ?", (vc_id,))
            await db.commit()

    async def delete_guild_setup(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM guild_setup WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM private_channels WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM blocked_users WHERE vc_id IN (SELECT vc_id FROM private_channels WHERE guild_id = ?)", (guild_id,))
            await db.commit()

    async def block_user(self, vc_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO blocked_users (vc_id, user_id) VALUES (?, ?)", (vc_id, user_id))
            await db.commit()
        if vc_id not in self.blocked_users:
            self.blocked_users[vc_id] = []
        if user_id not in self.blocked_users[vc_id]:
            self.blocked_users[vc_id].append(user_id)

    async def unblock_user(self, vc_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM blocked_users WHERE vc_id = ? AND user_id = ?", (vc_id, user_id))
            await db.commit()
        if vc_id in self.blocked_users and user_id in self.blocked_users[vc_id]:
            self.blocked_users[vc_id].remove(user_id)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_db()
        await self.load_data()
        for guild_id, data in self.setup_data.items():
            guild = self.bot.get_guild(guild_id)
            if guild:
                try:
                    control_channel = guild.get_channel(data["control_channel_id"])
                    if control_channel:
                        msg = None
                        if data["control_message_id"]:
                            try:
                                msg = await control_channel.fetch_message(data["control_message_id"])
                            except:
                                pass
                        
                        if msg:
                            view = ControlPanelView(self, guild)
                            await msg.edit(view=view, embed=None, content=None)
                        else:
                            view = ControlPanelView(self, guild)
                            msg = await control_channel.send(view=view)
                            self.setup_data[guild_id]["control_message_id"] = msg.id
                            await self.save_guild_setup(guild_id, self.setup_data[guild_id])
                except Exception as e:
                    print(f"Error in J2C on_ready: {e}")
                    continue

    @commands.command(name='j2csetup')
    @commands.has_permissions(administrator=True)
    async def setup_private_channels(self, ctx):
        if ctx.guild.id in self.setup_data:
            await ctx.send(view=CV2("❌ Error", "¡El sistema J2C ya está configurado en este servidor!"))
            return
            
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if not category:
            category = await ctx.guild.create_category(self.category_name)
        
        join_channel = await ctx.guild.create_voice_channel(
            "➕ Únete para crear",
            category=category,
            reason="J2C System Setup"
        )
        
        control_channel = await ctx.guild.create_text_channel(
            "ctrl-panel",
            category=category,
            reason="J2C System Setup"
        )
        
        view = ControlPanelView(self, ctx.guild)
        control_message = await control_channel.send(view=view)
        
        self.setup_data[ctx.guild.id] = {
            "join_channel_id": join_channel.id,
            "control_channel_id": control_channel.id,
            "control_message_id": control_message.id
        }
        await self.save_guild_setup(ctx.guild.id, self.setup_data[ctx.guild.id])
        
        await ctx.send(view=CV2("✅ Éxito", f"¡Configuración del sistema J2C completada! Únete a {join_channel.mention} para crear un canal de voz privado."))

    @commands.command(name='j2creset')
    @commands.has_permissions(administrator=True)
    async def reset_private_channels(self, ctx):
        if ctx.guild.id not in self.setup_data:
            await ctx.send(view=CV2("❌ Error", "¡El sistema J2C no está configurado en este servidor!"))
            return
            
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category:
            for channel in category.channels:
                try:
                    await channel.delete(reason="J2C System Reset")
                except:
                    continue
        
        if category:
            try:
                await category.delete(reason="J2C System Reset")
            except:
                pass
        
        vc_ids = [vc_id for vc_id, data in self.private_channels.items() 
                 if data.get("guild_id") == ctx.guild.id]
        for vc_id in vc_ids:
            del self.private_channels[vc_id]
        
        del self.setup_data[ctx.guild.id]
        await self.delete_guild_setup(ctx.guild.id)
        
        await ctx.send(view=CV2("✅ Éxito", "¡El sistema J2C se ha restablecido por completo en este servidor!"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id not in self.setup_data:
            return
            
        guild_data = self.setup_data[member.guild.id]
        
        # User joined the join channel
        if after.channel and after.channel.id == guild_data["join_channel_id"]:
            if member.id in self.creating_vc:
                return
            self.creating_vc.add(member.id)
            try:
                category_id = guild_data.get("category_id")
                category = None
                if category_id:
                    try:
                        category = member.guild.get_channel(int(category_id))
                    except:
                        pass
                
                # Fallback 1: Use the parent category of the join channel
                if not category and after.channel.category:
                    category = after.channel.category
                    
                # Fallback 2: J2C category by name
                if not category:
                    category = discord.utils.get(member.guild.categories, name=self.category_name)
                    
                vc = await member.guild.create_voice_channel(
                    f"VC de {member.name}",
                    category=category,
                    reason="Private VC Creation",
                    user_limit=2
                )
                
                await member.move_to(vc)
                
                self.private_channels[vc.id] = {
                    "owner": member.id,
                    "limit": 2,
                    "region": "",
                    "is_locked": False,
                    "has_waiting_room": False,
                    "has_thread": False,
                    "guild_id": member.guild.id
                }
                await self.save_private_channel(vc.id, member.guild.id, self.private_channels[vc.id])
                await self.update_control_panel(member.guild)
            finally:
                self.creating_vc.discard(member.id)
            
        # User left a private channel
        if before.channel and before.channel.id in self.private_channels:
            # Check if user was blocked
            if (before.channel.id in self.blocked_users and 
                member.id in self.blocked_users[before.channel.id]):
                await member.move_to(None)
                return
                
            # Check if channel is empty
            if len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except:
                    pass
                
                if before.channel.id in self.private_channels:
                    del self.private_channels[before.channel.id]
                    await self.delete_private_channel(before.channel.id)
                
                await self.update_control_panel(member.guild)

    async def update_control_panel(self, guild: discord.Guild):
        if guild.id not in self.setup_data:
            return
            
        guild_data = self.setup_data[guild.id]
        control_channel = guild.get_channel(guild_data["control_channel_id"])
        if not control_channel or not guild_data["control_message_id"]:
            return
            
        try:
            control_message = await control_channel.fetch_message(guild_data["control_message_id"])
            view = ControlPanelView(self, guild)
            await control_message.edit(view=view, embed=None, content=None)
        except:
            pass

class ControlPanelView(LayoutView):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        
        desc = ("Únete al canal de voz 'Únete para crear' para crear tu propio canal de voz privado.\n\n"
               "Usa los botones de abajo para administrar tu canal de voz privado.")
        active_vcs = []
        for vc_id, data in self.cog.private_channels.items():
            if guild.get_channel(vc_id):
                owner = guild.get_member(data["owner"])
                if owner:
                    status = []
                    if data["is_locked"]:
                        status.append("🔒 Bloqueado")
                    if data["has_thread"]:
                        status.append("💬 Hilo")
                    
                    vc_info = f"<#{vc_id}> (👑 {owner.mention})"
                    if status:
                        vc_info += f" [{' '.join(status)}]"
                    active_vcs.append(vc_info)
        
        if active_vcs:
            desc += "\n\n**Canales de voz privados activos**\n" + "\n".join(active_vcs)
            
        container = build_container(
            TextDisplay("**Sistema J2C**"),
            Separator(visible=True),
            TextDisplay(desc)
        )
        self.add_item(container)

        b_limit = ui.Button(label="LÍMITE", style=discord.ButtonStyle.blurple, custom_id="j2c:limit", emoji="⏳")
        b_limit.callback = self.set_limit
        b_privacy = ui.Button(label="PRIVACIDAD", style=discord.ButtonStyle.blurple, custom_id="j2c:privacy", emoji="🔒")
        b_privacy.callback = self.toggle_privacy
        b_thread = ui.Button(label="HILO", style=discord.ButtonStyle.blurple, custom_id="j2c:thread", emoji="💬")
        b_thread.callback = self.create_thread
        b_untrust = ui.Button(label="DESCONFIAR", style=discord.ButtonStyle.green, custom_id="j2c:untrust", emoji="❌")
        b_untrust.callback = self.untrust
        b_invite = ui.Button(label="INVITAR", style=discord.ButtonStyle.green, custom_id="j2c:invite", emoji="✉️")
        b_invite.callback = self.invite_user
        b_kick = ui.Button(label="EXPULSAR", style=discord.ButtonStyle.green, custom_id="j2c:kick", emoji="👢")
        b_kick.callback = self.kick_user
        b_region = ui.Button(label="REGIÓN", style=discord.ButtonStyle.green, custom_id="j2c:region", emoji="🌍")
        b_region.callback = self.set_region
        b_unblock = ui.Button(label="DESBLOQUEAR", style=discord.ButtonStyle.red, custom_id="j2c:unblock", emoji="🔓")
        b_unblock.callback = self.unblock
        b_claim = ui.Button(label="RECLAMAR", style=discord.ButtonStyle.red, custom_id="j2c:claim", emoji="⭐")
        b_claim.callback = self.claim
        b_transfer = ui.Button(label="TRANSFERIR", style=discord.ButtonStyle.red, custom_id="j2c:transfer", emoji="🔄")
        b_transfer.callback = self.transfer
        b_delete = ui.Button(label="ELIMINAR", style=discord.ButtonStyle.red, custom_id="j2c:delete", emoji="🗑️")
        b_delete.callback = self.delete_vc
        b_block = ui.Button(label="BLOQUEAR", style=discord.ButtonStyle.danger, custom_id="j2c:block", emoji="🚫")
        b_block.callback = self.block

        self.add_item(ActionRow(b_limit, b_privacy, b_thread))
        self.add_item(ActionRow(b_untrust, b_invite, b_kick, b_region))
        self.add_item(ActionRow(b_unblock, b_claim, b_transfer, b_delete))
        self.add_item(ActionRow(b_block))
    
    async def get_owned_vc(self, interaction: discord.Interaction) -> Optional[discord.VoiceChannel]:
        for vc_id, data in self.cog.private_channels.items():
            if data["owner"] == interaction.user.id:
                vc = interaction.guild.get_channel(vc_id)
                if vc:
                    return vc
        return None
    
    async def set_limit(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        modal = SetLimitModal(vc)
        await interaction.response.send_modal(modal)
    
    async def toggle_privacy(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        is_locked = not self.cog.private_channels[vc.id]["is_locked"]
        await vc.set_permissions(interaction.guild.default_role, connect=not is_locked)
        self.cog.private_channels[vc.id]["is_locked"] = is_locked
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"¡El canal de voz ahora está {'🔒 bloqueado' if is_locked else '🔓 desbloqueado'}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)

    
    async def create_thread(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        has_thread = not self.cog.private_channels[vc.id]["has_thread"]
        self.cog.private_channels[vc.id]["has_thread"] = has_thread
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        if has_thread:
            thread = await interaction.channel.create_thread(name=f"Discusión de {vc.name}", auto_archive_duration=60)
            await interaction.followup.send(f"Hilo creado: {thread.mention}", ephemeral=True)
        else:
            await interaction.followup.send("Función de hilos desactivada para tu canal de voz", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def untrust(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        await interaction.followup.send("La función de desconfianza se implementaría aquí", ephemeral=True)
    
    async def invite_user(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        options = []
        for member in interaction.guild.members:
            if (member not in vc.members and not member.bot and member != interaction.user):
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("¡No hay miembros disponibles para invitar!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Selecciona miembros para invitar", self.invite_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona miembros para invitar:", view=view, ephemeral=True)
    
    async def invite_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            member = interaction.guild.get_member(int(user_id))
            if member:
                try: await member.send(f"¡{interaction.user.mention} te ha invitado a unirte a {vc.mention}!")
                except: pass
        await interaction.followup.send("¡Invitaciones enviadas!", ephemeral=True)
    
    async def kick_user(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        options = []
        for member in vc.members:
            if member.id != interaction.user.id:
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("¡No hay usuarios para expulsar de tu canal de voz!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Selecciona miembros para expulsar", self.kick_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona miembros para expulsar:", view=view, ephemeral=True)
    
    async def kick_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            member = interaction.guild.get_member(int(user_id))
            if member and member in vc.members:
                try: await member.move_to(None)
                except: pass
        await interaction.followup.send("¡Miembros seleccionados expulsados!", ephemeral=True)
    
    async def set_region(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        regions = [
            SelectOption(label="Automática", value="auto"), SelectOption(label="Oeste de EE. UU.", value="us-west"),
            SelectOption(label="Este de EE. UU.", value="us-east"), SelectOption(label="Europa", value="europe"),
            SelectOption(label="Singapur", value="singapore"), SelectOption(label="Japón", value="japan"),
            SelectOption(label="Brasil", value="brazil"), SelectOption(label="Australia", value="australia")
        ]
        dropdown = RegionSelectDropdown(regions, vc)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona una región:", view=view, ephemeral=True)
    
    async def unblock(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        if vc.id not in self.cog.blocked_users or not self.cog.blocked_users[vc.id]:
            await interaction.response.send_message("¡No hay usuarios bloqueados!", ephemeral=True)
            return
        options = []
        for user_id in self.cog.blocked_users[vc.id]:
            member = interaction.guild.get_member(user_id)
            if member:
                options.append(SelectOption(label=member.name, value=str(user_id)))
        dropdown = UserSelectDropdown(options, "Selecciona usuarios para desbloquear", self.unblock_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona usuarios para desbloquear:", view=view, ephemeral=True)
    
    async def unblock_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            await self.cog.unblock_user(vc.id, int(user_id))
        await interaction.followup.send("¡Usuarios seleccionados desbloqueados!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def claim(self, interaction: discord.Interaction):
        available_vcs = []
        for vc_id, data in self.cog.private_channels.items():
            if data["guild_id"] == interaction.guild.id:
                vc = interaction.guild.get_channel(vc_id)
                if vc:
                    owner = interaction.guild.get_member(data["owner"])
                    if not owner or owner not in vc.members:
                        available_vcs.append((vc, data))
        if not available_vcs:
            await interaction.response.send_message("¡No hay canales de voz disponibles para reclamar!", ephemeral=True)
            return
        options = []
        for vc, data in available_vcs:
            owner_mention = f"<{data['owner']}>" if data['owner'] else "Desconocido"
            options.append(SelectOption(label=f"{vc.name} (anterior: {owner_mention})", value=str(vc.id)))
        dropdown = VCSelectDropdown(options, "Selecciona el canal de voz para reclamar", self.claim_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona el canal de voz para reclamar:", view=view, ephemeral=True)
    
    async def claim_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc_id = int(selected[0])
        vc = interaction.guild.get_channel(vc_id)
        if not vc:
            await interaction.followup.send("¡El canal de voz ya no existe!", ephemeral=True)
            return
        self.cog.private_channels[vc.id]["owner"] = interaction.user.id
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"¡Has reclamado {vc.mention}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def transfer(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        options = []
        for member in vc.members:
            if member.id != interaction.user.id:
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("¡No hay usuarios a quienes transferir en tu canal de voz!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Selecciona el nuevo propietario", self.transfer_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona el nuevo propietario:", view=view, ephemeral=True)
    
    async def transfer_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        new_owner_id = int(selected[0])
        new_owner = interaction.guild.get_member(new_owner_id)
        if not new_owner:
            await interaction.followup.send("¡Usuario no encontrado!", ephemeral=True)
            return
        self.cog.private_channels[vc.id]["owner"] = new_owner_id
        await self.cog.save_private_channel(vc.id, interaction.guild.id, self.cog.private_channels[vc.id])
        await interaction.followup.send(f"¡Se transfirió la propiedad de {vc.mention} a {new_owner.mention}!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def delete_vc(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.followup.send("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        for member in vc.members:
            try: await member.move_to(None)
            except: pass
        await vc.delete()
        if vc.id in self.cog.private_channels:
            del self.cog.private_channels[vc.id]
            await self.cog.delete_private_channel(vc.id)
        await interaction.followup.send("¡Tu canal de voz privado ha sido eliminado!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)
    
    async def block(self, interaction: discord.Interaction):
        vc = await self.get_owned_vc(interaction)
        if not vc:
            await interaction.response.send_message("¡No eres dueño de ningún canal de voz privado!", ephemeral=True)
            return
        options = []
        for member in interaction.guild.members:
            if (member not in vc.members and not member.bot and member != interaction.user):
                options.append(SelectOption(label=member.name, value=str(member.id)))
        if not options:
            await interaction.response.send_message("¡No hay miembros disponibles para bloquear!", ephemeral=True)
            return
        dropdown = UserSelectDropdown(options, "Selecciona miembros para bloquear", self.block_selected)
        view = ui.View()
        view.add_item(dropdown)
        await interaction.response.send_message("Selecciona miembros para bloquear:", view=view, ephemeral=True)
    
    async def block_selected(self, interaction: discord.Interaction, selected: List[str]):
        await interaction.response.defer(ephemeral=True)
        vc = await self.get_owned_vc(interaction)
        if not vc: return
        for user_id in selected:
            await self.cog.block_user(vc.id, int(user_id))
        await interaction.followup.send("¡Se bloqueó a los miembros seleccionados para que no se unan!", ephemeral=True)
        await self.cog.update_control_panel(interaction.guild)


class UserSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], placeholder: str, callback):
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=len(options))
        self.callback_func = callback
    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values)

class RegionSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], vc: discord.VoiceChannel):
        super().__init__(placeholder="Selecciona una región", options=options)
        self.vc = vc
    async def callback(self, interaction: discord.Interaction):
        region = self.values[0]
        try:
            await self.vc.edit(rtc_region=region if region != "auto" else None)
            await interaction.response.send_message(f"¡Región establecida en {self.values[0]}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"No se pudo establecer la región: {e}", ephemeral=True)

class VCSelectDropdown(ui.Select):
    def __init__(self, options: List[SelectOption], placeholder: str, callback):
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)
        self.callback_func = callback
    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values)

class SetLimitModal(ui.Modal, title="Establecer límite de usuarios del canal de voz"):
    def __init__(self, vc: discord.VoiceChannel):
        super().__init__()
        self.vc = vc
        self.limit = ui.TextInput(
            label="Límite de usuarios (0 sin límite)",
            placeholder="Ingresa un número entre 0 y 99",
            default=str(vc.user_limit) if vc.user_limit else "0",
            max_length=2
        )
        self.add_item(self.limit)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit.value)
            if limit < 0 or limit > 99:
                raise ValueError
            await self.vc.edit(user_limit=limit if limit != 0 else None)
            cog = interaction.client.get_cog("JoinToCreate")
            if cog and self.vc.id in cog.private_channels:
                cog.private_channels[self.vc.id]["limit"] = limit
                await cog.save_private_channel(self.vc.id, interaction.guild.id, cog.private_channels[self.vc.id])
            await interaction.response.send_message(f"¡Límite de usuarios establecido en {limit if limit != 0 else 'sin límite'}!", ephemeral=True)
            await cog.update_control_panel(interaction.guild)
        except:
            await interaction.response.send_message("¡Límite inválido! Ingresa un número entre 0 y 99.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(JoinToCreate(bot))