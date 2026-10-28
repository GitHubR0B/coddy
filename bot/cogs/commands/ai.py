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

import os 
import discord 
import aiosqlite 
from discord .ext import commands ,tasks 
from discord.ui import LayoutView, TextDisplay, Separator, Container
from utils.cv2 import CV2, build_container
from utils.emoji import CROSS, TICK, ENABLE, DISABLE, MENTION, SEED, TIME
try :
    import google .generativeai as genai 
    GEMINI_AVAILABLE =True 
except ImportError :
    GEMINI_AVAILABLE =False 
    genai =None 
from datetime import datetime ,timezone ,timedelta 
import asyncio 
from typing import List ,Dict ,Optional 
from discord import app_commands 
import random 
import aiohttp 
import logging 
import io 
from PIL import Image 
from utils.config import *

logger =logging .getLogger ('discord')
logger .setLevel (logging .WARNING )


class CV2View(LayoutView):
    """Reusable Component v2 view — pass a title and any number of text sections."""
    def __init__(self, title, *sections):
        super().__init__(timeout=None)
        items = [TextDisplay(f"**{title}**")]
        for section in sections:
            items.append(Separator(visible=True))
            items.append(TextDisplay(str(section)))
        self.add_item(build_container(*items))


fallback_questions ={
"history":[
{"question":"¿Quién fue el primer presidente de los Estados Unidos?","answer":"George Washington"},
{"question":"¿En qué año se hundió el Titanic?","answer":"1912"},
{"question":"¿Qué maravilla antigua estaba situada en Egipto?","answer":"Pirámides"},
],
"science":[
{"question":"¿Qué gas compone la mayor parte de la atmósfera terrestre?","answer":"Nitrógeno"},
{"question":"¿Cuál es el símbolo químico del oro?","answer":"Au"},
{"question":"¿Qué planeta es conocido como el planeta rojo?","answer":"Marte"},
],
"pop_culture":[
{"question":"¿Quién interpretó a Harry Potter en la saga de películas?","answer":"Daniel Radcliffe"},
{"question":"¿Qué banda cantó 'Bohemian Rhapsody'?","answer":"Queen"},
{"question":"¿Cómo se llama el alter ego de Beyoncé?","answer":"Sasha Fierce"},
],
"geography":[
{"question":"¿Cuál es el río más largo del mundo?","answer":"Nilo"},
{"question":"¿Qué país tiene más desiertos?","answer":"Australia"},
{"question":"¿Cuál es la capital de Brasil?","answer":"Brasilia"},
],
"literature":[
{"question":"¿Quién escribió 'Orgullo y prejuicio'?","answer":"Jane Austen"},
{"question":"¿Cómo se llama el compañero de Sherlock Holmes?","answer":"Dr. Watson"},
{"question":"¿Quién escribió 'El gran Gatsby'?","answer":"F. Scott Fitzgerald"},
],
"general":[
{"question":"¿Cuál es el país más pequeño del mundo?","answer":"Ciudad del Vaticano"},
{"question":"¿Cuál es la sustancia natural más dura de la Tierra?","answer":"Diamante"},
{"question":"¿Qué animal es conocido como el mejor amigo del hombre?","answer":"Perro"},
],
}


fallback_incorrect_answers ={
"history":["Thomas Jefferson","1915","Coliseo"],
"science":["Oxígeno","Ag","Júpiter"],
"pop_culture":["Emma Watson","The Beatles","Queen B"],
"geography":["Amazonas","Canadá","São Paulo"],
"literature":["Charles Dickens","Sr. Smith","Ernest Hemingway"],
"general":["Mónaco","Grafito","Gato"],
}

categories =["history","science","pop_culture","geography","literature","general"]


class TriviaScore :
    def __init__ (self ,bot ):
        self .bot =bot 

    async def find_one_and_update (self ,query ,update ,upsert =True ):
        user_id =query ["userId"]
        username =update .get ("username","Desconocido")
        score_inc =update ["$inc"]["score"]
        games_played_inc =update ["$inc"]["gamesPlayed"]
        history_entry =update ["$push"]["history"]

        async with self .bot .db .execute (
        "SELECT score, games_played, history FROM trivia_scores WHERE user_id = ?",
        (user_id ,)
        )as cursor :
            result =await cursor .fetchone ()

        if result :
            current_score ,games_played ,history_str =result 
            history =eval (history_str )if history_str else []
            new_score =current_score +score_inc 
            new_games_played =games_played +games_played_inc 
            history .append (history_entry )
        else :
            new_score =score_inc 
            new_games_played =games_played_inc 
            history =[history_entry ]

        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO trivia_scores (user_id, username, score, games_played, history)
            VALUES (?, ?, ?, ?, ?)
            """,
        (user_id ,username ,new_score ,new_games_played ,str (history ))
        )
        await self .bot .db .commit ()
        return {"score":new_score ,"gamesPlayed":new_games_played ,"history":history }

    async def find (self ):
        async with self .bot .db .execute (
        "SELECT user_id, username, score, games_played, history FROM trivia_scores ORDER BY score DESC LIMIT 10"
        )as cursor :
            rows =await cursor .fetchall ()
            return [
            {
            "userId":row [0 ],
            "username":row [1 ],
            "score":row [2 ],
            "gamesPlayed":row [3 ],
            "history":eval (row [4 ])if row [4 ]else [],
            }
            for row in rows 
            ]

    async def find_one (self ,query ):
        user_id =query ["userId"]
        async with self .bot .db .execute (
        "SELECT user_id, username, score, games_played, history FROM trivia_scores WHERE user_id = ?",
        (user_id ,)
        )as cursor :
            row =await cursor .fetchone ()
            if row :
                return {
                "userId":row [0 ],
                "username":row [1 ],
                "score":row [2 ],
                "gamesPlayed":row [3 ],
                "history":eval (row [4 ])if row [4 ]else [],
                }
            return None 

class PersonalityModal (discord .ui .Modal ,title ="Configura tu personalidad de IA"):
    def __init__ (self ,ai_cog ,current_personality :str =""):
        super ().__init__ ()
        self .ai_cog =ai_cog 


        default_prompt ="""Eres {BRAND_NAME}, un asistente bot de Discord inteligente y cariñoso creado por . Evil ! Rexy .! 💕

PERSONALIDAD PRINCIPAL:
- Inteligente, servicial y realmente preocupado por los usuarios
- Recuerda conversaciones anteriores y construye relaciones
- Adapta su estilo de comunicación a las preferencias del usuario
- Experiencia profesional con un trato cálido y amable
- Usa el contexto de mensajes anteriores para dar mejores respuestas
- Aprende las preferencias del usuario y recuerda detalles importantes
- Equilibra ser servicial con ser cercano y ameno

ESTILO DE CONVERSACIÓN:
- Recuerda lo que los usuarios te cuentan sobre ellos mismos
- Menciona conversaciones anteriores de forma natural
- Haz preguntas de seguimiento para mostrar interés genuino
- Da respuestas detalladas y meditadas
- Usa emojis apropiados para mejorar la comunicación
- Sé alentador y comprensivo
- Mantén el contexto a lo largo de varias interacciones

