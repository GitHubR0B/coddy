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
from discord import app_commands
import aiohttp
import asyncio
import random
import time
from utils.ai_utils import poly_image_gen, generate_image_prodia
from prodia.constants import Model
from utils.Tools import *
from utils.cv2 import CV2

blacklisted_words = [
    "naked", "nude", "nudes", "teen", "gay", "lesbian", "porn", "xnxx",
    "bitch", "loli", "hentai", "explicit", "pornography", "adult", "XXX",
    "sex", "erotic", "dick", "vagina", "pussy", "gay", "lick", "creampie", "nsfw",
    "hardcore", "ass", "anal", "anus", "boobs", "tits", "cum", "cunnilingus", "squirt", "penis", "lick", "masturbate", "masturbation ", "orgasm", "orgy", "fap", "fapping", "fuck", "fucking", "handjob", "cowgirl", "doggystyle", "blowjob", "boobjob", "boobies", "horny", "nudity"
]

blocked=["minor", "minors", "kid", "kids", "child", "children", "baby", "babies", "toddler", "childporn", "todd", "underage"]

class CooldownManager:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self.cooldowns = {}

    def check_cooldown(self, user_id: int):
        now = time.time()
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = [now]
            return None

        self.cooldowns[user_id] = [timestamp for timestamp in self.cooldowns[user_id] if now - timestamp < self.per]
        if len(self.cooldowns[user_id]) >= self.rate:
            retry_after = self.per - (now - self.cooldowns[user_id][0])
            return retry_after
        self.cooldowns[user_id].append(now)
        return None

cooldown_manager = CooldownManager(rate=1, per=60.0)

async def cooldown_check(interaction: discord.Interaction):
    retry_after = cooldown_manager.check_cooldown(interaction.user.id)
    if retry_after:
        await interaction.response.send_message(f"Estás en tiempo de espera. Inténtalo de nuevo en {retry_after:.2f} segundos.", ephemeral=True)
        return False
    return True





class AiStuffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @app_commands.command(name="imagine", description="Genera una imagen con IA")
    @discord.app_commands.choices(
        model=[
            discord.app_commands.Choice(name='✨ Elldreth vivid mix (Paisajes, personajes estilizados, nsfw)', value='ELLDRETHVIVIDMIX'),
            discord.app_commands.Choice(name='💪 Deliberate v2 (Lo que quieras, nsfw)', value='DELIBERATE'),
            discord.app_commands.Choice(name='🔮 Dreamshaper (Qué bueno está esto)', value='DREAMSHAPER_6'),
            discord.app_commands.Choice(name='🎼 Lyriel', value='LYRIEL_V16'),
            discord.app_commands.Choice(name='💥 Anything diffusion (Bueno para anime)', value='ANYTHING_V4'),
            discord.app_commands.Choice(name='🌅 Openjourney (Alternativa a Midjourney)', value='OPENJOURNEY'),
            discord.app_commands.Choice(name='🏞️ Realistic (Imágenes realistas)', value='REALISTICVS_V20'),
            discord.app_commands.Choice(name='👨‍🎨 Portrait (Para retratos, supongo)', value='PORTRAIT'),
            discord.app_commands.Choice(name='🌟 Rev animated (Ilustración, Anime)', value='REV_ANIMATED'),
            discord.app_commands.Choice(name='🤖 Analog', value='ANALOG'),
            discord.app_commands.Choice(name='🌌 AbyssOrangeMix', value='ABYSSORANGEMIX'),
            discord.app_commands.Choice(name='🌌 Dreamlike v1', value='DREAMLIKE_V1'),
            discord.app_commands.Choice(name='🌌 Dreamlike v2', value='DREAMLIKE_V2'),
            discord.app_commands.Choice(name='🌌 Dreamshaper 5', value='DREAMSHAPER_5'),
            discord.app_commands.Choice(name='🌌 MechaMix', value='MECHAMIX'),
            discord.app_commands.Choice(name='🌌 MeinaMix', value='MEINAMIX'),
            discord.app_commands.Choice(name='🌌 Stable Diffusion v14', value='SD_V14'),
            discord.app_commands.Choice(name='🌌 Stable Diffusion v15', value='SD_V15'),
            discord.app_commands.Choice(name="🌌 Shonin's Beautiful People", value='SBP'),
            discord.app_commands.Choice(name="🌌 TheAlly's Mix II", value='THEALLYSMIX'),
            discord.app_commands.Choice(name='🌌 Timeless', value='TIMELESS')
        ],
        sampler=[
            discord.app_commands.Choice(name='📏 Euler (Recomendado)', value='Euler'),
            discord.app_commands.Choice(name='📏 Euler a', value='Euler a'),
            discord.app_commands.Choice(name='📐 Heun', value='Heun'),
            discord.app_commands.Choice(name='💥 DPM++ 2M Karras', value='DPM++ 2M Karras'),
            discord.app_commands.Choice(name='💥 DPM++ SDE Karras', value='DPM++ SDE Karras'),
            discord.app_commands.Choice(name='🔍 DDIM', value='DDIM')
        ]
    )
    @discord.app_commands.describe(
        prompt="Escribe un prompt increíble para una imagen",
        model="Modelo para generar la imagen",
        sampler="Sampler para el denoising",
        negative="Prompt que especifica lo que no quieres que genere el modelo",
    )
    async def imagine(self, interaction: discord.Interaction, prompt: str, model: discord.app_commands.Choice[str], sampler: discord.app_commands.Choice[str], negative: str = None, seed: int = None):
        retry_after = cooldown_manager.check_cooldown(interaction.user.id)
        if retry_after:
            await interaction.response.send_message(f"Estás en tiempo de espera. Inténtalo de nuevo en {retry_after:.2f} segundos.", ephemeral=True)
            return

        await interaction.response.defer()

        is_nsfw = any(word in prompt.lower() for word in blacklisted_words)

        is_child = any(word in prompt.lower() for word in blocked)

        if is_child:
            await interaction.followup.send("El contenido de pornografía infantil no está permitido porque viola los ToS de Discord. Inténtalo de nuevo con otro prompt.")
            return

        if is_nsfw and not interaction.channel.nsfw:
            await interaction.followup.send("Solo puedes crear imágenes NSFW en canales NSFW. Prueba en un canal adecuado.", ephemeral=True)
            return

        model_uid = Model[model.value].value[0]

        try:
            imagefileobj = await generate_image_prodia(prompt, model_uid, sampler.value, seed, negative)
        except aiohttp.ClientPayloadError:
            await interaction.followup.send("Ocurrió un error al generar la imagen. Inténtalo de nuevo más tarde.", ephemeral=True)
            return
        except Exception as e:
            await interaction.followup.send(f"Ocurrió un error inesperado: {e}", ephemeral=True)
            return

        if is_nsfw:
            img_file = discord.File(imagefileobj, filename="image.png", spoiler=True, description=prompt)
            prompt = f"||{prompt}||"
        else:
            img_file = discord.File(imagefileobj, filename="image.png", description=prompt)

        desc = (
            f"**Prompt:** {prompt}\n"
            f"**Modelo:** {model.value}\n"
            f"**Sampler:** {sampler.value}\n"
            f"**Semilla:** {seed}"
        )
        if negative:
            desc += f"\n**Prompt negativo:** {negative}"
        if is_nsfw:
            desc += f"\n**NSFW:** {str(is_nsfw)}"

        view = CV2(f"Imagen generada por {interaction.user.display_name}", desc)

        await interaction.followup.send(view=view, file=img_file, ephemeral=True)



async def setup(bot):
    await bot.add_cog(AiStuffCog(bot))
