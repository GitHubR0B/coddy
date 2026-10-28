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
from utils.emoji import LOCK
from discord.ext import commands


class _encrypt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def help_custom(self):
        emoji = LOCK
        label = "Comandos de cifrado"
        description = "Codifica y decodifica texto en varios formatos"
        return emoji, label, description

    @commands.group(name="encryption", aliases=["encrypt"], invoke_without_command=True)
    async def _Encryption(self, ctx: commands.Context):
        """Show all available encryption commands"""
        embed = discord.Embed(
            title="Comandos de cifrado",
            description=f"Usa `{ctx.prefix}encode <type>` para codificar texto y `{ctx.prefix}decode <type>` para decodificarlo.",
            color=0x000000,
        )

        embed.add_field(
            name="📝 Comandos de codificación",
            value=f"""
`{ctx.prefix}encode base32` / `{ctx.prefix}encode b32` - Codifica en base32
`{ctx.prefix}encode base64` / `{ctx.prefix}encode b64` - Codifica en base64
`{ctx.prefix}encode rot13` / `{ctx.prefix}encode r13` - Codifica en rot13
`{ctx.prefix}encode hex` - Codifica en hex
`{ctx.prefix}encode base85` / `{ctx.prefix}encode b85` - Codifica en base85
`{ctx.prefix}encode ascii85` / `{ctx.prefix}encode a85` - Codifica en ASCII85
""",
            inline=False,
        )

        embed.add_field(
            name="📄 Comandos de decodificación",
            value=f"""
`{ctx.prefix}decode base32` / `{ctx.prefix}decode b32` - Decodifica desde base32
`{ctx.prefix}decode base64` / `{ctx.prefix}decode b64` - Decodifica desde base64
`{ctx.prefix}decode rot13` / `{ctx.prefix}decode r13` - Decodifica desde rot13
`{ctx.prefix}decode hex` - Decodifica desde hex
`{ctx.prefix}decode base85` / `{ctx.prefix}decode b85` - Decodifica desde base85
`{ctx.prefix}decode ascii85` / `{ctx.prefix}decode a85` - Decodifica desde ASCII85
""",
            inline=False,
        )

        embed.add_field(
            name="🔐 Utilidad",
            value=f"`{ctx.prefix}password` - Genera una contraseña segura aleatoria (enviada por MD)",
            inline=False,
        )

        embed.set_footer(
            text="Usa los comandos encode/decode para cifrar o descifrar tu texto"
        )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(_encrypt(bot))
