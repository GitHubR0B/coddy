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
from utils.emoji import CROSS, TICK
from discord.ext import commands
from discord.utils import get
import os
from utils.Tools import *
from typing import Optional, Union
from discord.ext.commands import Context
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from utils import *


class Voice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color = 0xFF0000

    @commands.group(name="voice", invoke_without_command=True, aliases=['vc'])
    @blacklist_check()
    @ignore_check()
    async def vc(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @vc.command(name="kick",
                help="Expulsa a un usuario del canal de voz.",
                usage="voice kick <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _kick(self, ctx, *, member: discord.Member):
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        ch = member.voice.channel.mention
        await member.edit(voice_channel=None,
                          reason=f"Disconnected by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{str(member)} ha sido desconectado de {ch}",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="kickall",
                help="Desconecta a todos los miembros del canal de voz.",
                usage="voice kick all")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(move_members=True)
    
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _kickall(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            await member.edit(
                voice_channel=None,
                reason=f"Comando Desconectar Todo ejecutado por: {str(ctx.author)}")
            count += 1
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"Se desconectó a {count} miembros de {ch}",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="mute",
                help="Silencia a un miembro en el canal de voz.",
                usage="voice mute <member>")
    @commands.has_guild_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _mute(self, ctx, *, member: discord.Member = None):
        if member is None:
            embed = discord.Embed(
                title=f"{CROSS} Error",
                description="Debes mencionar a un miembro para silenciarlo.",
                color=self.color
            )
            embed.set_footer(
                text=f"Solicitado por: {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.reply(embed=embed)

        if member.voice is None:
            embed = discord.Embed(
                title=f"{CROSS} Error",
                description=f"{str(member)} no está conectado a ningún canal de voz.",
                color=self.color
            )
            embed.set_footer(
                text=f"Solicitado por: {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.reply(embed=embed)

        if member.voice.mute:
            embed = discord.Embed(
                title=f"{CROSS} Error",
                description=f"{str(member)} ya está silenciado en el canal de voz.",
                color=self.color
            )
            embed.set_footer(
                text=f"Solicitado por: {ctx.author}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.reply(embed=embed)

        await member.edit(mute=True)
        embed = discord.Embed(
            title=f"{TICK}> Éxito",
            description=f"{str(member)} ha sido silenciado en {member.voice.channel.mention}.",
            color=self.color
        )
        embed.set_footer(
            text=f"Solicitado por: {ctx.author}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        )
        return await ctx.reply(embed=embed)

    @vc.command(name="unmute",
                help="Quita el silencio a un miembro en el canal de voz.",
                usage="voice unmute <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(mute_members=True)
    #@commands.bot_has_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def vcunmute(self, ctx, *, member: discord.Member):
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if member.voice.mute == False:
            embed2 = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} ya no está silenciado en el canal de voz.",
                color=self.color)
            embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed2)
        ch = member.voice.channel.mention
        embed3 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"Se quitó el silencio a {str(member)} en {ch}",
            color=self.color)
        embed3.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed3.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        await member.edit(mute=False, reason=f"Unmuted by {str(ctx.author)}")
        return await ctx.reply(embed=embed3)

    @vc.command(name="muteall",
                help="Silencia a todos los miembros de un canal de voz.",
                usage="voice muteall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _muteall(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == False:
                await member.edit(
                    mute=True,
                    reason=
                    f"voice muteall Command Executed by {str(ctx.author)}")
                count += 1
        embed2 = discord.Embed(title=f"{TICK}> Éxito",
                               description=f"Se silenció a {count} miembros en {ch}",
                               color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="unmuteall",
                help="Quita el silencio a todos los miembros de un canal de voz.",
                usage="voice unmuteall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _unmuteall(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == True:
                await member.edit(
                    mute=False,
                    reason=
                    f"Voice unmuteall Command Executed by: {str(ctx.author)}")
                count += 1
        embed2 = discord.Embed(title=f"{TICK}> Éxito",
                               description=f"Se quitó el silencio a {count} miembros en {ch}",
                               color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="deafen",
                help="Ensordece a un usuario en un canal de voz.",
                usage="voice deafen <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(deafen_members=True)
    #@commands.bot_has_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _deafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if member.voice.deaf == True:
            embed2 = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} ya está ensordecido en el canal de voz",
                color=self.color)
            embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed2)
        ch = member.voice.channel.mention
        embed3 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{str(member)} ha sido ensordecido en {ch}",
            color=self.color)
        embed3.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed3.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        await member.edit(deafen=True, reason=f"Deafen by {str(ctx.author)}")
        return await ctx.reply(embed=embed3)

    @vc.command(name="undeafen",
                help="Quita el ensordecimiento a un usuario en un canal de voz.",
                usage="voice undeafen <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(deafen_members=True)
    #@commands.bot_has_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _undeafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if member.voice.deaf == False:
            embed2 = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} ya no está ensordecido en el canal de voz",
                color=self.color)
            embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed2)
        ch = member.voice.channel.mention
        embed3 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"Se quitó el ensordecimiento a {str(member)} en {ch}",
            color=self.color)
        embed3.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed3.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        await member.edit(deafen=False,
                          reason=f"Undeafen by {str(ctx.author)}")
        return await ctx.reply(embed=embed3)

    @vc.command(name="deafenall",
                help="Ensordece a todos los usuarios de un canal de voz.",
                usage="voice deafenall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _deafenall(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == False:
                await member.edit(
                    deafen=True,
                    reason=
                    f"voice deafenall Command Executed by {str(ctx.author)}")
                count += 1
        embed2 = discord.Embed(title=f"{TICK}> Éxito",
                               description=f"Se ensordeció a {count} miembros en {ch}",
                               color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                           icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="undeafenall",
                help="Quita el ensordecimiento a todos los miembros de un canal de voz.",
                usage="voice undeafenall")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _undeafall(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == True:
                await member.edit(
                    deafen=False,
                    reason=
                    f"Voice undeafenall Command Executed by: {str(ctx.author)}")
                count += 1
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"Se quitó el ensordecimiento a {count} miembros en {ch}",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                           icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="moveall",
                help="Mueve a todos los miembros del canal de voz al canal de voz especificado.",
                usage="voice moveall <voice channel>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _moveall(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        try:
            ch = ctx.author.voice.channel.mention
            nch = channel.mention
            count = 0
            for member in ctx.author.voice.channel.members:
                await member.edit(
                    voice_channel=channel,
                    reason=
                    f"voice moveall Command Executed by: {str(ctx.author)}")
                count += 1
            embed2 = discord.Embed(title=f"{TICK}> Éxito",

                description=f"Se movió a {count} miembros de {ch} a {nch}",
                color=self.color)
            embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            await ctx.reply(embed=embed2)
        except:
            embed3 = discord.Embed(title=f"{CROSS} Error",

                description=f"Canal de voz proporcionado no válido",
                color=self.color)
            embed3.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed3.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            await ctx.reply(embed=embed3)

    

    @vc.command(name="pullall",
                help="Mueve a todos los miembros de TODOS los canales de voz a un canal de voz especificado.",
                usage="voice pullall <channel>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _pullall(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        count = 0
        for vc in ctx.guild.voice_channels:
            for member in vc.members:
                if member != ctx.author:
                    try:
                        await member.edit(
                            voice_channel=channel,
                            reason=f"Pullall Command Executed by: {str(ctx.author)}")
                        count += 1
                    except:
                        pass
        embed2 = discord.Embed(title=f"{TICK}> Éxito",
                               description=f"Se movió a {count} miembros a {channel.mention}",
                               color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)


    @vc.command(name="move",
                help="Mueve a un miembro de un canal de voz a otro.",
                usage="voice move <member> <channel>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _move(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if channel == member.voice.channel:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} ya está en {channel.mention}.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        await member.edit(voice_channel=channel,
                          reason=f"Moved by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{str(member)} ha sido movido a {channel.mention}",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)
        

    @vc.command(name="pull",
                help="Trae a un miembro de otro canal de voz al tuyo.",
                usage="voice pull <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    #@commands.bot_has_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _pull(self, ctx, member: discord.Member):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if member.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} no está conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        if member.voice.channel == ctx.author.voice.channel:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                f"{str(member)} ya está en tu canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        await member.edit(voice_channel=ctx.author.voice.channel,
                          reason=f"Pulled by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{str(member)} ha sido traído a tu canal de voz.",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="lock",
                help="Bloquea el canal de voz para que nadie pueda unirse.",
                usage="voice lock")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _lock(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        ch = ctx.author.voice.channel.mention
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role,
                                                       connect=False,
                                                       reason=f"Locked by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{ch} ha sido bloqueado.",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="unlock",
                help="Desbloquea el canal de voz para que cualquiera pueda unirse.",
                usage="voice unlock")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _unlock(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        ch = ctx.author.voice.channel.mention
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role,
                                                       connect=True,
                                                       reason=f"Unlocked by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{ch} ha sido desbloqueado.",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="private",
                help="Hace que el canal de voz sea privado.",
                usage="voice private")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _private(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        ch = ctx.author.voice.channel.mention
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role,
                                                       connect=False,
                                                       view_channel=False,
                                                       reason=f"Made private by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{ch} se ha hecho privado.",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

    @vc.command(name="unprivate",
                help="Hace que el canal de voz sea público.",
                usage="voice unprivate")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _unprivate(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(title=f"{CROSS} Error",

                description=
                "No estás conectado a ningún canal de voz.",
                color=self.color)
            embed.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
            return await ctx.reply(embed=embed)
        ch = ctx.author.voice.channel.mention
        await ctx.author.voice.channel.set_permissions(ctx.guild.default_role,
                                                       connect=True,
                                                       view_channel=True,
                                                       reason=f"Made public by {str(ctx.author)}")
        embed2 = discord.Embed(title=f"{TICK}> Éxito",

            description=f"{ch} se ha hecho público.",
            color=self.color)
        embed2.set_footer(text=f"Solicitado por: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed2.set_thumbnail(url="https://cdn.discordapp.com/emojis/1279464563150032991.png")
        return await ctx.reply(embed=embed2)

 