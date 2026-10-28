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
from utils.emoji import TICK
from discord .ext import commands 
from discord import app_commands 
import aiosqlite 
import random 
import string 
import io 
from PIL import Image ,ImageDraw ,ImageFont 
import asyncio 
import logging 
from datetime import datetime ,timezone ,timedelta 
from typing import Optional 
from utils .Tools import *


logger =logging .getLogger ('discord')

DATABASE_PATH ='db/verification.db'


DISCORD_COLORS ={
'primary':0xFF0000 ,
'success':0xFF0000 ,
'warning':0xFF0000 ,
'error':0xFF0000 ,
'secondary':0xFF0000 ,
'neutral':0xFF0000 
}


def utc_to_ist (dt :datetime )->datetime :
    ist_offset =timedelta (hours =5 ,minutes =30 )
    return dt .replace (tzinfo =timezone .utc ).astimezone (timezone (ist_offset ))


async def check_bot_permissions (guild :discord .Guild ,channel =None )->dict :
    """Check if bot has necessary permissions"""
    bot_member =guild .me 
    required_perms ={
    'guild':['manage_roles','manage_channels','send_messages','manage_messages'],
    'channel':['view_channel','send_messages','attach_files','embed_links','manage_messages']
    }

    missing_perms ={'guild':[],'channel':[]}


    for perm in required_perms ['guild']:
        if not getattr (bot_member .guild_permissions ,perm ):
            missing_perms ['guild'].append (perm .replace ('_',' ').title ())


    if channel and hasattr (channel ,'permissions_for'):
        channel_perms =channel .permissions_for (bot_member )
        for perm in required_perms ['channel']:
            if not getattr (channel_perms ,perm ):
                missing_perms ['channel'].append (perm .replace ('_',' ').title ())

    return missing_perms 


def validate_role_hierarchy (guild :discord .Guild ,role :discord .Role )->bool :
    """Check if bot can manage the specified role"""
    bot_top_role =guild .me .top_role 
    return bot_top_role .position >role .position 

async def create_verified_role (guild :discord .Guild )->discord .Role :
    """Create a verified role with proper permissions"""
    try :

        existing_role =discord .utils .get (guild .roles ,name ="Verified")
        if existing_role :
            return existing_role 


        verified_role =await guild .create_role (
        name ="Verified",
        color =discord .Color .from_rgb (35 ,165 ,90 ),
        reason ="Auto-created for verification system",
        permissions =discord .Permissions (
        read_messages =True ,
        send_messages =True ,
        read_message_history =True ,
        use_external_emojis =True ,
        add_reactions =True ,
        attach_files =True ,
        embed_links =True ,
        connect =True ,
        speak =True ,
        use_voice_activation =True 
        )
        )


        bot_roles =[role for role in guild .roles if role .managed and role .members and guild .me in role .members ]
        position =1 
        if bot_roles :
            position =min (role .position for role in bot_roles )-1 

        await verified_role .edit (position =max (1 ,position ))

        return verified_role 
    except Exception as e :
        logger .error (f"Error creating verified role: {e}")
        raise 

async def auto_fix_permissions (guild :discord .Guild ,verification_channel :discord .TextChannel ,verified_role :discord .Role ):
    """Automatically fix channel permissions for verification system"""
    try :
        everyone_role =guild .default_role 
        bot_member =guild .me 
        failed_channels =[]


        try :
            await verification_channel .set_permissions (
            everyone_role ,
            view_channel =True ,
            send_messages =False ,
            add_reactions =False ,
            reason ="Auto-fix: Verification channel permissions"
            )
            await verification_channel .set_permissions (
            verified_role ,
            view_channel =False ,
            reason ="Auto-fix: Hide verification from verified users"
            )
            await verification_channel .set_permissions (
            bot_member ,
            view_channel =True ,
            send_messages =True ,
            manage_messages =True ,
            embed_links =True ,
            attach_files =True ,
            reason ="Auto-fix: Bot verification permissions"
            )
        except discord .Forbidden :
            logger .warning (f"Cannot fix permissions for verification channel: {verification_channel.name}")


        for channel in guild .channels :
            if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                if channel .id !=verification_channel .id :
                    try :

                        current_overwrites =channel .overwrites 


                        everyone_perms =current_overwrites .get (everyone_role )
                        if not everyone_perms or everyone_perms .view_channel is not False :
                            await channel .set_permissions (
                            everyone_role ,
                            view_channel =False ,
                            reason ="Auto-fix: Verification system privacy"
                            )


                        verified_perms =current_overwrites .get (verified_role )
                        if not verified_perms or verified_perms .view_channel is not True :
                            await channel .set_permissions (
                            verified_role ,
                            view_channel =True ,
                            reason ="Auto-fix: Verified role access"
                            )
                    except discord .Forbidden :
                        failed_channels .append (channel .name )

        if failed_channels :
            logger .warning (f"Failed to auto-fix permissions for channels: {', '.join(failed_channels)}")

        return len (failed_channels )

    except Exception as e :
        logger .error (f"Error in auto-fix permissions: {e}")
        return -1 

