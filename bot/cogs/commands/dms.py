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
from discord.ui import LayoutView, TextDisplay, Separator, Container, Button, ActionRow
from discord.ext import commands
from utils.cv2 import CV2, build_container
from utils.config import STAFF_IDS


class SuccessView(LayoutView):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

        self.add_item(
            build_container(
                TextDisplay("**Mensaje enviado**"),
                Separator(visible=True),
                TextDisplay(
                    f"✅ Tu mensaje se ha enviado correctamente a **{member.name}**"
                ),
            )
        )


class ErrorView(LayoutView):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

        self.add_item(
            build_container(
                TextDisplay("**Error de entrega**"),
                Separator(visible=True),
                TextDisplay(
                    f"❌ No se pudo enviar el mensaje. Es posible que **{member.name}** tenga los mensajes directos desactivados."
                ),
            )
        )


class GenericErrorView(LayoutView):
    def __init__(self, error):
        super().__init__(timeout=None)
        self.error = error

        self.add_item(
            build_container(
                TextDisplay("**Se produjo un error**"),
                Separator(visible=True),
                TextDisplay(f"🤔 Algo salió mal. Error: {error}"),
            )
        )


class PermissionErrorView(LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            build_container(
                TextDisplay("**Permiso denegado**"),
                Separator(visible=True),
                TextDisplay("❌ No tienes permiso para usar este comando."),
            )
        )


class StaffDMCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dmstaff")
    async def dm_staff(self, ctx, member: discord.Member, *, message: str):
        if ctx.author.id not in STAFF_IDS:
            view = PermissionErrorView()
            await ctx.reply(view=view)
            return

        try:
            embed = discord.Embed(
                title="📢 Un mensaje del equipo de staff",
                description=message,
                color=0xFF0000,
            )
            embed.set_footer(text=f"Este mensaje fue enviado por {ctx.author.name}.")

            await member.send(embed=embed)

            view = SuccessView(member)
            await ctx.reply(view=view)

        except discord.Forbidden:
            view = ErrorView(member)
            await ctx.reply(view=view)
        except Exception as e:
            view = GenericErrorView(str(e))
            await ctx.reply(view=view)
            print(f"Error in dmstaff command: {e}")


async def setup(bot):
    await bot.add_cog(StaffDMCog(bot))
