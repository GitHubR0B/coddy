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
from discord.ext import commands
from utils.Tools import * # Assuming these decorators exist as provided

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Color is set to Red (255, 0, 0) as requested
        self.color = discord.Color.from_rgb(255, 0, 0)

    @commands.hybrid_command(
        name="kick",
        help="Expulsa a un miembro del servidor.",
        usage="kick <member> [reason]",
        aliases=["kickmember"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick_command(self, ctx, member: discord.Member, *, reason: str = None):
        """Expulsa a un miembro del servidor con una razón opcional."""
        reason = reason or "No se proporcionó una razón"

        # --- Hierarchy and permission checks ---
        if member == ctx.author:
            return await ctx.send("No puedes expulsarte a ti mismo.")

        if member == self.bot.user:
            return await ctx.send("No puedes expulsarme.")

        if ctx.author.top_role <= member.top_role and ctx.guild.owner != ctx.author:
            return await ctx.send("No puedes expulsar a un miembro con un rol igual o superior al tuyo.")

        if ctx.guild.me.top_role <= member.top_role:
            return await ctx.send("Mi rol no es lo suficientemente alto para expulsar a este miembro.")

        # --- Attempt to DM the user ---
        try:
            dm_message = f"Has sido expulsado de **{ctx.guild.name}**. Razón: {reason}"
            await member.send(dm_message)
        except (discord.Forbidden, discord.HTTPException):
            # Fails silently if the user has DMs closed or an error occurs
            pass

        # --- Kick the member ---
        await member.kick(reason=f"Acción de {ctx.author.name} | Razón: {reason}")
        
        # --- Create and send the simplified confirmation embed ---
        member_avatar_url = member.avatar.url if member.avatar else None

        embed = discord.Embed(
            description=(
                f"**{TICK} | {member.mention} fue expulsado correctamente\nRazón: {reason}**"
            ),
            color=self.color # Uses the red color 0xFF0000
        )
        embed.set_author(name=f"Se expulsó correctamente a {member.name}")
        embed.set_footer(text=f"Acción de {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        if member_avatar_url:
            embed.set_thumbnail(url=member_avatar_url)

        await ctx.send(embed=embed)

# Function to add the cog to your bot
async def setup(bot):
    await bot.add_cog(Kick(bot))
