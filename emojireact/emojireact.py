import discord
from discord.ext import commands
from redbot.core import Config
from emoji import UNICODE_EMOJI

class EmojiReactions:
    
    def __init__(self, bot):
        self.bot = bot
        defult_guild = {"unicode": True, "guild":True}
        self.config = Config.get_conf(self, 35677998656)
        self.config.register_guild(**defult_guild)

    @commands.group()
    async def emojireact(self, ctx):
        if ctx.invoked_subcommand is None:
             await ctx.send_help()

    @emojireact.group(name="unicode")
    async def _unicode(self, ctx):
        """Add or remove unicode emoji reactions"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @emojireact.group(name="guild")
    async def _guild(self, ctx):
        """Add or remove guild emoji reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @emojireact.group(name="all")
    async def _all(self, ctx):
        """Add or remove all emoji reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_all.command(name="add", aliases=["on"])        
    async def add_all(self,ctx):
        """Adds all emoji reactions to the guild"""
        await self.config.guild(ctx.guild).unicode.set(True)
        await self.config.guild(ctx.guild).guild.set(True)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing emojis!")

    @_all.command(name="remove", aliases=["off"])        
    async def rem_all(self,ctx):
        """Removes all emoji reactions to the guild"""
        await self.config.guild(ctx.guild).unicode.set(False)
        await self.config.guild(ctx.guild).guild.set(False)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing emojis!")

    @_unicode.command(name="add", aliases=["on"])        
    async def add_unicode(self,ctx):
        """Adds unicode emoji reactions to the guild"""
        await self.config.guild(ctx.guild).unicode.set(True)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing unicode emojis!")

    @_unicode.command(name="remove", aliases=["off"])        
    async def rem_unicode(self,ctx):
        """Removes unicode emoji reactions to the guild"""
        await self.config.guild(ctx.guild).unicode.set(False)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing unicode emojis!")

    @_guild.command(name="add", aliases=["on"])        
    async def add_guild(self,ctx):
        """Adds guild emoji reactions to the guild"""
        await self.config.guild(ctx.guild).guild.set(True)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing guild emojis!")

    @_guild.command(name="remove", aliases=["off"])        
    async def rem_guild(self,ctx):
        """Removes guild emoji reactions to the guild"""
        await self.config.guild(ctx.guild).guild.set(False)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing guild emojis!")

    async def on_message(self, message):
        channel = message.channel
        emoji_list = []
        for word in message.content.split(" "):
            if word.startswith("<:") and word.endswith(">") and await self.config.guild(message.guild).guild():
                emoji_list.append(word.rpartition(">")[0].partition("<")[2])
            if word in UNICODE_EMOJI and await self.config.guild(message.guild).unicode():
                emoji_list.append(word)
        if emoji_list == []:
            return
        for emoji in emoji_list:
            try:
                await self.bot.add_reaction(message, emoji)
            except:
                pass