class VerificationModal (discord .ui .Modal ,title ="Ingresa el código de verificación"):
    def __init__ (self ,bot ,captcha_code :str ,guild_id :int ):
        super ().__init__ ()
        self .bot =bot 
        self .captcha_code =captcha_code 
        self .guild_id =guild_id 

    captcha_input =discord .ui .TextInput (
    label ="Código de verificación",
    placeholder ="Ingresa el código de 6 caracteres de la imagen",
    required =True ,
    max_length =6 ,
    min_length =6 
    )

    async def on_submit (self ,interaction :discord .Interaction ):
        try :
            if self .captcha_input .value .strip ()!=self .captcha_code :
                embed =discord .Embed (
                title ="Código incorrecto",
                description ="El código que ingresaste es incorrecto. Vuelve a intentarlo haciendo clic en el botón de verificación del servidor.",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )
                return 

            guild =self .bot .get_guild (self .guild_id )
            if not guild :
                await interaction .response .send_message ("Servidor no encontrado.",ephemeral =True )
                return 

            member =guild .get_member (interaction .user .id )
            if not member :
                await interaction .response .send_message ("No estás en el servidor.",ephemeral =True )
                return 


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await interaction .response .send_message ("El sistema de verificación no está configurado.",ephemeral =True )
                        return 

                    verified_role =guild .get_role (result [0 ])
                    if not verified_role :
                        await interaction .response .send_message ("No se encontró el rol verificado.",ephemeral =True )
                        return 


                    if verified_role in member .roles :
                        embed =discord .Embed (
                        title ="Ya estás verificado",
                        description ="¡Ya estás verificado en este servidor!",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            await member .add_roles (verified_role ,reason ="CAPTCHA verification completed")


            await self .log_verification (guild .id ,member .id ,"captcha")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Verificación exitosa",
            description =f"¡Bienvenido a **{guild.name}**!\n\n"
            f"Te has verificado correctamente y ahora puedes acceder a todos los canales.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verificado a las {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )


            await self .send_verification_log (guild ,member ,"CAPTCHA",True )

        except discord .Forbidden :
            await interaction .response .send_message ("El bot no tiene permiso para asignar roles.",ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verification modal: {e}")
            pass 

    async def log_verification (self ,guild_id :int ,user_id :int ,method :str ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    current_time =utc_to_ist (discord .utils .utcnow ())
                    await cur .execute (
                    "INSERT INTO verification_logs (guild_id, user_id, verification_method, verified_at) VALUES (?, ?, ?, ?)",
                    (guild_id ,user_id ,method ,current_time .isoformat ())
                    )
                    await db .commit ()
        except Exception as e :
            logger .error (f"Error logging verification: {e}")

    async def send_verification_log (self ,guild :discord .Guild ,user :discord .Member ,method :str ,success :bool ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT log_channel_id FROM verification_config WHERE guild_id = ?",
                    (guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if result and result [0 ]:
                        log_channel =guild .get_channel (result [0 ])
                        if log_channel and log_channel .permissions_for (guild .me ).send_messages :
                            current_time =utc_to_ist (discord .utils .utcnow ())
                            embed =discord .Embed (
                            title ="Registro de verificación de usuario",
                            color =DISCORD_COLORS ['success']if success else DISCORD_COLORS ['error'],
                            timestamp =current_time 
                            )
                            embed .add_field (
                            name ="Información del usuario",
                            value =f"**Usuario:** {user.mention}\n**ID:** {user.id}\n**Nombre de usuario:** {user.name}",
                            inline =False 
                            )
                            embed .add_field (
                            name ="Detalles de la verificación",
                            value =f"**Método:** {method}\n**Estado:** {'Correcto' if success else 'Fallido'}\n**Hora:** {current_time.strftime('%I:%M %p IST')}",
                            inline =False 
                            )
                            embed .set_thumbnail (url =user .avatar .url if user .avatar else user .default_avatar .url )
                            await log_channel .send (embed =embed )
        except Exception as e :
            logger .error (f"Error sending verification log: {e}")

class VerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Verificación rápida",style =discord .ButtonStyle .green ,custom_id ="verify_button_quick")
    async def verify_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id, verification_method FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Sistema no disponible",
                        description ="El sistema de verificación no está configurado o está desactivado.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    verification_method =result [1 ]

                    if not verified_role :
                        embed =discord .Embed (
                        description ="No se encontró el rol verificado. Contacta a un administrador.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Ya estás verificado",
                        description ="¡Ya estás verificado! Puedes acceder a todos los canales.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            if verification_method not in ["button","both"]:
                embed =discord .Embed (
                title ="CAPTCHA requerido",
                description ="Este servidor requiere verificación por CAPTCHA. Usa el botón de CAPTCHA que aparece abajo.",
                color =DISCORD_COLORS ['warning']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )
                return 


            await interaction .user .add_roles (verified_role ,reason ="Quick button verification")


            modal =VerificationModal (self .bot ,"",interaction .guild .id )
            await modal .log_verification (interaction .guild .id ,interaction .user .id ,"button")
            await modal .send_verification_log (interaction .guild ,interaction .user ,"BUTTON",True )

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Bienvenido al servidor",
            description =f"¡**{interaction.user.mention}** se ha verificado!\n\n"
            f"¡Bienvenido a {interaction.guild.name}!\n"
            f"Ahora tienes acceso a todos los canales.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verificado a las {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )

        except discord .Forbidden :
            embed =discord .Embed (
            description ="El bot no tiene permiso para asignar roles. Contacta a un administrador.",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verify button: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    @discord .ui .button (label ="Verificar con CAPTCHA",style =discord .ButtonStyle .primary ,custom_id ="verify_captcha_secure")
    async def verify_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Sistema no disponible",
                        description ="El sistema de verificación no está configurado o está desactivado.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    if not verified_role :
                        embed =discord .Embed (
                        description ="No se encontró el rol verificado. Contacta a un administrador.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Ya estás verificado",
                        description ="¡Ya estás verificado! Puedes acceder a todos los canales.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            captcha_code =self .generate_captcha_code ()
            captcha_image =self .create_captcha_image (captcha_code )

            try :

                file =discord .File (captcha_image ,filename ="captcha.png")
                embed =discord .Embed (
                title ="Verificación por CAPTCHA",
                description =f"**Servidor:** {interaction.guild.name}\n\n"
                f"Resuelve el CAPTCHA de abajo para verificarte.\n"
                f"Haz clic en el botón de abajo para ingresar tu respuesta.\n\n"
                f"**Importante:** ¡El código distingue entre mayúsculas y minúsculas!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_image (url ="attachment://captcha.png")
                embed .set_footer (text ="Este CAPTCHA expirará en 10 minutos")

                modal =VerificationModal (self .bot ,captcha_code ,interaction .guild .id )
                view =CaptchaModalView (modal )

                await interaction .user .send (embed =embed ,file =file ,view =view )


                embed =discord .Embed (
                title ="Revisa tus mensajes directos",
                description ="Te envié un CAPTCHA por mensaje directo.\n\n"
                f"**Pasos:**\n"
                f"1. Revisa mis mensajes directos\n"
                f"2. Resuelve la imagen del CAPTCHA\n"
                f"3. Haz clic en el botón para ingresar tu respuesta\n\n"
                f"¡Asegúrate de tener los mensajes directos abiertos!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_footer (text ="El CAPTCHA expira en 10 minutos")
                await interaction .response .send_message (embed =embed ,ephemeral =True )

            except discord .Forbidden :
                embed =discord .Embed (
                title ="Mensajes directos desactivados",
                description ="¡No pude enviarte un mensaje directo! Activa los mensajes directos de miembros del servidor e inténtalo de nuevo.\n\n"
                f"**Cómo activar los mensajes directos:**\n"
                f"1. Haz clic derecho en **{interaction.guild.name}**\n"
                f"2. Ve a **Configuración de privacidad**\n"
                f"3. Activa **Mensajes directos**\n"
                f"4. Vuelve a intentar la verificación",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error in verify captcha: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    def generate_captcha_code (self )->str :
        """Generate a random 6-character alphanumeric code"""
        return ''.join (random .choices (string .ascii_letters +string .digits ,k =6 ))

    def create_captcha_image (self ,code :str )->io .BytesIO :
        """Create a CAPTCHA image with the given code"""

        width ,height =300 ,120 
        image =Image .new ('RGB',(width ,height ),color ='white')
        draw =ImageDraw .Draw (image )


        for y in range (height ):
            color_value =255 -int ((y /height )*50 )
            for x in range (width ):
                draw .point ((x ,y ),fill =(color_value ,color_value ,255 ))


        for _ in range (200 ):
            x =random .randint (0 ,width )
            y =random .randint (0 ,height )
            draw .point ((x ,y ),fill =(random .randint (150 ,200 ),random .randint (150 ,200 ),random .randint (150 ,200 )))


        for _ in range (8 ):
            x1 =random .randint (0 ,width )
            y1 =random .randint (0 ,height )
            x2 =random .randint (0 ,width )
            y2 =random .randint (0 ,height )
            draw .line ([(x1 ,y1 ),(x2 ,y2 )],fill =(random .randint (100 ,150 ),random .randint (100 ,150 ),random .randint (100 ,150 )),width =2 )


        try :
            font =ImageFont .truetype ("utils/arial.ttf",40 )
        except :
            try :
                font =ImageFont .load_default ()
            except :
                font =None 


        if font :
            bbox =draw .textbbox ((0 ,0 ),code ,font =font )
            text_width =bbox [2 ]-bbox [0 ]
            text_height =bbox [3 ]-bbox [1 ]
        else :
            text_width =len (code )*20 
            text_height =20 

        start_x =(width -text_width )//2 
        start_y =(height -text_height )//2 


        for i ,char in enumerate (code ):
            char_x =start_x +(i *text_width //len (code ))+random .randint (-8 ,8 )
            char_y =start_y +random .randint (-15 ,15 )


            color =(random .randint (0 ,100 ),random .randint (0 ,100 ),random .randint (0 ,100 ))

            if font :
                draw .text ((char_x ,char_y ),char ,fill =color ,font =font )
            else :
                draw .text ((char_x ,char_y ),char ,fill =color )


        draw .rectangle ([(0 ,0 ),(width -1 ,height -1 )],outline ='black',width =2 )


        img_buffer =io .BytesIO ()
        image .save (img_buffer ,format ='PNG',quality =95 )
        img_buffer .seek (0 )

        return img_buffer 



class CaptchaOnlyVerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Verificar con CAPTCHA",style =discord .ButtonStyle .primary ,custom_id ="verify_captcha_only")
    async def verify_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Sistema no disponible",
                        description ="El sistema de verificación no está configurado o está desactivado.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    if not verified_role :
                        embed =discord .Embed (
                        description ="No se encontró el rol verificado. Contacta a un administrador.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Ya estás verificado",
                        description ="¡Ya estás verificado! Puedes acceder a todos los canales.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            captcha_code =self .generate_captcha_code ()
            captcha_image =self .create_captcha_image (captcha_code )

            try :

                file =discord .File (captcha_image ,filename ="captcha.png")
                embed =discord .Embed (
                title ="Verificación por CAPTCHA",
                description =f"**Servidor:** {interaction.guild.name}\n\n"
                f"Resuelve el CAPTCHA de abajo para verificarte.\n"
                f"Haz clic en el botón de abajo para ingresar tu respuesta.\n\n"
                f"**Importante:** ¡El código distingue entre mayúsculas y minúsculas!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_image (url ="attachment://captcha.png")
                embed .set_footer (text ="Este CAPTCHA expirará en 10 minutos")

                modal =VerificationModal (self .bot ,captcha_code ,interaction .guild .id )
                view =CaptchaModalView (modal )

                await interaction .user .send (embed =embed ,file =file ,view =view )


                embed =discord .Embed (
                title ="Revisa tus mensajes directos",
                description ="Te envié un CAPTCHA por mensaje directo.\n\n"
                f"**Pasos:**\n"
                f"1. Revisa mis mensajes directos\n"
                f"2. Resuelve la imagen del CAPTCHA\n"
                f"3. Haz clic en el botón para ingresar tu respuesta\n\n"
                f"¡Asegúrate de tener los mensajes directos abiertos!",
                color =DISCORD_COLORS ['secondary']
                )
                embed .set_footer (text ="El CAPTCHA expira en 10 minutos")
                await interaction .response .send_message (embed =embed ,ephemeral =True )

            except discord .Forbidden :
                embed =discord .Embed (
                title ="Mensajes directos desactivados",
                description ="¡No pude enviarte un mensaje directo! Activa los mensajes directos de miembros del servidor e inténtalo de nuevo.\n\n"
                f"**Cómo activar los mensajes directos:**\n"
                f"1. Haz clic derecho en **{interaction.guild.name}**\n"
                f"2. Ve a **Configuración de privacidad**\n"
                f"3. Activa **Mensajes directos**\n"
                f"4. Vuelve a intentar la verificación",
                color =DISCORD_COLORS ['error']
                )
                await interaction .response .send_message (embed =embed ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error in verify captcha: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

    def generate_captcha_code (self )->str :
        """Generate a random 6-character alphanumeric code"""
        return ''.join (random .choices (string .ascii_letters +string .digits ,k =6 ))

    def create_captcha_image (self ,code :str )->io .BytesIO :
        """Create a CAPTCHA image with the given code"""

        width ,height =300 ,120 
        image =Image .new ('RGB',(width ,height ),color ='white')
        draw =ImageDraw .Draw (image )


        for y in range (height ):
            color_value =255 -int ((y /height )*50 )
            for x in range (width ):
                draw .point ((x ,y ),fill =(color_value ,color_value ,255 ))


        for _ in range (200 ):
            x =random .randint (0 ,width )
            y =random .randint (0 ,height )
            draw .point ((x ,y ),fill =(random .randint (150 ,200 ),random .randint (150 ,200 ),random .randint (150 ,200 )))


        for _ in range (8 ):
            x1 =random .randint (0 ,width )
            y1 =random .randint (0 ,height )
            x2 =random .randint (0 ,width )
            y2 =random .randint (0 ,height )
            draw .line ([(x1 ,y1 ),(x2 ,y2 )],fill =(random .randint (100 ,150 ),random .randint (100 ,150 ),random .randint (100 ,150 )),width =2 )


        try :
            font =ImageFont .truetype ("utils/arial.ttf",40 )
        except :
            try :
                font =ImageFont .load_default ()
            except :
                font =None 


        if font :
            bbox =draw .textbbox ((0 ,0 ),code ,font =font )
            text_width =bbox [2 ]-bbox [0 ]
            text_height =bbox [3 ]-bbox [1 ]
        else :
            text_width =len (code )*20 
            text_height =20 

        start_x =(width -text_width )//2 
        start_y =(height -text_height )//2 


        for i ,char in enumerate (code ):
            char_x =start_x +(i *text_width //len (code ))+random .randint (-8 ,8 )
            char_y =start_y +random .randint (-15 ,15 )


            color =(random .randint (0 ,100 ),random .randint (0 ,100 ),random .randint (0 ,100 ))

            if font :
                draw .text ((char_x ,char_y ),char ,fill =color ,font =font )
            else :
                draw .text ((char_x ,char_y ),char ,fill =color )


        draw .rectangle ([(0 ,0 ),(width -1 ,height -1 )],outline ='black',width =2 )


        img_buffer =io .BytesIO ()
        image .save (img_buffer ,format ='PNG',quality =95 )
        img_buffer .seek (0 )

        return img_buffer 

class CaptchaModalView (discord .ui .View ):
    def __init__ (self ,modal :VerificationModal ):
        super ().__init__ (timeout =600 )
        self .modal =modal 

    @discord .ui .button (label ="Ingresar código",style =discord .ButtonStyle .secondary ,custom_id ="enter_captcha_code")
    async def enter_captcha (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        await interaction .response .send_modal (self .modal )

class VerificationSetupView (discord .ui .View ):
    def __init__ (self ,bot ,ctx ):
        super ().__init__ (timeout =300 )
        self .bot =bot 
        self .ctx =ctx 
        self .verification_channel =None 
        self .log_channel =None 
        self .verification_method ="both"

    @discord .ui .select (
    cls =discord .ui .ChannelSelect ,
    channel_types =[discord .ChannelType .text ],
    placeholder ="Selecciona el canal de verificación..."
    )
    async def verification_channel_select (self ,interaction :discord .Interaction ,select :discord .ui .ChannelSelect ):
        await interaction .response .defer ()
        selected_channel =select .values [0 ]
        self .verification_channel =interaction .guild .get_channel (selected_channel .id )

    @discord .ui .select (
    cls =discord .ui .ChannelSelect ,
    channel_types =[discord .ChannelType .text ],
    placeholder ="Selecciona el canal de registros (opcional)..."
    )
    async def log_channel_select (self ,interaction :discord .Interaction ,select :discord .ui .ChannelSelect ):
        await interaction .response .defer ()
        selected_channel =select .values [0 ]
        self .log_channel =interaction .guild .get_channel (selected_channel .id )

    @discord .ui .select (
    placeholder ="Selecciona el método de verificación...",
    options =[
    discord .SelectOption (
    label ="Solo botón rápido",
    value ="button",
    description ="Los usuarios se verifican al instante con un clic"
    ),
    discord .SelectOption (
    label ="Solo CAPTCHA",
    value ="captcha",
    description ="Los usuarios deben resolver un CAPTCHA (más seguro)"
    ),
    discord .SelectOption (
    label ="Ambos métodos",
    value ="both",
    description ="Los usuarios pueden elegir entre botón o CAPTCHA"
    )
    ]
    )
    async def method_select (self ,interaction :discord .Interaction ,select :discord .ui .Select ):
        await interaction .response .defer ()
        self .verification_method =select .values [0 ]

    @discord .ui .button (label ="Configurar sistema de verificación",style =discord .ButtonStyle .green )
    async def setup_verification (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        if not self .verification_channel :
            embed =discord .Embed (
            title ="Configuración incompleta",
            description ="¡Primero selecciona un canal de verificación!",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
            return 

        try :
            await interaction .response .defer (ephemeral =True )


            verified_role =await create_verified_role (interaction .guild )


            failed_count =await auto_fix_permissions (interaction .guild ,self .verification_channel ,verified_role )


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """INSERT OR REPLACE INTO verification_config 
                           (guild_id, verification_channel_id, verified_role_id, log_channel_id, verification_method, enabled) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                    interaction .guild .id ,
                    self .verification_channel .id ,
                    verified_role .id ,
                    self .log_channel .id if self .log_channel else None ,
                    self .verification_method ,
                    True 
                    )
                    )
                    await db .commit ()


            await self .send_verification_panel (verified_role )


            try :
                await asyncio .sleep (5 )
                if hasattr (interaction ,'message')and interaction .message :
                    await interaction .message .delete ()
            except discord .NotFound :
                pass 
            except discord .Forbidden :
                pass 
            except Exception as e :
                logger .error (f"Error deleting setup embed: {e}")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Configuración del sistema de verificación completada",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .add_field (
            name ="Resumen de la configuración",
            value =f"**Canal de verificación:** {self.verification_channel.mention}\n"
            f"**Rol verificado:** {verified_role.mention}\n"
            f"**Canal de registros:** {self.log_channel.mention if self.log_channel else 'Ninguno'}\n"
            f"**Método:** {dict(button='Botón', captcha='CAPTCHA', both='Ambos', manual='Manual').get(self.verification_method, self.verification_method)}",
            inline =False 
            )

            security_features ="Todos los canales ocultos para usuarios sin verificar\n" "Canal de verificación bloqueado para usuarios sin verificar\n" "Eliminación automática de mensajes en el canal de verificación\n" "Sistema de CAPTCHA por mensaje directo\n" "Registro completo de actividad activado"

            if failed_count >0 :
                security_features +=f"\n\nNota: no se pudieron corregir automáticamente {failed_count} canales por permisos"

            embed .add_field (
            name ="Funciones de seguridad",
            value =security_features ,
            inline =False 
            )
            embed .add_field (
            name ="Estado del sistema",
            value =f"{TICK} **¡El sistema de verificación está ACTIVADO y listo para usar!**",
            inline =False 
            )
            embed .set_footer (text =f"Configuración completada y activada a las {current_time.strftime('%I:%M %p IST')}")


            await interaction .followup .send (embed =embed ,ephemeral =True )


            try :
                await asyncio .sleep (3 )
                if hasattr (interaction ,'message')and interaction .message :
                    await interaction .message .delete ()
            except discord .NotFound :
                pass 
            except discord .Forbidden :
                pass 
            except Exception as e :
                logger .error (f"Error deleting setup embed: {e}")

            self .stop ()

        except Exception as e :
            logger .error (f"Error setting up verification: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await interaction .followup .send (embed =embed ,ephemeral =True )

    async def send_verification_panel (self ,verified_role :discord .Role ):
        """Send the verification panel to the verification channel"""
        try :
            channel =self .verification_channel 
            current_time =utc_to_ist (discord .utils .utcnow ())

            embed =discord .Embed (
            title ="Verificación del servidor requerida",
            description =f"¡**Bienvenido a {channel.guild.name}!**\n\n"
            f"Para acceder a todos los canales y funciones, primero debes verificarte.\n\n"
            f"**Elige tu método de verificación:**",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )

            if self .verification_method in ["button","both"]:
                embed .add_field (
                name ="Verificación rápida",
                value ="¡Acceso instantáneo con un clic! Ideal para usuarios de confianza.",
                inline =True 
                )

            if self .verification_method in ["captcha","both"]:
                embed .add_field (
                name ="Verificación por CAPTCHA",
                value ="Verificación segura por mensaje directo. ¡Demuestra que eres humano!",
                inline =True 
                )

            embed .add_field (
            name ="¿Qué pasa después de verificarte?",
            value =f"• Acceso a todos los canales del servidor\n"
            f"• Posibilidad de chatear y participar\n"
            f"• Acceso a todas las funciones del servidor\n"
            f"• Rol **{verified_role.name}** asignado",
            inline =False 
            )

            embed .set_footer (text =f"Panel de verificación • {current_time.strftime('%I:%M %p IST')}")


            if self .verification_method =="button":
                view =ButtonOnlyVerificationView (self .bot )
            elif self .verification_method =="captcha":
                view =CaptchaOnlyVerificationView (self .bot )
            else :
                view =VerificationView (self .bot )

            await channel .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error sending verification panel: {e}")

class ButtonOnlyVerificationView (discord .ui .View ):
    def __init__ (self ,bot ):
        super ().__init__ (timeout =None )
        self .bot =bot 

    @discord .ui .button (label ="Verificar ahora",style =discord .ButtonStyle .green ,custom_id ="verify_button_only")
    async def verify_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        try :

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id, verification_method FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (interaction .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="Sistema no disponible",
                        description ="El sistema de verificación no está configurado o está desactivado.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 

                    verified_role =interaction .guild .get_role (result [0 ])
                    verification_method =result [1 ]

                    if not verified_role :
                        embed =discord .Embed (
                        description ="No se encontró el rol verificado. Contacta a un administrador.",
                        color =DISCORD_COLORS ['error']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


                    if verified_role in interaction .user .roles :
                        embed =discord .Embed (
                        title ="Ya estás verificado",
                        description ="¡Ya estás verificado! Puedes acceder a todos los canales.",
                        color =DISCORD_COLORS ['success']
                        )
                        await interaction .response .send_message (embed =embed ,ephemeral =True )
                        return 


            await interaction .user .add_roles (verified_role ,reason ="Quick button verification")


            modal =VerificationModal (self .bot ,"",interaction .guild .id )
            await modal .log_verification (interaction .guild .id ,interaction .user .id ,"button")
            await modal .send_verification_log (interaction .guild ,interaction .user ,"BUTTON",True )

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Bienvenido al servidor",
            description =f"¡**{interaction.user.mention}** se ha verificado!\n\n"
            f"¡Bienvenido a {interaction.guild.name}!\n"
            f"Ahora tienes acceso a todos los canales.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verificado a las {current_time.strftime('%I:%M %p IST')}")

            await interaction .response .send_message (embed =embed ,ephemeral =True )

        except discord .Forbidden :
            embed =discord .Embed (
            description ="El bot no tiene permiso para asignar roles. Contacta a un administrador.",
            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )
        except Exception as e :
            logger .error (f"Error in verify button: {e}")
            embed =discord .Embed (


            color =DISCORD_COLORS ['error']
            )
            await interaction .response .send_message (embed =embed ,ephemeral =True )

class Verification (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .bot .loop .create_task (self .create_tables ())

        self .bot .add_view (VerificationView (self .bot ))
        self .bot .add_view (ButtonOnlyVerificationView (self .bot ))
        self .bot .add_view (CaptchaOnlyVerificationView (self .bot ))

    async def create_tables (self ):
        """Create database tables for verification system"""
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS verification_config (
                        guild_id INTEGER PRIMARY KEY,
                        verification_channel_id INTEGER NOT NULL,
                        verified_role_id INTEGER NOT NULL,
                        log_channel_id INTEGER,
                        verification_method TEXT DEFAULT 'both',
                        enabled BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS verification_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        verification_method TEXT NOT NULL,
                        verified_at TEXT NOT NULL,
                        FOREIGN KEY (guild_id) REFERENCES verification_config (guild_id)
                    )
                """)

                await db .commit ()
                pass 
        except Exception as e :
            logger .error (f"Error creating verification tables: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        """Auto-delete messages in verification channel from non-bot users"""
        if message .author .bot :
            return 

        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (message .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if result and result [0 ]==message .channel .id :

                        if not message .author .guild_permissions .manage_messages :
                            try :
                                await message .delete ()

                                embed =discord .Embed (
                                title ="Mensaje eliminado",
                                description ="Este canal es solo para verificación. Usa los botones de arriba para verificarte.",
                                color =DISCORD_COLORS ['warning']
                                )
                                try :
                                    await message .author .send (embed =embed )
                                except discord .Forbidden :
                                    pass 
                            except discord .Forbidden :
                                pass 
        except Exception as e :
            logger .error (f"Error in verification message handler: {e}")

    @commands .hybrid_group (name ="verification",invoke_without_command =True ,description ="Gestión avanzada del sistema de verificación.")
    @commands .has_permissions (administrator =True )
    async def verification (self ,ctx ):
        await ctx .send_help (ctx .command )

    @verification .command (name ="setup",description ="Configura el sistema avanzado de verificación.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_setup (self ,ctx ):
        try :

            missing_perms =await check_bot_permissions (ctx .guild )

            if missing_perms ['guild']:
                embed =discord .Embed (
                title ="Permisos faltantes",
                description =f"Al bot le faltan permisos requeridos en el servidor: {', '.join(missing_perms['guild'])}\n\n"
                "Otorga estos permisos e inténtalo de nuevo.",
                color =DISCORD_COLORS ['error']
                )
                await ctx .send (embed =embed )
                return 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Configuración del sistema avanzado de verificación",
            description ="**¡Bienvenido al sistema de verificación de nueva generación!**\n\n"
            "• **Crea automáticamente el rol verificado** con los permisos adecuados\n"
            "• **CAPTCHA por mensaje directo** para mayor seguridad\n"
            "• **Gestión inteligente de canales** - oculta la verificación tras verificarse\n"
            "• **Corrección automática de permisos** para una configuración sin complicaciones\n"
            "• **Eliminación automática de mensajes** en el canal de verificación\n"
            "• **Registro completo** y estadísticas\n\n"
            "**Configura tu sistema con los menús desplegables de abajo:**",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Asistente de configuración iniciado a las {current_time.strftime('%I:%M %p IST')}")

            view =VerificationSetupView (self .bot ,ctx )
            await ctx .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error in verification setup: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="status",description ="Consulta el estado y las estadísticas del sistema de verificación.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_status (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """SELECT verification_channel_id, verified_role_id, log_channel_id, 
                                  verification_method, enabled FROM verification_config 
                           WHERE guild_id = ?""",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="No configurado",
                        description ="El sistema de verificación no está configurado. Usa `/verificacion configurar` para comenzar.",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 

                    verification_channel =ctx .guild .get_channel (result [0 ])
                    verified_role =ctx .guild .get_role (result [1 ])
                    log_channel =ctx .guild .get_channel (result [2 ])if result [2 ]else None 
                    verification_method =result [3 ]
                    enabled =result [4 ]


                    await cur .execute (
                    "SELECT COUNT(*) FROM verification_logs WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    total_verifications =(await cur .fetchone ())[0 ]

                    await cur .execute (
                    """SELECT verification_method, COUNT(*) FROM verification_logs 
                           WHERE guild_id = ? GROUP BY verification_method""",
                    (ctx .guild .id ,)
                    )
                    method_stats =await cur .fetchall ()


                    yesterday =utc_to_ist (discord .utils .utcnow ())-timedelta (days =1 )
                    await cur .execute (
                    "SELECT COUNT(*) FROM verification_logs WHERE guild_id = ? AND verified_at > ?",
                    (ctx .guild .id ,yesterday .isoformat ())
                    )
                    recent_verifications =(await cur .fetchone ())[0 ]


            issues =[]
            if not verification_channel :
                issues .append ("Canal de verificación no encontrado")
            if not verified_role :
                issues .append ("Rol verificado no encontrado")
            elif not validate_role_hierarchy (ctx .guild ,verified_role ):
                issues .append ("El bot no puede gestionar el rol verificado (jerarquía de roles)")

            missing_perms =await check_bot_permissions (ctx .guild ,verification_channel )
            if missing_perms ['guild']:
                issues .append (f"Permisos del servidor faltantes: {', '.join(missing_perms['guild'])}")
            if missing_perms ['channel']:
                issues .append (f"Permisos del canal faltantes: {', '.join(missing_perms['channel'])}")

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Estado del sistema de verificación",
            color =DISCORD_COLORS ['success']if enabled and not issues else DISCORD_COLORS ['warning']if enabled else DISCORD_COLORS ['error'],
            timestamp =current_time 
            )


            status_text ="Totalmente operativo"if enabled and not issues else "Operativo con problemas"if enabled else "Desactivado"

            embed .add_field (
            name ="Estado del sistema",
            value =f"**Estado:** {status_text}\n"
            f"**Método:** {dict(button='Botón', captcha='CAPTCHA', both='Ambos', manual='Manual').get(verification_method, verification_method)}\n"
            f"**Activado:** {'Sí' if enabled else 'No'}",
            inline =True 
            )

            embed .add_field (
            name ="Configuración",
            value =f"**Canal:** {verification_channel.mention if verification_channel else 'No encontrado'}\n"
            f"**Rol:** {verified_role.mention if verified_role else 'No encontrado'}\n"
            f"**Canal de registros:** {log_channel.mention if log_channel else 'Ninguno'}",
            inline =True 
            )

            embed .add_field (
            name ="Estadísticas",
            value =f"**Verificaciones totales:** {total_verifications}\n"
            f"**Últimas 24 horas:** {recent_verifications}\n"
            f"**Miembros verificados:** {len([m for m in ctx.guild.members if verified_role in m.roles]) if verified_role else 0}",
            inline =True 
            )

            if method_stats :
                stats_text ="\n".join ([f"**{dict(button='Botón', captcha='CAPTCHA', both='Ambos', manual='Manual').get(method, method)}:** {count}"for method ,count in method_stats ])
                embed .add_field (
                name ="Desglose por método",
                value =stats_text ,
                inline =True 
                )

            if issues :
                embed .add_field (
                name ="Problemas detectados",
                value ="\n".join ([f"• {issue}"for issue in issues ]),
                inline =False 
                )

            embed .set_footer (text =f"Estado revisado a las {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error checking verification status: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="fix",description ="Corrige automáticamente los permisos de los canales para el sistema de verificación.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_fix (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id, verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        embed =discord .Embed (
                        title ="No configurado",
                        description ="El sistema de verificación no está configurado o está desactivado.",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 

                    verification_channel =ctx .guild .get_channel (result [0 ])
                    verified_role =ctx .guild .get_role (result [1 ])

                    if not verification_channel or not verified_role :
                        embed =discord .Embed (
                        description ="No se encontró el canal o el rol de verificación.",
                        color =DISCORD_COLORS ['error']
                        )
                        await ctx .send (embed =embed )
                        return 


            failed_count =await auto_fix_permissions (ctx .guild ,verification_channel ,verified_role )

            if failed_count ==-1 :
                embed =discord .Embed (
                color =DISCORD_COLORS ['error']
                )
            elif failed_count >0 :
                embed =discord .Embed (
                title ="Permisos corregidos parcialmente",
                description =f"Se corrigieron automáticamente los permisos de la mayoría de los canales.\n"
                f"No se pudieron corregir {failed_count} canales por restricciones de permisos.",
                color =DISCORD_COLORS ['warning']
                )
            else :
                embed =discord .Embed (
                title ="Permisos corregidos",
                description ="¡Se corrigieron automáticamente todos los permisos de los canales!",
                color =DISCORD_COLORS ['success']
                )

            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error fixing verification permissions: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="disable",description ="Desactiva el sistema de verificación y restablece todos los permisos de los canales.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_disable (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verification_channel_id, verified_role_id FROM verification_config WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("El sistema de verificación no está configurado.")
                        return 


                    await cur .execute (
                    "UPDATE verification_config SET enabled = 0 WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    await db .commit ()


            verification_channel =ctx .guild .get_channel (result [0 ])if result [0 ]else None 
            verified_role =ctx .guild .get_role (result [1 ])if result [1 ]else None 
            everyone_role =ctx .guild .default_role 
            count =0 
            failed_count =0 


            for channel in ctx .guild .channels :
                if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                    try :

                        overwrites =channel .overwrites .copy ()


                        if everyone_role in overwrites :
                            del overwrites [everyone_role ]
                        if verified_role and verified_role in overwrites :
                            del overwrites [verified_role ]


                        await channel .edit (overwrites =overwrites ,reason ="Verification system disabled - restoring public access")
                        count +=1 
                    except discord .Forbidden :
                        failed_count +=1 
                    except Exception as e :
                        logger .error (f"Error resetting permissions for channel {channel.name}: {e}")
                        failed_count +=1 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Sistema de verificación desactivado",
            description =f"El sistema de verificación se desactivó y todos los canales volvieron al acceso público.\n\n"
            f"**Canales restablecidos:** {count}\n"
            f"**No se pudieron restablecer:** {failed_count}"+(f" (por restricciones de permisos)"if failed_count >0 else ""),
            color =DISCORD_COLORS ['success']if failed_count ==0 else DISCORD_COLORS ['warning'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Desactivado y restablecido a las {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error disabling verification: {e}")
            embed =discord .Embed (
            color =DISCORD_COLORS ['error']
            )
            await ctx .send (embed =embed )

    @verification .command (name ="enable",description ="Activa el sistema de verificación.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_enable (self ,ctx ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("El sistema de verificación no está configurado. Usa `/verificacion configurar` primero.")
                        return 


                    verified_role =ctx .guild .get_role (result [0 ])
                    if not verified_role :
                        await ctx .send ("El rol verificado ya no existe. Vuelve a ejecutar la configuración.")
                        return 

                    if not validate_role_hierarchy (ctx .guild ,verified_role ):
                        await ctx .send ("El bot no puede gestionar el rol verificado por la jerarquía de roles. Ajusta las posiciones de los roles.")
                        return 


                    missing_perms =await check_bot_permissions (ctx .guild )
                    if missing_perms ['guild']:
                        await ctx .send (
                        f"Al bot le faltan permisos requeridos: "
                        f"{', '.join(missing_perms['guild'])}. Otorga estos permisos primero."
                        )
                        return 

                    await cur .execute (
                    "UPDATE verification_config SET enabled = 1 WHERE guild_id = ?",
                    (ctx .guild .id ,)
                    )
                    await db .commit ()

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Sistema de verificación activado",
            description ="El sistema de verificación se ha activado.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Activado a las {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error enabling verification: {e}")
            pass 

    @verification .command (name ="logs",description ="Consulta los registros de verificación recientes.")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_logs (self ,ctx ,limit :int =10 ):
        try :
            if limit >50 :
                limit =50 

            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    """SELECT user_id, verification_method, verified_at 
                           FROM verification_logs WHERE guild_id = ? 
                           ORDER BY verified_at DESC LIMIT ?""",
                    (ctx .guild .id ,limit )
                    )
                    logs =await cur .fetchall ()

                    if not logs :
                        await ctx .send ("No se encontraron registros de verificación.")
                        return 

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title =f"Registros de verificación recientes ({len(logs)})",
            color =DISCORD_COLORS ['primary'],
            timestamp =current_time 
            )

            log_text =""
            for user_id ,method ,verified_at in logs :
                user =ctx .guild .get_member (user_id )
                user_name =user .display_name if user else f"Usuario desconocido ({user_id})"
                log_text +=f"**{user_name}** - {method.upper()} - {verified_at}\n"

            embed .description =log_text 
            embed .set_footer (text =f"Registros obtenidos a las {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except Exception as e :
            logger .error (f"Error retrieving verification logs: {e}")
            pass 

    @verification .command (name ="reset",description ="Restablece todos los permisos de los canales (elimina las restricciones de verificación).")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_reset (self ,ctx ):
        try :
            embed =discord .Embed (
            title ="Restablecer permisos de los canales",
            description ="Esto eliminará todas las restricciones de los canales relacionadas con la verificación.\n\n"
            "**Advertencia:** Esta acción no se puede deshacer y puede tardar un poco.\n"
            "Todos los canales volverán a ser visibles para @everyone.",
            color =DISCORD_COLORS ['warning']
            )

            view =discord .ui .View (timeout =60 )

            async def confirm_reset (interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("¡Esta acción no es para ti!",ephemeral =True )
                    return 

                await interaction .response .defer ()


                everyone_role =ctx .guild .default_role 
                count =0 
                failed_count =0 

                for channel in ctx .guild .channels :
                    if isinstance (channel ,(discord .TextChannel ,discord .VoiceChannel ,discord .CategoryChannel )):
                        try :
                            await channel .set_permissions (
                            everyone_role ,
                            overwrite =None ,
                            reason ="Verification system reset"
                            )
                            count +=1 
                        except discord .Forbidden :
                            failed_count +=1 

                current_time =utc_to_ist (discord .utils .utcnow ())
                success_embed =discord .Embed (
                title ="Permisos restablecidos",
                description =f"Se restablecieron correctamente los permisos de {count} canales.\n"
                f"{f'No se pudieron restablecer {failed_count} canales por restricciones de permisos.' if failed_count > 0 else ''}\n\n"
                f"La configuración del sistema de verificación se conservó.\n"
                f"Puedes volver a activar las restricciones con `/verificacion configurar`.",
                color =DISCORD_COLORS ['success'],
                timestamp =current_time 
                )
                success_embed .set_footer (text =f"Restablecimiento completado a las {current_time.strftime('%I:%M %p IST')}")
                await interaction .edit_original_response (embed =success_embed ,view =None )

            async def cancel_reset (interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("¡Esta acción no es para ti!",ephemeral =True )
                    return 
                await interaction .response .edit_message (content ="Restablecimiento cancelado.",embed =None ,view =None )

            confirm_button =discord .ui .Button (label ="Confirmar restablecimiento",style =discord .ButtonStyle .red )
            cancel_button =discord .ui .Button (label ="Cancelar",style =discord .ButtonStyle .grey )

            confirm_button .callback =confirm_reset 
            cancel_button .callback =cancel_reset 

            view .add_item (confirm_button )
            view .add_item (cancel_button )

            await ctx .send (embed =embed ,view =view )

        except Exception as e :
            logger .error (f"Error in verification reset: {e}")
            pass 

    @verification .command (name ="verify",description ="Verifica manualmente a un usuario (solo administradores).")
    @blacklist_check ()
    @ignore_check ()
    @commands .has_permissions (administrator =True )
    async def verification_verify (self ,ctx ,user :discord .Member ):
        try :
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    await cur .execute (
                    "SELECT verified_role_id FROM verification_config WHERE guild_id = ? AND enabled = 1",
                    (ctx .guild .id ,)
                    )
                    result =await cur .fetchone ()

                    if not result :
                        await ctx .send ("El sistema de verificación no está configurado o está desactivado.")
                        return 

                    verified_role =ctx .guild .get_role (result [0 ])
                    if not verified_role :
                        await ctx .send ("No se encontró el rol verificado.")
                        return 

                    if not validate_role_hierarchy (ctx .guild ,verified_role ):
                        await ctx .send ("El bot no puede gestionar el rol verificado por la jerarquía de roles.")
                        return 

                    if verified_role in user .roles :
                        await ctx .send (f"{user.mention} ya está verificado.")
                        return 


            if not ctx .guild .me .guild_permissions .manage_roles :
                await ctx .send ("El bot no tiene el permiso 'Gestionar roles'.")
                return 


            await user .add_roles (verified_role ,reason =f"Manual verification by {ctx.author}")


            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .cursor ()as cur :
                    current_time =utc_to_ist (discord .utils .utcnow ())
                    await cur .execute (
                    "INSERT INTO verification_logs (guild_id, user_id, verification_method, verified_at) VALUES (?, ?, ?, ?)",
                    (ctx .guild .id ,user .id ,"manual",current_time .isoformat ())
                    )
                    await db .commit ()

            current_time =utc_to_ist (discord .utils .utcnow ())
            embed =discord .Embed (
            title ="Usuario verificado manualmente",
            description =f"{ctx.author.mention} verificó manualmente a {user.mention}.",
            color =DISCORD_COLORS ['success'],
            timestamp =current_time 
            )
            embed .set_footer (text =f"Verificado a las {current_time.strftime('%I:%M %p IST')}")
            await ctx .send (embed =embed )

        except discord .Forbidden :
            await ctx .send ("El bot no tiene permiso para asignar roles.")
        except Exception as e :
            logger .error (f"Error manually verifying user: {e}")
            pass 

async def setup (bot):
    await bot.add_cog(Verification (bot))
    logger .info ("Advanced verification cog loaded successfully")
