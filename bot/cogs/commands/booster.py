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
from utils.emoji import CROSS, NITRO_BOOST, TICK, TIMER
import asyncio 
import logging 
import aiosqlite 
import json 
from discord .ext import commands 
from utils .Tools import *
from discord .ext .commands import Context 
from discord import app_commands 
import time 
import datetime 
import re 
from typing import *
from time import strftime 
from core import Cog ,zyrox ,Context 
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

logging .basicConfig (
level =logging .INFO ,
format ="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
datefmt ="%H:%M:%S",
)

class Booster (Cog ):
    def __init__ (self ,bot : Zyrox ):
        self .bot =bot 
        self .color =0xFF0000 
        self .db_path ="db/boost.db"
        self .bot .loop .create_task (self .setup_database ())


        self .url_pattern =re .compile (
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',re .IGNORECASE 
        )


 
    async def setup_database (self ):
        """Initialize boost database tables"""
        async with aiosqlite .connect (self .db_path )as db :
            await db .execute ("""
                CREATE TABLE IF NOT EXISTS boost_config (
                    guild_id INTEGER PRIMARY KEY,
                    config TEXT NOT NULL
                )
            """)
            await db .commit ()

    async def get_boost_config (self ,guild_id :int )->dict :
        """Get boost configuration for a guild"""
        async with aiosqlite .connect (self .db_path )as db :
            async with db .execute ("SELECT config FROM boost_config WHERE guild_id = ?",(guild_id ,))as cursor :
                row =await cursor .fetchone ()
                if row :
                    return json .loads (row [0 ])


                default_config ={
                "boost":{
                "channel":[],
                "message":"¡{user.mention} acaba de impulsar {server.name}! 🎉",
                "embed":True ,
                "ping":False ,
                "image":"",
                "thumbnail":"",
                "autodel":0 
                },
                "boost_roles":{
                "roles":[]
                }
                }
                await self .update_boost_config (guild_id ,default_config )
                return default_config 

    async def update_boost_config (self ,guild_id :int ,config :dict ):
        """Update boost configuration for a guild"""
        async with aiosqlite .connect (self .db_path )as db :
            await db .execute (
            "INSERT OR REPLACE INTO boost_config (guild_id, config) VALUES (?, ?)",
            (guild_id ,json .dumps (config ))
            )
            await db .commit ()

    def is_authorized (self ,ctx )->bool :
        """Check if user is authorized to use admin commands"""
        return (
        ctx .author ==ctx .guild .owner 
        or ctx .author .guild_permissions .administrator 
        or ctx .author .top_role .position >=ctx .guild .me .top_role .position 
        )


    def format_boost_message (self ,message :str ,user :discord .Member ,guild :discord .Guild )->str :
        """Format boost message with new variable style"""
        replacements ={

        "{server.name}":guild .name ,
        "{server.id}":str (guild .id ),
        "{server.owner}":str (guild .owner ),
        "{server.icon}":guild .icon .url if guild .icon else "",
        "{server.boost_count}":str (guild .premium_subscription_count ),
        "{server.boost_level}":f"Nivel {guild.premium_tier}",
        "{server.member_count}":str (guild .member_count ),


        "{user.name}":user .display_name ,
        "{user.mention}":user .mention ,
        "{user.tag}":str (user ),
        "{user.id}":str (user .id ),
        "{user.avatar}":user .display_avatar .url ,
        "{user.created_at}":f"<t:{int(user.created_at.timestamp())}:F>",
        "{user.joined_at}":f"<t:{int(user.joined_at.timestamp())}:F>"if user .joined_at else "Desconocido",
        "{user.top_role}":user .top_role .name if user .top_role else "Ninguno",
        "{user.is_booster}":str (bool (user .premium_since )),
        "{user.is_mobile}":str (user .is_on_mobile ()),
        "{user.boosted_at}":f"<t:{int(user.premium_since.timestamp())}:F>"if user .premium_since else "Desconocido"
        }


        for old ,new in replacements .items ():
            message =message .replace (old ,new )

        return message 

    async def send_permission_error (self ,ctx ):
        """Send permission error embed"""
        await ctx.send(view=CV2("Error de permisos", "```diff\n- Debes tener el permiso de Administrador.\n- Tu rol más alto debe estar por encima de mi rol más alto.\n```"))

    @commands .group (name ="boost",aliases =['bst'],invoke_without_command =True ,help ="Comandos de configuración del mensaje de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @_boost .command (name ="thumbnail",help ="Establece la miniatura del mensaje de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_thumbnail (self ,ctx ,thumbnail_url :str ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        if not self .url_pattern .match (thumbnail_url ):
            await ctx.send(view=CV2("Error", f"{CROSS} Proporciona una URL válida."))

            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["thumbnail"]=thumbnail_url 
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se actualizó correctamente la URL de la miniatura del impulso."))

    @_boost .command (name ="image",help ="Establece la imagen del mensaje de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_image (self ,ctx ,*,image_url :str ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        if not self .url_pattern .match (image_url ):
            await ctx.send(view=CV2("Error", f"{CROSS} Proporciona una URL válida."))

            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["image"]=image_url 
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se actualizó correctamente la URL de la imagen del impulso."))

    @_boost .command (name ="autodel",help ="Establece el temporizador de autoeliminación de los mensajes de impulso (0 para desactivar)")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_autodel (self ,ctx ,seconds :int ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        if seconds <0 :
            await ctx.send(view=CV2("Error", f"{CROSS} El temporizador de autoeliminación debe ser 0 o mayor."))

            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["autodel"]=seconds 
        await self .update_boost_config (ctx .guild .id ,data )

        description =f"{TICK} Temporizador de autoeliminación establecido en {seconds} segundos."
        if seconds ==0 :
            description =f"{TICK} La autoeliminación ha sido desactivada."

        await ctx.send(view=CV2("Éxito", description))

    @_boost .command (name ="message",help ="Establece el contenido del mensaje de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_message (self ,ctx ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 
        variables_text = (
            "Envía tu mensaje de impulso en este canal ahora.\n\n**Variables disponibles:**\n"
            "```\n"
            "{server.name}         - Nombre del servidor\n"
            "{server.id}           - ID del servidor\n"
            "{server.owner}        - Propietario del servidor\n"
            "{server.icon}         - URL del icono del servidor\n"
            "{server.boost_count}  - Cantidad actual de impulsos\n"
            "{server.boost_level}  - Nivel de impulso (p. ej., Nivel 2)\n"
            "{server.member_count} - Cantidad total de miembros\n\n"
            "{user.name}        - Nombre visible del impulsor\n"
            "{user.mention}     - Menciona al impulsor\n"
            "{user.tag}         - Etiqueta completa del impulsor\n"
            "{user.id}          - ID del impulsor\n"
            "{user.avatar}      - URL del avatar del impulsor\n"
            "{user.created_at}  - Cuándo se creó la cuenta\n"
            "{user.joined_at}   - Cuándo se unió el usuario al servidor\n"
            "{user.top_role}    - Nombre del rol más alto del impulsor\n"
            "{user.is_booster}  - Si es impulsor\n"
            "{user.is_mobile}   - Si está en móvil\n"
            "{user.boosted_at}  - Marca de tiempo del impulso\n"
            "```\n*Tienes 60 segundos para responder*"
        )
        await ctx.send(view=CV2(f"{TICK} Configuración del mensaje de impulso", variables_text))

        def check (m ):
            return m .author ==ctx .author and m .channel ==ctx .channel 

        try :
            message =await self .bot .wait_for ('message',check =check ,timeout =60.0 )
        except asyncio .TimeoutError :
            await ctx.send(view=CV2("Tiempo agotado", f"{TIMER} ¡Tiempo agotado! Inténtalo de nuevo."))

            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["message"]=message .content 
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se actualizó correctamente el mensaje de impulso."))

    @_boost .command (name ="embed",help ="Activa o desactiva el formato de embed para los mensajes de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_embed (self ,ctx ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["embed"]=not data ["boost"]["embed"]
        await self .update_boost_config (ctx .guild .id ,data )

        status ="activado"if data ["boost"]["embed"]else "desactivado"
        await ctx.send(view=CV2("Éxito", f"{TICK} El formato de embed ha sido **{status}**."))

    @_boost .command (name ="ping",help ="Activa o desactiva la mención al impulsor")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_ping (self ,ctx ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        data ["boost"]["ping"]=not data ["boost"]["ping"]
        await self .update_boost_config (ctx .guild .id ,data )

        status ="activado"if data ["boost"]["ping"]else "desactivado"
        await ctx.send(view=CV2("Éxito", f"{TICK} La mención al impulsor ha sido **{status}**."))

    @_boost .group (name ="channel",help ="Administra los canales de notificación de impulsos")
    @blacklist_check ()
    @ignore_check ()
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_channel (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @_boost_channel .command (name ="add",help ="Añade un canal de notificación de impulsos")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_channel_add (self ,ctx ,channel :discord .TextChannel ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        channels =data ["boost"]["channel"]

        if len (channels )>=3 :
            await ctx.send(view=CV2("Error", f"{CROSS} Se alcanzó el límite máximo de canales de impulso (3 canales)."))
            return 

        if str (channel .id )in channels :
            await ctx.send(view=CV2("Error", f"{CROSS} Este canal ya está en la lista de canales de impulso."))
            return 

        channels .append (str (channel .id ))
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se añadió {channel.mention} a la lista de canales de impulso."))

    @_boost_channel .command (name ="remove",help ="Elimina un canal de notificación de impulsos")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_channel_remove (self ,ctx ,channel :discord .TextChannel ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        channels =data ["boost"]["channel"]

        if not channels :
            await ctx.send(view=CV2("Error", f"{CROSS} No hay canales de impulso configurados actualmente."))
            return 

        if str (channel .id )not in channels :
            await ctx.send(view=CV2("Error", f"{CROSS} Este canal no está en la lista de canales de impulso."))
            return 

        channels .remove (str (channel .id ))
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se eliminó {channel.mention} de la lista de canales de impulso."))

    @_boost .command (name ="test",help ="Prueba cómo se verá el mensaje de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boost_test (self ,ctx ):
        data =await self .get_boost_config (ctx .guild .id )
        channels =data ["boost"]["channel"]

        if not channels :
            await ctx.send(view=CV2("Error", f"{CROSS} Configura primero un canal de impulso con `boost channel add #channel`."))
            return 


        formatted_message =self .format_boost_message (data ["boost"]["message"],ctx .author ,ctx .guild )


        channel =self .bot .get_channel (int (channels [0 ]))
        if not channel :
            await ctx.send(view=CV2("Error", f"{CROSS} El canal de impulso configurado ya no existe."))

            return 

        try :
            if data ["boost"]["embed"]:
                embed =discord .Embed (description =formatted_message ,color =self .color )
                embed .set_author (name =ctx .author .display_name ,icon_url =ctx .author .display_avatar .url )
                embed .timestamp =discord .utils .utcnow ()

                if data ["boost"]["image"]:
                    embed .set_image (url =data ["boost"]["image"])

                if data ["boost"]["thumbnail"]:
                    embed .set_thumbnail (url =data ["boost"]["thumbnail"])

                if ctx .guild .icon :
                    embed .set_footer (text =ctx .guild .name ,icon_url =ctx .guild .icon .url )

                ping_content =ctx .author .mention if data ["boost"]["ping"]else ""
                await channel .send (ping_content ,embed =embed )
            else :
                await channel .send (formatted_message )

        except discord .Forbidden :
            await ctx.send(view=CV2("Error", f"{CROSS} No tengo permiso para enviar mensajes en el canal de impulso."))

        except Exception as e :
            await ctx.send(view=CV2("Error", f"{CROSS} Ocurrió un error: `{str(e)}`"))


    @_boost .command (name ="config",help ="Muestra la configuración actual de impulsos")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def _boost_config (self ,ctx ):
        data =await self .get_boost_config (ctx .guild .id )
        channels =data ["boost"]["channel"]

        if not channels :
            await ctx.send(view=CV2("Error", f"{CROSS} Configura primero un canal de impulso con `boost channel add #channel`."))

            return 

        channel_mentions =[]
        for channel_id in channels :
            channel =self .bot .get_channel (int (channel_id ))
            if channel :
                channel_mentions .append (channel .mention )

        embed_status = f"{TICK} Activado" if data["boost"]["embed"] else f"{CROSS} Desactivado"
        ping_status = f"{TICK} Activado" if data["boost"]["ping"] else f"{CROSS} Desactivado"
        autodel_status = f"{data['boost']['autodel']}s" if data["boost"]["autodel"] else "Desactivado"
        channels_str = "\n".join(channel_mentions) if channel_mentions else "Ninguno"

        config_text = (
            f"**Canales**\n{channels_str}\n\n"
            f"**Mensaje**\n```{data['boost']['message']}```\n"
            f"**Embed:** {embed_status}\n"
            f"**Mención:** {ping_status}\n"
            f"**Autoeliminación:** {autodel_status}"
        )

        await ctx.send(view=CV2(f"{NITRO_BOOST} Configuración de impulsos de {ctx.guild.name}", config_text))

    @_boost .command (name ="reset",help ="Restablece la configuración de impulsos")
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def _boost_reset (self ,ctx ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )

        if not data ["boost"]["channel"]:
            await ctx.send(view=CV2("Error", f"{CROSS} No se encontró configuración de impulsos para restablecer."))
            return 


        data ["boost"]["channel"]=[]
        data ["boost"]["image"]=""
        data ["boost"]["message"]="¡{user.mention} acaba de impulsar {server.name}! 🎉"
        data ["boost"]["thumbnail"]=""
        data ["boost"]["embed"]=True 
        data ["boost"]["ping"]=False 
        data ["boost"]["autodel"]=0 

        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se restableció correctamente toda la configuración de impulsos."))

    @commands .group (name ="boostrole",invoke_without_command =True ,help ="Administra los roles de impulso")
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @blacklist_check ()
    @ignore_check ()
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boostrole (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @_boostrole .command (name ="config",help ="Muestra la configuración de roles de impulso")
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def _boostrole_config (self ,ctx ):
        data =await self .get_boost_config (ctx .guild .id )
        role_ids =data ["boost_roles"]["roles"]

        if not role_ids :
            await ctx.send(view=CV2(f"Roles de impulso - {ctx.guild.name}", "No hay roles de impulso configurados."))
            return 

        roles =[]
        for role_id in role_ids :
            role =ctx .guild .get_role (int (role_id ))
            if role :
                roles .append (role .mention )

        roles_str = "\n".join(roles) if roles else "No se encontraron roles válidos"
        await ctx.send(view=CV2(f"Roles de impulso - {ctx.guild.name}", roles_str))

    @_boostrole .command (name ="add",help ="Añade un rol de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boostrole_add (self ,ctx ,role :discord .Role ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        roles =data ["boost_roles"]["roles"]

        if len (roles )>=10 :
            await ctx.send(view=CV2("Error", f"{CROSS} Se alcanzó el límite máximo de roles de impulso (10 roles)."))
            return 

        if str (role .id )in roles :
            await ctx.send(view=CV2("Error", f"{CROSS} {role.mention} ya es un rol de impulso."))
            return 

        roles .append (str (role .id ))
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} {role.mention} se añadió como rol de impulso."))

    @_boostrole .command (name ="remove",help ="Elimina un rol de impulso")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def _boostrole_remove (self ,ctx ,role :discord .Role ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )
        roles =data ["boost_roles"]["roles"]

        if not roles :
            await ctx.send(view=CV2("Error", f"{CROSS} No hay roles de impulso configurados actualmente."))
            return 

        if str (role .id )not in roles :
            await ctx.send(view=CV2("Error", f"{CROSS} {role.mention} no es un rol de impulso."))
            return 

        roles .remove (str (role .id ))
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} {role.mention} se eliminó de los roles de impulso."))

    @_boostrole .command (name ="reset",help ="Restablece la configuración de roles de impulso")
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def _boostrole_reset (self ,ctx ):
        if not self .is_authorized (ctx ):
            await self .send_permission_error (ctx )
            return 

        data =await self .get_boost_config (ctx .guild .id )

        if not data ["boost_roles"]["roles"]:
            await ctx.send(view=CV2("Error", f"{CROSS} No hay roles de impulso configurados actualmente."))
            return 

        data ["boost_roles"]["roles"]=[]
        await self .update_boost_config (ctx .guild .id ,data )

        await ctx.send(view=CV2("Éxito", f"{TICK} Se eliminaron correctamente todos los roles de impulso."))

async def setup (bot ):
    await bot .add_cog (Booster(bot ))