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
from utils.cv2 import CV2

class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="qr",
        aliases=["qrcode"],
        help="Envía una imagen de código QR.",
        with_app_command=True
    )
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def qr(self, ctx):
        view = CV2("Plataforma de pago", "Aquí puedes pagar con UPI mediante el QR de abajo")
        from discord.ui import MediaGallery
        gallery = MediaGallery()
        gallery.add_item(media="https://media.discordapp.net/attachments/1334099972739829843/1377897856286851152/share_image4613677226378289500.png?ex=69f6ec61&is=69f59ae1&hm=50c40fe1e341074865e4b29b1321ab19af3649889c276f3fa4407468dbd75f4a&=&format=webp&quality=lossless&width=441&height=892")
        view.children[0].add_item(gallery)
        await ctx.reply(view=view)

    @qr.error
    async def qr_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ Debes ser **administrador** para usar este comando.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"⏳ Estás en tiempo de espera. Inténtalo de nuevo en `{round(error.retry_after, 1)}s`.")
        else:
            await ctx.reply(f"⚠️ Ocurrió un error: `{str(error)}`")

# Required for bot.load_extension()
async def setup(bot):
    await bot.add_cog(QR(bot))
