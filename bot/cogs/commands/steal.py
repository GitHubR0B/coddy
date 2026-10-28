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
from discord.ui import View, Button
import requests
from io import BytesIO
import re
from utils.Tools import *

class Steal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.hybrid_command(name="steal", help="Roba un emoji o sticker", usage="steal <emoji>", aliases=["eadd"], with_app_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, emote=None):
        if ctx.message.reference:
            ref_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            attachments = ref_message.attachments
            stickers = ref_message.stickers
            emojis = [emote for emote in ref_message.content.split() if emote.startswith('<:') or emote.startswith('<a:')]

            if attachments or stickers or emojis:
                await self.create_buttons(ctx, attachments, stickers, emojis)
                return

        if emote:
            await self.process_emoji(ctx, emote)
        else:
            await ctx.send(embed=discord.Embed(title="Robar", description="No se encontró ningún emoji ni sticker", color=0xFF0000))

    async def process_emoji(self, ctx, emote):
        try:
            if emote[0] == '<':
                name = emote.split(':')[1]
                emoji_id = emote.split(':')[2][:-1]
                anim = emote.split(':')[0]
                if anim == '<a':
                    url = f'https://cdn.discordapp.com/emojis/{emoji_id}.gif'
                else:
                    url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png'
                await self.add_emoji(ctx, url, name, animated=(anim == '<a'))
            else:
                await ctx.send(embed=discord.Embed(title="Robar", description="Emoji inválido", color=0xFF0000))
        except Exception as e:
            await ctx.send(embed=discord.Embed(title="Robar", description=f"No se pudo añadir el emoji: {str(e)}", color=0xFF0000))

    async def add_emoji(self, ctx, url, name, animated):
        try:
            if not self.has_emoji_slot(ctx.guild, animated):
                await ctx.send(embed=discord.Embed(title="Robar", description="No quedan espacios para emojis", color=0xFF0000))
                return

            sanitized_name = self.sanitize_name(name)
            response = requests.get(url)
            img = response.content
            emote = await ctx.guild.create_custom_emoji(name=sanitized_name, image=img)
            await ctx.send(embed=discord.Embed(title="Robar", description=f"¡Se añadió el emoji \"**{emote}**\"!", color=0xFF0000))
        except Exception as e:
            await ctx.send(embed=discord.Embed(title="Robar", description=f"No se pudo añadir el emoji: {str(e)}", color=0xFF0000))

    async def add_sticker(self, ctx, url, name):
        try:
            if len(ctx.guild.stickers) >= self.get_max_sticker_count(ctx.guild):
                await ctx.send(embed=discord.Embed(title="Robar", description="No quedan espacios para stickers", color=0xFF0000))
                return

            sanitized_name = self.sanitize_name(name)
            response = requests.get(url)
            img = BytesIO(response.content)
            emoji = "⭐"  
            await ctx.guild.create_sticker(name=sanitized_name, description="Añadido por el bot", file=discord.File(img, filename="sticker.png"), emoji=emoji)
            await ctx.send(embed=discord.Embed(title="Robar", description=f"¡Se añadió el sticker \"**{sanitized_name}**\"!", color=0xFF0000))
        except Exception as e:
            await ctx.send(embed=discord.Embed(title="Robar", description=f"No se pudo añadir el sticker: {str(e)}", color=0xFF0000))

    def sanitize_name(self, name):
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        return sanitized[:32]  

    def has_emoji_slot(self, guild, animated):
        normal_emojis = [emoji for emoji in guild.emojis if not emoji.animated]
        animated_emojis = [emoji for emoji in guild.emojis if emoji.animated]
        max_normal, max_animated = self.get_max_emoji_count(guild)

        if animated:
            return len(animated_emojis) < max_animated
        else:
            return len(normal_emojis) < max_normal

    def get_max_emoji_count(self, guild):
        if guild.premium_tier == 3:
            return 250, 250
        elif guild.premium_tier == 2:
            return 150, 150
        elif guild.premium_tier == 1:
            return 100, 100
        else:
            return 50, 50

    def get_max_sticker_count(self, guild):
        if guild.premium_tier == 3:
            return 60
        elif guild.premium_tier == 2:
            return 30
        elif guild.premium_tier == 1:
            return 15
        else:
            return 5

    async def create_buttons(self, ctx, attachments, stickers, emojis):
        class StealView(View):
            def __init__(self, bot, ctx, attachments, stickers, emojis):
                super().__init__()
                self.bot = bot
                self.ctx = ctx
                self.attachments = attachments
                self.stickers = stickers
                self.emojis = emojis

            @discord.ui.button(label="Robar como emoji", style=discord.ButtonStyle.primary)
            async def steal_as_emoji(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                if interaction.user.id != self.ctx.author.id:
                    await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                    return
                await interaction.response.defer()
                for sticker in self.stickers:
                    
                    if sticker.format in [discord.StickerFormatType.png, discord.StickerFormatType.apng, discord.StickerFormatType.lottie]:
                        animated = sticker.format == discord.StickerFormatType.apng
                        await self.bot.cogs['Steal'].add_emoji(self.ctx, sticker.url, sticker.name.replace(' ', '_'), animated=animated)
                    else:
                        await self.ctx.send(embed=discord.Embed(title="Robar", description=f"Formato de sticker no compatible para {sticker.name}", color=0xFF0000))
                for attachment in self.attachments:
                    await self.bot.cogs['Steal'].add_emoji(self.ctx, attachment.url, attachment.filename.split('.')[0].replace(' ', '_'), animated=False)
                for emote in self.emojis:
                    name = emote.split(':')[1]
                    emoji_id = emote.split(':')[2][:-1]
                    anim = emote.split(':')[0]
                    if anim == '<a':
                        url = f'https://cdn.discordapp.com/emojis/{emoji_id}.gif'
                    else:
                        url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png'
                    await self.bot.cogs['Steal'].add_emoji(self.ctx, url, name, animated=(anim == '<a'))

            @discord.ui.button(label="Robar como sticker", style=discord.ButtonStyle.success)
            async def steal_as_sticker(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                if interaction.user.id != self.ctx.author.id:
                    await interaction.response.send_message("Esta interacción no es para ti.", ephemeral=True)
                    return
                await interaction.response.defer()
                for sticker in self.stickers:
                    await self.bot.cogs['Steal'].add_sticker(self.ctx, sticker.url, sticker.name)
                for attachment in self.attachments:
                    await self.bot.cogs['Steal'].add_sticker(self.ctx, attachment.url, attachment.filename.split('.')[0])
                for emote in self.emojis:
                    name = emote.split(':')[1]
                    emoji_id = emote.split(':')[2][:-1]
                    anim = emote.split(':')[0]
                    if anim == '<a':
                        url = f'https://cdn.discordapp.com/emojis/{emoji_id}.gif'
                    else:
                        url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png'
                    await self.bot.cogs['Steal'].add_sticker(self.ctx, url, name)

        embed = discord.Embed(description="Elige qué robar:", color=0xFF0000)
        if attachments:
            embed.set_image(url=attachments[0].url)
        elif stickers:
            embed.set_image(url=stickers[0].url)
        elif emojis:
            for emote in emojis:
                emoji_id = emote.split(':')[2][:-1]
                url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
                embed.set_image(url=url)

        view = StealView(self.bot, ctx, attachments, stickers, emojis)
        await ctx.send(embed=embed, view=view)


