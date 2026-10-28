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
from utils.emoji import CHANNEL, TICK
from discord.ext import commands

class Unhide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255,0, 0) # Green color for success

    @commands.hybrid_command(
        name="unhide",
        help="Muestra un canal al rol predeterminado (@everyone).",
        usage="unhide [channel]",
        aliases=["unhidechannel"])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unhide_command(self, ctx, channel: discord.TextChannel = None):
        """Hace que un canal vuelva a ser visible para @everyone."""
        # If no channel is mentioned, use the current channel
        channel = channel or ctx.channel

        # Get the author's avatar URL
        author_avatar_url = ctx.author.avatar.url if ctx.author.avatar else None

        # Check if the channel is already visible
        if channel.permissions_for(ctx.guild.default_role).read_messages:
            embed = discord.Embed(
                description=f"**{CHANNEL} Canal**: {channel.mention}\n{TICK} **Estado**: Ya visible",
                color=self.color
            )
            embed.set_author(name=f"{channel.name} ya es visible")
            if author_avatar_url:
                embed.set_thumbnail(url=author_avatar_url)
            await ctx.send(embed=embed)
            return

        # Unhide the channel by updating permissions
        await channel.set_permissions(ctx.guild.default_role, read_messages=True)

        # Create the success embed
        embed = discord.Embed(
            description=f"**{TICK} | {channel.mention} se mostró correctamente.**",
            color=self.color
        )
        embed.set_author(name="Canal visible")
        embed.set_footer(text=f"Acción de {ctx.author.name}", icon_url=author_avatar_url)
        if author_avatar_url:
            embed.set_thumbnail(url=author_avatar_url)
            
        await ctx.send(embed=embed)

# Function to add the cog to your bot
async def setup(bot):
    await bot.add_cog(Unhide(bot))