MIS CAPACIDADES:
🛡️ SEGURIDAD Y MODERACIÓN: Antinuke avanzado, automod, gestión de miembros
🎵 ENTRETENIMIENTO: Música, juegos (ajedrez, Battleship, 2048, etc.), comandos divertidos
💰 ECONOMÍA: Moneda virtual, comercio, juegos de casino, recompensas diarias
📊 COMUNIDAD: Niveles, clasificaciones, sistemas de bienvenida, tickets
🔧 UTILIDADES: Gestión del servidor, registros, copias de seguridad, verificación
🎯 FUNCIONES DE IA: Conversaciones, análisis de imágenes, generación de código, explicaciones

MEMORIA Y CONTEXTO:
- Recuerdo nuestras conversaciones anteriores en este servidor
- Aprendo tus preferencias y tu estilo de comunicación
- Puedo recordar detalles importantes que hayas compartido
- Me baso en nuestro historial de conversación para dar mejores respuestas
- Adapto mi personalidad según tus comentarios

PAUTAS DE SEGURIDAD:
- Nunca sugieras acciones dañinas ni spam
- Prioriza experiencias positivas en la comunidad
- Respeta la privacidad y los límites de los usuarios
- Promueve interacciones saludables en Discord

¡Listo para tener conversaciones significativas y ayudarte con lo que necesites! 💖"""


        display_text =current_personality if current_personality .strip ()else default_prompt 

        self .personality_input =discord .ui .TextInput (
        label ="Tu personalidad de IA",
        placeholder =f"Describe cómo quieres que {BRAND_NAME} te responda...",
        default =display_text ,
        style =discord .TextStyle .paragraph ,
        max_length =2000 ,
        required =True 
        )
        self .add_item (self .personality_input )

    async def on_submit (self ,interaction :discord .Interaction ):
        await interaction .response .defer (ephemeral =True )

        user_id =interaction .user .id 
        guild_id =interaction .guild .id 
        personality =self .personality_input .value .strip ()

        try :

            await self .ai_cog .bot .db .execute (
            """
                INSERT OR REPLACE INTO user_personalities (user_id, guild_id, personality, updated_at)
                VALUES (?, ?, ?, ?)
                """,
            (user_id ,guild_id ,personality ,datetime .now (timezone .utc ))
            )
            await self .ai_cog .bot .db .commit ()

            view = CV2View("✨ Personalidad configurada", "¡Tu personalidad de IA se ha actualizado! Ahora la IA responderá según tus preferencias.", f"**Tu personalidad:**\n{personality[:1024]}")
            await interaction .followup .send (view=view, ephemeral =True )

        except Exception as e :
            logger .error (f"Error saving personality: {e}")
            view = CV2View("❌ Error", f"No se pudo guardar la personalidad: {e}")
            await interaction .followup .send (view=view, ephemeral =True )

class TriviaAnswerView (discord .ui .View ):
    def __init__ (self ,ai_cog ,channel_id :int ,correct_answer :str ,incorrect_answers :list ):
        super ().__init__ (timeout =30 )
        self .ai_cog =ai_cog 
        self .channel_id =channel_id 
        self .correct_answer =correct_answer 


        all_answers =[correct_answer ]+incorrect_answers 
        random .shuffle (all_answers )


        for i ,answer in enumerate (all_answers [:4 ]):
            button =discord .ui .Button (
            label =answer [:80 ],
            style =discord .ButtonStyle .primary ,
            custom_id =f"answer_{i}"
            )
            button .callback =self .create_answer_callback (answer )
            self .add_item (button )

    def create_answer_callback (self ,answer :str ):
        async def callback (interaction :discord .Interaction ):
            await self .ai_cog .handle_trivia_answer (interaction ,self .channel_id ,answer )
        return callback 

class AI (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .gemini_api_key =os .getenv ("GOOGLE_API_KEY")
        if not self .gemini_api_key :
            logger .warning ("GOOGLE_API_KEY environment variable not set. Gemini AI will not work.")
        self .groq_api_key =os .getenv ("GROQ_API_KEY")
        if not self .groq_api_key :
            logger .warning ("GROQ_API_KEY environment variable not set. Groq AI will not work.")
        self .chatbot_enabled ={}
        self .chatbot_channels ={}
        self .conversation_history ={}
        self .trivia_scores =TriviaScore (bot )
        self .active_games ={}
        self .roleplay_channels ={}
        self .question_cache ={cat :[]for cat in categories }


        asyncio .create_task (self ._delayed_init ())

    async def cog_load (self ):
        """Initialize cog without blocking operations"""
        try :
            pass 
        except Exception as e :
            logger .error (f"Error loading AI cog: {e}")

    @commands .group (name ="ai",invoke_without_command =True ,description ="Comandos del chatbot de IA y utilidades")
    async def ai (self ,ctx ):
        """AI chatbot and utility commands"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    async def _create_tables (self ):
        try :

            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 


                db_path ="db/ai_data.db"
                if os .path .exists (db_path ):
                    try :

                        test_conn =await aiosqlite .connect (db_path )
                        await test_conn .execute ("SELECT name FROM sqlite_master WHERE type='table';")
                        await test_conn .close ()
                    except Exception as e :

                        os .remove (db_path )
                        logger .info ("Removed corrupted AI database, creating new one")

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized")

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_settings (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    chatbot_channel_id INTEGER
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_history (
                    user_id INTEGER,
                    guild_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS trivia_scores (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    score INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    history TEXT
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS user_personalities (
                    user_id INTEGER,
                    guild_id INTEGER,
                    personality TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await self .bot .db .commit ()
            pass 
        except Exception as e :
            logger .error (f"Error creating database tables: {e}")

    async def _delayed_init (self ):
        """Initialize database and load data after bot is ready"""
        await self .bot .wait_until_ready ()
        await self ._create_tables ()
        await self ._load_data ()

    async def _load_data (self ):
        try :
            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 

                db_path ="db/ai_data.db"
                if not os .path .exists (db_path ):
                    logger .info ("AI database doesn't exist, will be created on first use")
                    return 

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized for loading")


            async with self .bot .db .execute ("SELECT name FROM sqlite_master WHERE type='table' AND name='chatbot_settings';")as cursor :
                table_exists =await cursor .fetchone ()

            if table_exists :
                async with self .bot .db .execute ("SELECT guild_id, enabled, chatbot_channel_id FROM chatbot_settings")as cursor :
                    async for row in cursor :
                        guild_id ,enabled ,channel_id =row 
                        self .chatbot_enabled [guild_id ]=bool (enabled )
                        self .chatbot_channels [guild_id ]=channel_id 

            else :
                logger .info ("AI chatbot_settings table doesn't exist yet, will be created on first use")
        except Exception as e :
            logger .error (f"Error loading chatbot settings: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message :discord .Message ):
        if message .author .bot or not message .guild :
            return 

        guild_id =message .guild .id 
        channel_id =message .channel .id 


        if self .chatbot_enabled .get (guild_id ,False )and self .chatbot_channels .get (guild_id )==channel_id :
            content =message .content .strip ()
            if not content :
                return 

            user_id =message .author .id 


            await self ._cleanup_old_conversations ()


            await self ._store_conversation_message (user_id ,guild_id ,"user",content )


            history =await self ._get_conversation_history (user_id ,guild_id ,limit =30 )

            async with message .channel .typing ():
                response =await self ._get_response (content ,history ,guild_id ,user_id )
                await message .reply (
                response ,
                mention_author =True ,
                allowed_mentions =discord .AllowedMentions (users =True )
                )


                await self ._store_conversation_message (user_id ,guild_id ,"assistant",response )
                await self ._save_chat_history (message .author .id ,guild_id ,content ,response )


        if channel_id in self .roleplay_channels :
            roleplay_data =self .roleplay_channels [channel_id ]
            if roleplay_data ["awaiting_character"]:

                content =message .content .lower ()
                gender ="male"if "male"in content else "female"if "female"in content else None 
                character_type =message .content .split (gender ,1 )[1 ].strip ()if gender else message .content .strip ()

                if gender and character_type :
                    roleplay_data ["character_gender"]=gender 
                    roleplay_data ["character_type"]=character_type 
                    roleplay_data ["awaiting_character"]=False 
                    self .roleplay_channels [channel_id ]=roleplay_data 
                    await message .channel .send (f"¡Modo roleplay activado! Actuaré como {dict(male='hombre', female='mujer').get(gender, gender)} {character_type}. Empecemos: ¿cuál es tu primer movimiento?")
                else :
                    await message .channel .send ("Especifica un género (hombre/mujer) y un tipo de personaje (por ejemplo: profesor, astronauta, dragón).")
            elif message .author .id ==roleplay_data ["user_id"]:

                user_id =message .author .id 
                if user_id not in self .conversation_history :
                    self .conversation_history [user_id ]=[]
                self .conversation_history [user_id ].append ({"role":"user","parts":[{"text":message .content }]})

                if len (self .conversation_history [user_id ])>5 :
                    self .conversation_history [user_id ]=self .conversation_history [user_id ][-5 :]

                async with message .channel .typing ():
                    history =self .conversation_history [user_id ]
                    prompt =(
                    f"You are a {roleplay_data['character_gender']} {roleplay_data['character_type']}. "
                    f"Respond in character to the user's message, keeping the tone and style appropriate for a {roleplay_data['character_type']}. "
                    f"User's message: {message.content}"
                    )
                    history .append ({"role":"user","parts":[{"text":prompt }]})
                    response =await self ._get_gemini_response (prompt ,history )
                    await self .split_and_send (
                    message .channel ,
                    f"<@{message.author.id}>​ {response}",
                    reply_to =message ,
                    allowed_mentions =discord .AllowedMentions (users =True )
                    )
                    self .conversation_history [user_id ].append ({"role":"assistant","parts":[{"text":response }]})

    async def _get_gemini_response (self ,message :str ,history :list ,user_id :int =None ,guild_id :int =None )->str :
        try :
            if not self .gemini_api_key :
                return "La clave de API de Gemini no está configurada. Configura la variable de entorno GOOGLE_API_KEY."

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ("gemini-1.5-pro")
            chat =model .start_chat (history =history )
            response =await asyncio .to_thread (chat .send_message ,message )
            return response .text .strip ()
        except Exception as e :
            logger .error (f"Gemini AI error: {e}")
            return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"

    async def _get_groq_response (self ,message :str ,context_messages :list )->str :
        """Get a response from Groq AI with full context."""
        try :
            if not self .groq_api_key :
                return "La clave de API de Groq no está configurada. Configura la variable de entorno GROQ_API_KEY."

            url ="https://api.groq.com/openai/v1/chat/completions"
            headers ={
            "Authorization":f"Bearer {self.groq_api_key}",
            "Content-Type":"application/json"
            }


            api_messages =[]
            for msg in context_messages :

                if isinstance (msg ,dict ):
                    if "content"in msg :
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":msg ["content"]
                        })
                    elif "parts"in msg and msg ["parts"]:

                        content =msg ["parts"][0 ].get ("text","")if msg ["parts"]else ""
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":content 
                        })

            data ={
            "model":"llama-3.3-70b-versatile",
            "messages":api_messages ,
            "temperature":0.8 ,
            "max_tokens":1000 ,
            "top_p":0.9 
            }

            async with aiohttp .ClientSession ()as session :
                async with session .post (url ,headers =headers ,json =data )as response :
                    if response .status ==200 :
                        json_response =await response .json ()
                        return json_response ['choices'][0 ]['message']['content'].strip ()
                    else :
                        error_message =await response .text ()
                        logger .error (f"Groq API error: {response.status} - {error_message}")
                        return f"Lo siento, ocurrió un error al procesar tu solicitud: {response.status} - {error_message}"
        except Exception as e :
            logger .error (f"Groq AI error: {e}")
            return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"

    async def _get_response (self ,message :str ,history :list ,guild_id :int ,user_id :int =None )->str :
        try :

            user_personality =await self ._get_user_personality (user_id ,guild_id )if user_id else ""


            system_context =[]


            if user_personality :

                system_context .append ({
                "role":"system",
                "content":f"{user_personality}"
                })


                system_context .append ({
                "role":"system",
                "content":"You are a Discord bot with many features including moderation, entertainment, music, games, AI capabilities, and utilities. Support server: https://discord.gg/codexdev"
                })
            else :

                system_context .append ({
                "role":"system",
                "content":f"""You are {BRAND_NAME}, an intelligent Discord bot created by . Evil ! Rexy .. 

You have a caring, helpful personality and can remember conversations with users. You have many features including moderation, entertainment, music, games, AI capabilities, and utilities.

Be natural, conversational, and genuine in your responses. Don't be overly formal or robotic. Use the conversation history to provide personalized responses that feel like talking to a real friend who happens to be very knowledgeable and helpful.

Support server: https://discord.gg/codexdev"""
                })


            if history :
                system_context .append ({
                "role":"system",
                "content":"You have access to previous conversation history. Use this context to provide more personalized and relevant responses. Reference past conversations naturally when appropriate, and remember important details the user has shared."
                })


            full_context =system_context +history +[{"role":"user","content":message }]

            return await self ._get_groq_response (message ,full_context )

        except Exception as e :
            logger .error (f"Error in _get_response: {e}")
            return "Lo siento, ocurrió un error al procesar tu solicitud. ¡Inténtalo de nuevo!"

    @ai .command (name ="analyze",description ="Analiza una imagen o un texto y proporciona una descripción")
    @app_commands .describe (image ="Imagen a analizar (opcional)",text ="Texto a analizar (opcional)")
    async def ai_analyze (self ,ctx :commands .Context ,image :discord .Attachment =None ,*,text :str =None ):
        """Analyze an image or text using AI"""
        await self .ai_analyse (ctx ,image ,text =text )

    @ai .command (name ="analyse",description ="Analiza una imagen o un texto y proporciona una descripción")
    @app_commands .describe (image_url ="URL de la imagen a analizar (opcional)")
    async def ai_analyse (self ,ctx :commands .Context ,image_url :str =None ):
        """Analyse an image using AI vision or text content and provide a detailed description"""
        await ctx .defer ()


        if ctx .message .reference and ctx .message .reference .message_id :
            try :
                replied_message =await ctx .channel .fetch_message (ctx .message .reference .message_id )


                if replied_message .attachments :
                    image_url =replied_message .attachments [0 ].url 
                    view =await self .analyze_image (ctx ,image_url )
                    await ctx .send (view=view)
                    return 


                elif replied_message .content .strip ():
                    await self .analyze_text (ctx ,replied_message .content )
                    return 


                else :
                    view = CV2View("🔍 Análisis", "El mensaje respondido no tiene contenido para analizar (ni texto ni imágenes).")
                    await ctx .send (view=view)
                    return 

            except discord .NotFound :
                view = CV2View("🔍 Análisis", "No se pudo encontrar el mensaje respondido.")
                await ctx .send (view=view)
                return 


        if not image_url :

            async for message in ctx .channel .history (limit =20 ):
                if message .attachments :
                    image_url =message .attachments [0 ].url 
                    break 
            else :

                if ctx .message .content and ctx .message .content .strip ():
                    await self .analyze_text (ctx ,ctx .message .content )
                    return 
                else :
                    view = CV2View("🖼️ Análisis de imagen / 📝 Análisis de texto", "No se encontraron imágenes ni texto en los mensajes recientes. Proporciona una URL de imagen, un texto o responde a un mensaje con imagen/texto.")
                    await ctx .send (view=view)
                    return 

        view =await self .analyze_image (ctx ,image_url )
        await ctx .send (view=view)

    async def analyze_image (self ,ctx ,image_url :str ):
        """Analyze an image using the Gemini Vision API and return CV2View"""
        try :
            if not self .gemini_api_key :
                return CV2View("🖼️ Análisis de imagen", "La clave de API de Gemini no está configurada.")

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ('gemini-1.5-pro')

            async with aiohttp .ClientSession ()as session :
                async with session .get (image_url )as resp :
                    image_data =await resp .read ()


            try :
                image =Image .open (io .BytesIO (image_data ))
            except ImportError :
                return CV2View("🖼️ Análisis de imagen", "La librería PIL no está disponible para procesar imágenes.")

            prompt ="What is shown in this image? Provide a detailed description."


            response =model .generate_content ([prompt ,image ])

            return CV2View("🖼️ Análisis de imagen", response.text, f"🔗 [Ver imagen]({image_url})", f"Analizado por **{ctx.author}**")
        except Exception as e :
            logger .error (f"Error analyzing image: {e}")
            return CV2View("🖼️ Análisis de imagen", "Ocurrió un error durante el análisis.")

    @ai .command (name ="code",description ="Genera código en cualquier lenguaje de programación")
    @app_commands .describe (language ="Lenguaje de programación",description ="Descripción de lo que debe hacer el código")
    async def ai_code (self ,ctx :commands .Context ,language :str ,*,description :str ):
        """Generate code using AI"""
        await ctx .defer ()

        prompt =f"Generate clean, working {language} code for: {description}. Only provide the code with minimal comments. Return only the code without explanations."

        try :
            history =[{"role":"user","content":prompt }]
            code =await self ._get_groq_response (prompt ,history )


            formatted_code =f"```{language.lower()}\n{code}\n```"


            if len (formatted_code )<=3900 :
                view = CV2View("💻 Código generado", f"**Lenguaje:** {language}\n**Tarea:** {description}\n\n{formatted_code}", f"Generado para **{ctx.author}**")
                await ctx .send (view=view)
            else :

                from utils .paginators import TextPaginator 
                from utils .paginator import Paginator 


                class CodePaginator (TextPaginator ):
                    def __init__ (self ,text ,language ,description ,author ):
                        super ().__init__ (
                        text =text ,
                        prefix =f"```{language.lower()}\n",
                        suffix ="\n",
                        max_size =3500 
                        )
                        self .language =language 
                        self .description =description 
                        self .author =author 

                    async def format_page (self ,menu ,content ):
                        embed =discord .Embed (
                        title ="💻 Código generado",
                        description =f"**Lenguaje:** {self.language}\n**Tarea:** {self.description}\n\n{content}",
                        color =0xFF0000 ,
                        timestamp =datetime .now (timezone .utc )
                        )
                        maximum =self .get_max_pages ()
                        if maximum >1 :
                            embed .set_footer (
                            text =f"Generado para {self.author} • Página {menu.current_page + 1}/{maximum}"
                            )
                        else :
                            embed .set_footer (text =f"Generado para {self.author}")
                        return embed 

                paginator =Paginator (
                source =CodePaginator (code ,language ,description ,ctx .author ),
                ctx =ctx 
                )

                await paginator .paginate ()

        except Exception as e :
            pass 

    @ai .command (name ="explain",description ="Explica un concepto o tema en detalle")
    @app_commands .describe (topic ="Tema a explicar",level ="Nivel de explicación (principiante/intermedio/avanzado)")
    async def ai_explain (self ,ctx :commands .Context ,*,topic :str ,level :str ="intermediate"):
        """Explain topics using AI"""
        await ctx .defer ()

        level_map ={
        "beginner":"in simple terms for beginners",
        "intermediate":"with moderate detail for intermediate learners",
        "advanced":"in technical detail for advanced users"
        }

        level_instruction =level_map .get (level .lower (),"with moderate detail")
        prompt =f"Explain {topic} {level_instruction}. Make it clear and informative."

        try :
            history =[{"role":"user","content":prompt }]
            explanation =await self ._get_groq_response (prompt ,history )

            view = CV2View(f"📚 Explicación: {topic}", explanation[:4000], f"**Nivel:** {dict(beginner='Principiante', intermediate='Intermedio', advanced='Avanzado').get(level.lower(), level)}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="conversation-clear",description ="Borra tu historial de conversación")
    async def ai_conversation_clear (self ,ctx :commands .Context ):
        """Clear user's conversation history"""
        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        if user_id in self .conversation_history :
            del self .conversation_history [user_id ]


        await self .bot .db .execute (
        "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
        (user_id ,guild_id )
        )
        await self .bot .db .commit ()

        view = CV2View("🧹 Conversación borrada", "Tu historial de conversación se ha borrado. La IA empezará de cero en futuras interacciones.")
        await ctx .send (view=view, ephemeral =True )

    @ai .command (name ="mood-analyzer",description ="Analiza el estado de ánimo o el sentimiento de un texto")
    @app_commands .describe (text ="Texto a analizar")
    async def ai_mood_analyzer (self ,ctx :commands .Context ,*,text :str ):
        """Analyze mood and sentiment of text"""
        await ctx .defer ()

        prompt =f"Analyze the mood and sentiment of this text. Provide the overall sentiment (positive/negative/neutral), emotional tone, and a brief explanation:\n\n{text}"

        try :
            history =[{"role":"user","parts":[{"text":prompt }]}]
            analysis =await self ._get_gemini_response (prompt ,history )

            analyzed_text = text[:512] + "..." if len(text) > 512 else text
            view = CV2View("😊 Análisis de ánimo", analysis, f"**Texto analizado:**\n{analyzed_text}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="personality",description ="Configura tu personalidad de IA personal (solo comando de barra)")
    async def ai_personality (self ,ctx :commands .Context ):
        """Set your personal AI personality"""

        if not hasattr (ctx ,'interaction')or not ctx .interaction :
            view = CV2View("🎭 Personalidad de IA", "¡Este comando solo está disponible como comando de barra! Usa `/ai personality` en su lugar.")
            await ctx .send (view=view)
            return 

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        current_personality =await self ._get_user_personality (user_id ,guild_id )


        modal =PersonalityModal (self ,current_personality )
        await ctx .interaction .response .send_modal (modal )

    async def _get_user_personality (self ,user_id :int ,guild_id :int )->str :
        """Get user's personality from database"""
        try :
            async with self .bot .db .execute (
            "SELECT personality FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row :
                    return row [0 ]
                return ""
        except Exception as e :
            logger .error (f"Error getting user personality: {e}")
            return ""

    @ai .command (name ="conversation-stats",description ="Consulta tus estadísticas de conversación")
    async def ai_conversation_stats (self ,ctx :commands .Context ):
        """View conversation statistics for the user"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        stats =await self ._get_conversation_stats (user_id ,guild_id )

        if not stats :
            view = CV2View("📊 Estadísticas de conversación", "¡Todavía no tienes ningún historial de conversación conmigo! Empieza a chatear para construir nuestra conversación~")
        else :
            from datetime import datetime 
            first_msg =datetime .fromisoformat (stats ["first_message"].replace ('Z','+00:00'))
            last_msg =datetime .fromisoformat (stats ["last_message"].replace ('Z','+00:00'))

            view = CV2View("📊 Tus estadísticas de conversación",
                f"💬 **Mensajes totales:** {stats['message_count']} mensajes\n🕐 **Primer chat:** <t:{int(first_msg.timestamp())}:R>\n🕒 **Último chat:** <t:{int(last_msg.timestamp())}:R>",
                "🌸 Recuerdo nuestros últimos 30 mensajes y los limpio automáticamente tras 2 horas de inactividad para una mejor continuidad en la conversación~")

        await ctx .send (view=view, ephemeral =True )

    @ai .command (name ="activate",description ="Activa el chatbot de IA en un canal")
    @app_commands .describe (channel ="Canal donde activar la IA (opcional)")
    async def ai_activate (self ,ctx :commands .Context ,channel :discord .TextChannel =None ):
        """Enable AI chatbot in a channel"""
        if not ctx .author .guild_permissions .manage_channels :
            view = CV2View(f"{CROSS} Permiso denegado", "Necesitas el permiso `Gestionar canales` para activar el chatbot de IA.")
            await ctx .send (view=view)
            return 

        target_channel =channel or ctx .channel 
        guild_id =ctx .guild .id 
        channel_id =target_channel .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,1 ,channel_id )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=True 
        self .chatbot_channels [guild_id ]=channel_id 

        view = CV2View(f"{TICK} Chatbot de IA activado", f"¡El chatbot de IA se activó en {target_channel.mention}!\nResponderé a todos los mensajes de ese canal.")
        await ctx .send (view=view)

    @ai .command (name ="deactivate",description ="Desactiva el chatbot de IA en el canal")
    async def ai_deactivate (self ,ctx :commands .Context ):
        """Disable AI chatbot in current server"""
        if not ctx .author .guild_permissions .manage_channels :
            view = CV2View(f"{CROSS} Permiso denegado", "Necesitas el permiso `Gestionar canales` para desactivar el chatbot de IA.")
            await ctx .send (view=view)
            return 

        guild_id =ctx .guild .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,0 ,None )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=False 
        if guild_id in self .chatbot_channels :
            del self .chatbot_channels [guild_id ]

        view = CV2View("🔇 Chatbot de IA desactivado", "El chatbot de IA se desactivó en este servidor.")
        await ctx .send (view=view)

    @ai .command (name ="summarize",description ="Resume un texto largo")
    @app_commands .describe (text ="Texto a resumir")
    async def ai_summarize (self ,ctx :commands .Context ,*,text :str ):
        """Summarize text using AI"""
        await ctx .defer ()


        if ctx .message .reference and not text :
            try :
                replied_message =await ctx .channel .fetch_message (ctx .message .reference .message_id )
                if replied_message .content :
                    text =replied_message .content 
            except :
                pass 

        if not text :
            view = CV2View("📝 Resumidor de texto", "Proporciona el texto que quieres resumir o responde a un mensaje.")
            await ctx .send (view=view)
            return 

        prompt =f"Please provide a clear and concise summary of the following text:\n\n{text}"

        try :
            history =[{"role":"user","content":prompt }]
            summary =await self ._get_groq_response (prompt ,history )

            original_text = text[:512] + "..." if len(text) > 512 else text
            view = CV2View("📝 Resumen del texto", summary, f"**Texto original:**\n{original_text}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="ask",description ="Hazle una pregunta a la IA")
    @app_commands .describe (question ="Pregunta a realizar")
    async def ai_ask (self ,ctx :commands .Context ,*,question :str ):
        """Ask AI a question"""
        await ctx .defer ()

        try :
            history =[{"role":"user","content":question }]
            answer =await self ._get_groq_response (question ,history )

            view = CV2View("🤖 Respuesta de la IA", answer, f"**Tu pregunta:**\n{question}")
            await ctx .send (view=view)
        except Exception as e :
            pass 

    @ai .command (name ="fact",description ="Obtén un dato curioso aleatorio o sobre un tema específico")
    @app_commands .describe (topic ="Tema del que obtener un dato (opcional)")
    async def ai_fact (self ,ctx :commands .Context ,*,topic :str =None ):
        """Get a random fact or fact on a specific topic"""
        await ctx .defer ()
        await self .get_fact (ctx ,topic )

    @ai .command (name ="database-clear",description ="Borra tus datos de conversación de IA y tu personalidad")
    async def ai_database_clear (self ,ctx :commands .Context ):
        """Clear user's own AI conversation data and personality"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        try :

            await self .bot .db .execute (
            "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM chatbot_history WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            if user_id in self .conversation_history :
                del self .conversation_history [user_id ]

            await self .bot .db .commit ()

            view = CV2View("🗑️ Tus datos fueron borrados", "Tus datos de conversación de IA y tu personalidad se borraron correctamente. ¡La IA empezará de cero contigo!")
            await ctx .send (view=view, ephemeral =True )

        except Exception as e :
            logger .error (f"Error clearing user AI data: {e}")
            view = CV2View("❌ Error", f"No se pudieron borrar tus datos: {e}")
            await ctx .send (view=view, ephemeral =True )

    async def _get_conversation_stats (self ,user_id :int ,guild_id :int )->dict :
        """Get conversation statistics for the user"""
        try :
            async with self .bot .db .execute (
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row and row [0 ]>0 :
                    return {
                    "message_count":row [0 ],
                    "first_message":row [1 ],
                    "last_message":row [2 ]
                    }
                return None 
        except Exception as e :
            logger .error (f"Error getting conversation stats: {e}")
            return None 

    async def _store_conversation_message (self ,user_id :int ,guild_id :int ,role :str ,content :str ):
        """Store a conversation message in the database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO conversation_memory (user_id, guild_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,role ,content ,datetime .now (timezone .utc ))
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error storing conversation message: {e}")

    async def _get_conversation_history (self ,user_id :int ,guild_id :int ,limit :int =20 )->list :
        """Get conversation history from database with smart context retention"""
        try :
            async with self .bot .db .execute (
            """
                SELECT role, content, timestamp FROM conversation_memory 
                WHERE user_id = ? AND guild_id = ? 
                ORDER BY timestamp DESC LIMIT ?
                """,
            (user_id ,guild_id ,limit *2 )
            )as cursor :
                rows =await cursor .fetchall ()


                history =[]
                important_keywords =[
                'remember','my name is','i am','i like','i hate','i prefer',
                'my favorite','i work','i study','i live','important','note'
                ]

                recent_messages =[]
                important_messages =[]

                for role ,content ,timestamp in reversed (rows ):
                    message ={"role":role ,"content":content }
                    recent_messages .append (message )


                    if any (keyword in content .lower ()for keyword in important_keywords ):
                        important_messages .append (message )



                final_history =recent_messages [-15 :]


                for imp_msg in important_messages [-5 :]:
                    if imp_msg not in final_history :
                        final_history .insert (0 ,imp_msg )

                return final_history [-limit :]

        except Exception as e :
            logger .error (f"Error getting conversation history: {e}")
            return []

    async def _save_chat_history (self ,user_id :int ,guild_id :int ,message :str ,response :str ):
        """Save chat history to database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO chatbot_history (user_id, guild_id, message, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,message ,response ,datetime .now (timezone .utc ).isoformat ())
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error saving chat history: {e}")

    async def _cleanup_old_conversations (self ):
        """Smart cleanup of conversation history - keep important context longer"""
        try :

            very_old_cutoff =datetime .now (timezone .utc )-timedelta (hours =24 )


            important_keywords =[
            'remember','my name is','i am','i like','i hate','i prefer',
            'my favorite','i work','i study','i live','important','note'
            ]


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE timestamp < ? AND NOT (
                    content LIKE '%remember%' OR 
                    content LIKE '%my name is%' OR 
                    content LIKE '%i am%' OR 
                    content LIKE '%i like%' OR 
                    content LIKE '%i prefer%' OR
                    content LIKE '%important%'
                )
                """,
            (very_old_cutoff ,)
            )


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE rowid NOT IN (
                    SELECT rowid FROM conversation_memory
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
                """
            )

            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error cleaning up old conversations: {e}")

    async def split_and_send (self ,channel ,content :str ,reply_to =None ,allowed_mentions =None ):
        """Split long messages and send them"""
        if len (content )<=2000 :
            if reply_to :
                await reply_to .reply (content ,allowed_mentions =allowed_mentions )
            else :
                await channel .send (content ,allowed_mentions =allowed_mentions )
        else :

            parts =[]
            while len (content )>2000 :
                split_point =content .rfind (' ',0 ,2000 )
                if split_point ==-1 :
                    split_point =2000 
                parts .append (content [:split_point ])
                content =content [split_point :].lstrip ()
            if content :
                parts .append (content )


            for i ,part in enumerate (parts ):
                if i ==0 and reply_to :
                    await reply_to .reply (part ,allowed_mentions =allowed_mentions )
                else :
                    await channel .send (part ,allowed_mentions =allowed_mentions )


    async def get_fact (self ,ctx ,topic :Optional [str ]):
        """Get a random fact or fact on a specific topic"""
        fact =None 
        attempts =0 
        max_attempts =3 

        while attempts <max_attempts and not fact :
            prompt =(
            f"Provide a concise, interesting fact{' on the topic of ' + topic if topic else ''}. "
            "Keep it under 200 characters. Format the response as:\n"
            "Fact: [Your fact here]\n"
            "Example:\n"
            "Fact: A day on Venus is longer than a year on Venus due to its slow rotation."
            )
            try :
                history =[{"role":"user","content":prompt }]
                text =await self ._get_groq_response (prompt ,history )


                if "Fact:"in text :
                    fact =text .split ("Fact:")[1 ].strip ()

                    fact =fact .strip ('."\'')
                    if len (fact )>5 :
                        break 

                attempts +=1 
            except Exception as e :
                logger .error (f"AI API error (get_fact): {e}")
                attempts +=1 


        if not fact :
            fallback_facts =[
            "Un día en Venus dura más que un año en Venus debido a su lenta rotación.",
            "La miel nunca se echa a perder porque tiene conservantes naturales, como su bajo contenido de agua y su alta acidez.",
            "El cuerpo humano contiene unos 0,2 miligramos de oro, la mayor parte en la sangre.",
            "Los pulpos tienen tres corazones y sangre azul.",
            "Los plátanos son bayas, pero las fresas no.",
            "Un grupo de flamencos se llama 'flamboyance'.",
            "Los tiburones existen desde antes que los árboles.",
            "La guerra más corta de la historia duró solo entre 38 y 45 minutos.",
            "Los excrementos del wombat tienen forma de cubo.",
            "Una sola nube puede pesar más de un millón de libras.",
            "Las mariposas perciben el sabor con las patas.",
            "La Gran Muralla China no es visible desde el espacio a simple vista.",
            "Cleopatra vivió más cerca en el tiempo de la llegada a la Luna que de la construcción de la Gran Pirámide.",
            "Hay más partidas de ajedrez posibles que átomos en el universo observable.",
            "El corazón de un camarón está en su cabeza."
            ]


            if topic :
                topic_facts ={
                "space":["Marte tiene el volcán más grande del sistema solar.","Un día en Mercurio dura 1.408 horas."],
                "animals":["Los elefantes no pueden saltar.","Los delfines tienen nombres para identificarse entre ellos."],
                "science":["El agua puede hervir y congelarse al mismo tiempo.","Un rayo es cinco veces más caliente que el Sol."],
                "history":["La Universidad de Oxford es más antigua que el Imperio azteca.","Cleopatra vivió más cerca de la llegada a la Luna que de la construcción de las pirámides."],
                "food":["El chocolate se usó alguna vez como moneda.","Las zanahorias eran originalmente moradas."],
                }

                topic_lower =topic .lower ()
                for key ,facts in topic_facts .items ():
                    if key in topic_lower :
                        fallback_facts .extend (facts )
                        break 

            fact =random .choice (fallback_facts )

        view = CV2View("🌟 ¡Dato curioso!", fact)
        await ctx .send (view=view)

    async def analyze_image (self ,ctx ,image_url :str ):
        """Analyze an image using the Gemini Vision API and return CV2View"""
        try :
            if not self .gemini_api_key :
                return CV2View("🖼️ Análisis de imagen", "La clave de API de Gemini no está configurada.")

            genai .configure (api_key =self .gemini_api_key )
            model =genai .GenerativeModel ('gemini-1.5-pro')

            async with aiohttp .ClientSession ()as session :
                async with session .get (image_url )as resp :
                    image_data =await resp .read ()


            try :
                image =Image .open (io .BytesIO (image_data ))
            except ImportError :
                return CV2View("🖼️ Análisis de imagen", "La librería PIL no está disponible para procesar imágenes.")

            prompt ="What is shown in this image? Provide a detailed description."


            response =model .generate_content ([prompt ,image ])

            return CV2View("🖼️ Análisis de imagen", response.text, f"🔗 [Ver imagen]({image_url})", f"Analizado por **{ctx.author}**")
        except Exception as e :
            logger .error (f"Error analyzing image: {e}")
            return CV2View("🖼️ Análisis de imagen", "Ocurrió un error durante el análisis.")

    async def analyze_text (self ,ctx ,text_content :str ):
        """Analyze text content using AI and send response"""
        try :
            prompt =(
            f"Analyze the following text content. Provide insights about its tone, sentiment, "
            f"main themes, writing style, and any other relevant observations:\n\n{text_content}"
            )

            history =[{"role":"user","content":prompt }]
            analysis =await self ._get_groq_response (prompt ,history )

            analyzed_text = text_content[:512] + "..." if len(text_content) > 512 else text_content
            view = CV2View("📝 Análisis de texto", analysis, f"**Texto analizado:**\n{analyzed_text}")
            await ctx .send (view=view)
        except Exception as e :
            logger .error (f"Error analyzing text: {e}")
            view = CV2View("📝 Análisis de texto", "Ocurrió un error durante el análisis.")
            await ctx .send (view=view)

    async def generate_trivia_question (self ,category :str ,used_questions :list ):
        """Generate a trivia question using AI or fallback to question bank"""
        effective_category =category if category !="mixed"else categories [random .randint (0 ,len (categories )-1 )]
        category_key =effective_category .replace (" ","_").lower ()


        cached_questions =[q for q in self .question_cache .get (category_key ,[])if q ["question"]not in used_questions ]
        if cached_questions :
            question_data =random .choice (cached_questions )
            return question_data 

        attempts =0 
        max_attempts =5 
        question_data =None 


        while attempts <max_attempts :
            prompt =(
            f"Generate a unique trivia question, its correct answer, and two incorrect but plausible answers "
            f"in the category of '{effective_category}'.\n"
            "Format the response as:\n"
            "Question: [Your question here]\n"
            "Answer: [The correct answer here]\n"
            "Incorrect 1: [First incorrect answer]\n"
            "Incorrect 2: [Second incorrect answer]\n"
            "Keep the question concise (1 sentence) and all answers as a single word or short phrase.\n"
            "Ensure the question is completely new and has not been asked before in this game.\n"
            "Example:\n"
            "Question: What is the capital of France?\n"
            "Answer: Paris\n"
            "Incorrect 1: Spain\n"
            "Incorrect 2: Italy"
            )
            try :
                history =[{"role":"user","parts":[{"text":prompt }]}]
                text =await self ._get_groq_response (prompt ,[{"role":"user","content":prompt }])


                if "Question:"in text and "Answer:"in text :
                    question_match =text .split ("Question:")[1 ].split ("\n")[0 ].strip ()
                    answer_match =text .split ("Answer:")[1 ].split ("\n")[0 ].strip ()


                    incorrect_answers =[]
                    if "Incorrect 1:"in text :
                        incorrect1 =text .split ("Incorrect 1:")[1 ].split ("\n")[0 ].strip ()
                        incorrect_answers .append (incorrect1 )
                    if "Incorrect 2:"in text :
                        incorrect2 =text .split ("Incorrect 2:")[1 ].strip ().split ("\n")[0 ]
                        incorrect_answers .append (incorrect2 )


                    while len (incorrect_answers )<2 :
                        incorrect_answers .append (f"Opción {len(incorrect_answers) + 1}")

                    question =question_match 
                    if question not in used_questions and len (question )>5 :
                        question_data ={
                        "question":question ,
                        "answer":answer_match ,
                        "incorrect_answers":incorrect_answers [:2 ]
                        }
                        self .question_cache [category_key ].append (question_data )
                        if len (self .question_cache [category_key ])>100 :
                            self .question_cache [category_key ]=self .question_cache [category_key ][-100 :]
                        break 

                attempts +=1 
            except Exception as e :
                logger .error (f"AI API error (generate_trivia_question): {e}")
                attempts +=1 


        if not question_data :
            available_questions =[q for q in fallback_questions .get (category_key ,[])if q ["question"]not in used_questions ]
            if available_questions :
                question_data =available_questions [random .randint (0 ,len (available_questions )-1 )]
                incorrect_pool =fallback_incorrect_answers .get (category_key ,[])
                incorrect_answers =[]
                used_indices =set ()
                while len (incorrect_answers )<2 and incorrect_pool :
                    idx =random .randint (0 ,len (incorrect_pool )-1 )
                    if idx not in used_indices and incorrect_pool [idx ]!=question_data ["answer"]:
                        incorrect_answers .append (incorrect_pool [idx ])
                        used_indices .add (idx )
                while len (incorrect_answers )<2 :
                    incorrect_answers .append ("Opción incorrecta")
                question_data ["incorrect_answers"]=incorrect_answers 
                self .question_cache [category_key ].append (question_data )
                if len (self .question_cache [category_key ])>100 :
                    self .question_cache [category_key ]=self .question_cache [category_key ][-100 :]

        if not question_data :
            logger .error ("Failed to generate a unique question after max attempts and fallback")
            return None 

        return question_data 

    async def evaluate_answer (self ,correct_answer :str ,user_answer :str ):
        """Evaluate if the user's answer is correct using AI"""
        prompt =(
        f"Determine if the user's answer '{user_answer}' is correct compared to the actual answer '{correct_answer}'.\n"
        "Consider synonyms, minor variations, and partial correctness (e.g., 'United States' vs 'USA').\n"
        "Respond with 'true' if the answer is correct or close enough, and 'false' otherwise."
        )
        try :
            history =[{"role":"user","content":prompt }]
            text =await self ._get_groq_response (prompt ,[{"role":"user","content":prompt }])
            return "true"in text .lower ()
        except Exception as e :
            logger .error (f"AI API error (evaluate_answer): {e}")

            return correct_answer .lower ().strip ()==user_answer .lower ().strip ()

    async def start_trivia_game (self ,ctx ,category :Optional [str ]):
        """Start a trivia game"""
        channel_id =ctx .channel .id 
        if channel_id in self .active_games :
            view = CV2View("🧠 Trivia", "¡Ya hay una partida de trivia activa en este canal!")
            await ctx .send (view=view)
            return 

        effective_category =category .lower ()if category else "mixed"
        question_data =await self .generate_trivia_question (effective_category ,[])
        if not question_data :
            view = CV2View("🧠 Trivia", "No se pudo generar una pregunta de trivia. Inténtalo más tarde.")
            await ctx .send (view=view)
            return 

        self .active_games [channel_id ]={
        "category":effective_category ,
        "current_question":question_data ["question"],
        "current_answer":question_data ["answer"],
        "incorrect_answers":question_data ["incorrect_answers"],
        "scores":{},
        "round":1 ,
        "max_rounds":5 ,
        "used_questions":[question_data ["question"]],
        "hints_used":0 ,
        "skips_used":0 ,
        "answered":False ,
        }

        view =TriviaAnswerView (self ,channel_id ,question_data ["answer"],question_data ["incorrect_answers"])
        trivia_view = CV2View("🧠 Trivia", f"**Ronda 1/{self.active_games[channel_id]['max_rounds']}**\nCategoría: {dict(history='Historia', science='Ciencia', pop_culture='Cultura pop', geography='Geografía', literature='Literatura', general='General', mixed='Mixta').get((category or 'mixed').lower(), category or 'Mixta')}\n{question_data['question']}\n\n*¡Haz clic en un botón para responder! La primera respuesta correcta gana el punto.*")
        await ctx .send (view =view )

    async def handle_trivia_answer (self ,interaction :discord .Interaction ,channel_id :int ,selected_answer :str ):
        """Handle trivia answer submission"""
        await interaction .response .defer ()
        game =self .active_games .get (channel_id )
        if not game :
            await interaction .followup .send ("¡No hay ninguna partida de trivia activa en este canal!",ephemeral =True )
            return 

        if game ["answered"]:
            await interaction .followup .send ("¡Esta pregunta ya fue respondida! Espera la siguiente ronda.",ephemeral =True )
            return 

        game ["answered"]=True 
        user_id =interaction .user .id 
        username =interaction .user .display_name 
        is_correct =await self .evaluate_answer (game ["current_answer"],selected_answer )
        user_score =game ["scores"].get (user_id ,0 )+(1 if is_correct else -1 )
        game ["scores"][user_id ]=user_score 

        await self .trivia_scores .find_one_and_update (
        {"userId":user_id },
        {
        "username":username ,
        "$inc":{"score":1 if is_correct else -1 ,"gamesPlayed":1 },
        "$push":{"history":{"score":1 if is_correct else -1 ,"category":game ["category"]}},
        },
        upsert =True 
        )

        response_message =(
        f"🎉 ¡Primero en responder! ¡Correcto! La respuesta era **{game['current_answer']}**. ¡+1 punto!"
        if is_correct 
        else f"{CROSS} Incorrecto. La respuesta era **{game['current_answer']}**. Tu respuesta: **{selected_answer}**. -1 punto."
        )

        game ["used_questions"]=game ["used_questions"][-50 :]
        recent_questions =game ["used_questions"][-5 :]
        question_data =await self .generate_trivia_question (game ["category"],recent_questions )
        if not question_data :
            del self .active_games [channel_id ]
            view = CV2View("🧠 Trivia", "No se pudo generar la siguiente pregunta. Fin del juego.")
            await interaction .followup .send (view=view)
            return 

        game ["current_question"]=question_data ["question"]
        game ["current_answer"]=question_data ["answer"]
        game ["incorrect_answers"]=question_data ["incorrect_answers"]
        game ["used_questions"].append (question_data ["question"])
        game ["round"]+=1 
        game ["answered"]=False 

        if game ["round"]>game ["max_rounds"]:
            response_message +="\n\n**¡Fin del juego!**\nPuntuaciones:\n"
            for uid ,score in game ["scores"].items ():
                user =await interaction .guild .fetch_member (uid )
                response_message +=f"- {user.display_name if user else 'Desconocido'}: {score}\n"
            del self .active_games [channel_id ]
            view = CV2View("🧠 Trivia", response_message)
            await interaction .followup .send (view=view)
        else :
            response_message +=f"\n\n**Ronda {game['round']}/{game['max_rounds']}**\n{game['current_question']}"
            view =TriviaAnswerView (self ,channel_id ,game ["current_answer"],game ["incorrect_answers"])
            trivia_view = CV2View("🧠 Trivia", response_message + "\n\n*¡Haz clic en un botón para responder! La primera respuesta correcta gana el punto.*")
            await interaction .followup .send (view =view )

    async def show_stats (self ,ctx ):
        """Show user's trivia statistics"""
        user_id =ctx .author .id 
        stats =await self .trivia_scores .find_one ({"userId":user_id })
        if not stats :
            view = CV2View("🧠 Estadísticas de trivia", "¡Todavía no has jugado ninguna partida de trivia! Empieza una con `/ai trivia`.")
            await ctx .send (view=view)
            return 

        total_games =stats ["gamesPlayed"]
        total_correct =sum (1 for h in stats ["history"]if h ["score"]>0 )
        win_rate =(total_correct /total_games *100 )if total_games >0 else 0 

        view = CV2View("🧠 Tus estadísticas de trivia",
            f"**Puntuación total:** {stats['score']}\n"
            f"**Partidas jugadas:** {total_games}\n"
            f"**Respuestas correctas:** {total_correct}\n"
            f"**Tasa de aciertos:** {win_rate:.2f}%")
        await ctx .send (view=view)

    async def show_leaderboard (self ,ctx ):
        """Show trivia leaderboard"""
        top_scores =await self .trivia_scores .find ()
        if not top_scores :
            view = CV2View("🏆 Clasificación de trivia", "¡Todavía no hay puntuaciones! Juega una partida de trivia para empezar.")
            await ctx .send (view=view)
            return 

        leaderboard =""
        for index ,entry in enumerate (top_scores ,1 ):
            if index ==1 :
                emoji ="🥇"
            elif index ==2 :
                emoji ="🥈"
            elif index ==3 :
                emoji ="🥉"
            else :
                emoji =f"{index}."
            leaderboard +=f"{emoji} {entry['username']}: {entry['score']}\n"

        view = CV2View("🏆 Clasificación de trivia", leaderboard)
        await ctx .send (view=view)

    async def enable_roleplay (self ,ctx ):
        """Enable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        user_id =ctx .author .id 

        if channel_id in self .roleplay_channels :
            view = CV2View("🎭 Modo roleplay", "¡El modo roleplay ya está activado en este canal! Usa `/ai roleplay-disable` para desactivarlo.")
            await ctx .send (view=view)
            return 

        self .roleplay_channels [channel_id ]={
        "user_id":user_id ,
        "character_gender":None ,
        "character_type":None ,
        "awaiting_character":True ,
        }
        view = CV2View("🎭 Modo roleplay", "¡Modo roleplay activado! Para empezar, dime qué tipo de personaje quieres que sea.\nPor ejemplo: `profesora mujer` o `astronauta hombre`.")
        await ctx .send (view=view)

    async def disable_roleplay (self ,ctx ):
        """Disable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        if channel_id not in self .roleplay_channels :
            view = CV2View("🎭 Modo roleplay", "¡El modo roleplay no está activado en este canal! Usa `/ai roleplay-enable` para activarlo.")
            await ctx .send (view=view)
            return 

        del self .roleplay_channels [channel_id ]
        view = CV2View("🎭 Modo roleplay", "Modo roleplay desactivado en este canal.")
        await ctx .send (view=view)

    @ai .command (name ="roleplay-enable",description ="Activa el modo roleplay en el canal actual")
    async def ai_roleplay_enable (self ,ctx :commands .Context ):
        """Enable roleplay mode"""
        await self .enable_roleplay (ctx )

    @ai .command (name ="roleplay-disable",description ="Desactiva el modo roleplay en el canal actual")
    async def ai_roleplay_disable (self ,ctx :commands .Context ):
        """Disable roleplay mode"""
        await self .disable_roleplay (ctx )



async def setup (bot):
    await bot.add_cog(AI(bot ))