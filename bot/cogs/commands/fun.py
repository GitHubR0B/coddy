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
from discord.ui import LayoutView, TextDisplay, Separator, MediaGallery
import random
import aiohttp
from discord import app_commands
from utils.Tools import blacklist_check, ignore_check
from utils.cv2 import CV2, build_container

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_api_key = "y3KcqQTdiS0RYcpNJrWn8hFGglKqX4is"

    ACTION_VERBS = {
        "hug": "abraza a",
        "kiss": "besa a",
        "pat": "acaricia a",
        "slap": "abofetea a",
        "tickle": "hace cosquillas a",
    }

    async def fetch_giphy(self, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_api_key}&q={query}&limit=30&rating=pg") as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data['data']:
                    return random.choice(data['data'])['images']['original']['url']
                else:
                    return None

    def random_emoji(self):
        return random.choice(["😂", "🤣", "😆", "😳", "🥴", "🙃", "😜"])

    async def action_command(self, ctx, user: discord.Member, action: str):
        gif_url = await self.fetch_giphy(action)
        if not gif_url:
            await ctx.send(view=CV2("😒 Error", "La API de GIPHY está dormida. ¡Inténtalo más tarde!"))
            return
        view = LayoutView(timeout=None)
        gallery = MediaGallery()
        gallery.add_item(media=gif_url)
        view.add_item(build_container(
            TextDisplay(f"**{ctx.author.mention} {self.ACTION_VERBS.get(action, action)} {user.mention} {self.random_emoji()}**"),
            gallery
        ))
        await ctx.send(view=view)

    async def meter_command(self, ctx, title, user, text):
        await ctx.send(view=CV2(title, text))

    @commands.command(name="shipp")
    @blacklist_check()
    @ignore_check()
    async def shipp(self, ctx, user1: discord.Member, user2: discord.Member):
        percentage = random.randint(0, 100)
        await ctx.send(view=CV2(f"{self.random_emoji()} Resultado del emparejamiento", f"**{user1.mention} x {user2.mention} = {percentage}% de amor**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def hug(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "hug")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def kiss(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "kiss")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def pat(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "pat")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def slap(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "slap")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def tickle(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "tickle")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def coinflip(self, ctx):
        result = random.choice(["Cara", "Cruz"])
        await ctx.send(view=CV2("🪙 Lanzamiento de moneda", f"**Resultado: {result}**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dice(self, ctx):
        result = random.randint(1, 6)
        await ctx.send(view=CV2("🎲 Tirada de dado", f"**¡Sacaste un {result}!**"))

    @commands.command(name="8ball")
    @blacklist_check()
    @ignore_check()
    async def eight_ball(self, ctx, *, question: str):
        responses = ["Es seguro.", "Sin duda alguna.", "Puedes contar con ello.",
                     "Pregunta de nuevo más tarde.", "Mejor no te lo digo ahora.",
                     "No cuentes con ello.", "Mis fuentes dicen que no.", "Muy dudoso."]
        await ctx.send(view=CV2("🎱 Bola 8 Mágica", f"**P:** {question}\n**R:** {random.choice(responses)}"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def roast(self, ctx, user: discord.Member):
        roasts = [
            f"{user.mention} ¡eres la razón por la que el champú trae instrucciones!",
            f"{user.mention} tienes algo en la barbilla... ¡no, en la tercera papada!",
            f"{user.mention} tus secretos están a salvo conmigo. Ni siquiera te escucho cuando me los cuentas."
        ]
        await ctx.send(view=CV2("🔥 Hora de las burlas", random.choice(roasts)))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def iq(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Test de IQ", f"**{user.mention} ¡tiene un IQ de {random.randint(50, 200)}!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dumb(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🤪 Test de estupidez", f"**{user.mention} ¡es {random.randint(0, 100)}% tonto!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def simprate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("😳 Nivel de simp", f"**{user.mention} ¡es {random.randint(0, 100)}% simp!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def toxic(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("☠️ Medidor de toxicidad", f"**{user.mention} ¡es {random.randint(0, 100)}% tóxico!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def intelligence(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Medidor de inteligencia", f"**{user.mention} ¡tiene {random.randint(0, 200)} puntos de IQ!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def genius(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🤓 Nivel de genio", f"**{user.mention} ¡es {random.randint(0, 100)}% genio!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def brainrate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🧠 Poder cerebral", f"**{user.mention} ¡está usando el {random.randint(0, 100)}% de su cerebro!**"))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def howhot(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(view=CV2("🔥 Medidor de atractivo", f"**{user.mention} ¡es {random.randint(0, 100)}% atractivo!**"))

async def setup(bot):
    await bot.add_cog(Fun(bot))