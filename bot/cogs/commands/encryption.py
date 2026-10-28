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

import base64
import binascii
import codecs
import secrets

import discord
from discord.ui import LayoutView, TextDisplay, Separator, Container
from discord.ext import commands
from utils.cv2 import CV2, build_container


class EncryptResultView(LayoutView):
    def __init__(self, convert, txtinput):
        super().__init__(timeout=None)

        try:
            display_text = txtinput.decode("UTF-8")
        except AttributeError:
            display_text = str(txtinput)

        if len(display_text) > 500:
            display_text = display_text[:500] + "..."

        self.add_item(
            build_container(
                TextDisplay(f"📑 **{convert}**"),
                Separator(visible=True),
                TextDisplay(display_text),
            )
        )


class DecodeErrorView(LayoutView):
    def __init__(self, codec_name):
        super().__init__(timeout=None)

        self.add_item(
            build_container(
                TextDisplay(f"❌ **{codec_name} no válido**"),
                Separator(visible=True),
                TextDisplay(f"La cadena proporcionada no es una codificación {codec_name} válida."),
            )
        )


class PasswordSentView(LayoutView):
    def __init__(self, author_name):
        super().__init__(timeout=None)

        self.add_item(
            build_container(
                TextDisplay("🔐 **Contraseña generada**"),
                Separator(visible=True),
                TextDisplay(
                    f"Te enviamos un DM con tu contraseña aleatoria generada **{author_name}**"
                ),
            )
        )


class PasswordDMView(LayoutView):
    def __init__(self, password):
        super().__init__(timeout=None)

        self.add_item(
            build_container(
                TextDisplay("🎁 **Aquí está tu contraseña:**"),
                Separator(visible=True),
                TextDisplay(password),
            )
        )


class encryption(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def encode(self, ctx):
        """Todos los métodos de codificación"""
        await ctx.send_help(ctx.command)

    @commands.group(invoke_without_command=True)
    async def decode(self, ctx):
        """Todos los métodos de decodificación"""
        await ctx.send_help(ctx.command)

    async def encryptout(self, ctx, convert, txtinput):
        view = EncryptResultView(convert, txtinput)
        await ctx.send(view=view)

    @encode.command(name="base32", aliases=["b32"])
    async def encode_base32(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en base32"""
        await self.encryptout(
            ctx, "Texto -> base32", base64.b32encode(txtinput.encode("UTF-8"))
        )

    @decode.command(name="base32", aliases=["b32"])
    async def decode_base32(self, ctx, *, txtinput: str):
        """Decodifica base32"""
        try:
            await self.encryptout(
                ctx, "base32 -> Texto", base64.b32decode(txtinput.encode("UTF-8"))
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("base32"))

    @encode.command(name="base64", aliases=["b64"])
    async def encode_base64(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en base64"""
        await self.encryptout(
            ctx, "Texto -> base64", base64.urlsafe_b64encode(txtinput.encode("UTF-8"))
        )

    @decode.command(name="base64", aliases=["b64"])
    async def decode_base64(self, ctx, *, txtinput: str):
        """Decodifica base64"""
        try:
            await self.encryptout(
                ctx,
                "base64 -> Texto",
                base64.urlsafe_b64decode(txtinput.encode("UTF-8")),
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("base64"))

    @encode.command(name="rot13", aliases=["r13"])
    async def encode_rot13(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en rot13"""
        await self.encryptout(ctx, "Texto -> rot13", codecs.decode(txtinput, "rot_13"))

    @decode.command(name="rot13", aliases=["r13"])
    async def decode_rot13(self, ctx, *, txtinput: str):
        """Decodifica rot13"""
        try:
            await self.encryptout(
                ctx, "rot13 -> Texto", codecs.decode(txtinput, "rot_13")
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("rot13"))

    @encode.command(name="hex")
    async def encode_hex(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en hex"""
        await self.encryptout(
            ctx, "Texto -> hex", binascii.hexlify(txtinput.encode("UTF-8"))
        )

    @decode.command(name="hex")
    async def decode_hex(self, ctx, *, txtinput: str):
        """Decodifica hex"""
        try:
            await self.encryptout(
                ctx, "hex -> Texto", binascii.unhexlify(txtinput.encode("UTF-8"))
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("hex"))

    @encode.command(name="base85", aliases=["b85"])
    async def encode_base85(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en base85"""
        await self.encryptout(
            ctx, "Texto -> base85", base64.b85encode(txtinput.encode("UTF-8"))
        )

    @decode.command(name="base85", aliases=["b85"])
    async def decode_base85(self, ctx, *, txtinput: str):
        """Decodifica base85"""
        try:
            await self.encryptout(
                ctx, "base85 -> Texto", base64.b85decode(txtinput.encode("UTF-8"))
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("base85"))

    @encode.command(name="ascii85", aliases=["a85"])
    async def encode_ascii85(self, ctx, *, txtinput: commands.clean_content):
        """Codifica en ASCII85"""
        await self.encryptout(
            ctx, "Texto -> ASCII85", base64.a85encode(txtinput.encode("UTF-8"))
        )

    @decode.command(name="ascii85", aliases=["a85"])
    async def decode_ascii85(self, ctx, *, txtinput: str):
        """Decodifica ASCII85"""
        try:
            await self.encryptout(
                ctx, "ASCII85 -> Texto", base64.a85decode(txtinput.encode("UTF-8"))
            )
        except Exception:
            await ctx.send(view=DecodeErrorView("ASCII85"))

    @commands.command(name="password")
    async def password(self, ctx):
        """Genera una contraseña segura aleatoria para ti"""
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.send(view=PasswordSentView(ctx.author.name))

        password = secrets.token_urlsafe(18)
        try:
            await ctx.author.send(view=PasswordDMView(password))
        except discord.Forbidden:
            await ctx.send(
                f"❌ No se pudo enviar el DM. Aquí está tu contraseña: **{password}**"
            )


async def setup(bot):
    await bot.add_cog(encryption(bot))
