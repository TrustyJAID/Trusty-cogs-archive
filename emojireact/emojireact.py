import discord
from discord.ext import commands
from .utils.dataIO import dataIO
import os
try:
    from emoji import UNICODE_EMOJI
except:
    raise RuntimeError("Can't load emoji. Do 'pip3 install emoji'.")

class ServerEmojiReact():
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/emojireact/settings.json"
        self.settings = dataIO.load_json(self.settings_file)

    @commands.group(pass_context=True)
    async def emojireact(self, ctx):
        if ctx.invoked_subcommand is None:
             await self.bot.send_cmd_help(ctx)

    @emojireact.group(pass_context=True, name="unicode")
    async def _unicode(self, ctx):
        """Add or remove unicode emoji reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @emojireact.group(pass_context=True, name="server")
    async def _server(self, ctx):
        """Add or remove server emoji reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @emojireact.group(pass_context=True, name="all")
    async def _all(self, ctx):
        """Add or remove all emoji reactions"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_all.command(pass_context=True, name="add", aliases=["on"])        
    async def add_all(self,ctx):
        """Adds all emoji reactions to the server"""
        self.settings[ctx.message.server.id] = {"unicode":True, "server": True}
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing emojis!")

    @_all.command(pass_context=True, name="remove", aliases=["off"])        
    async def rem_all(self,ctx):
        """Removes all emoji reactions to the server"""
        self.settings[ctx.message.server.id] = {"unicode":False, "server": False}
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing emojis!")

    @_unicode.command(pass_context=True, name="add", aliases=["on"])        
    async def add_unicode(self,ctx):
        """Adds unicode emoji reactions to the server"""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {"unicode":True, "server": False}
        else:
            self.settings[ctx.message.server.id]["unicode"] = True
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing unicode emojis!")

    @_unicode.command(pass_context=True, name="remove", aliases=["off"])        
    async def rem_unicode(self,ctx):
        """Removes unicode emoji reactions to the server"""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {"unicode":False, "server": False}
        else:
            self.settings[ctx.message.server.id]["unicode"] = False
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing unicode emojis!")

    @_server.command(pass_context=True, name="add", aliases=["on"])        
    async def add_server(self,ctx):
        """Adds server emoji reactions to the server"""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {"unicode":True, "server": True}
        else:
            self.settings[ctx.message.server.id]["server"] = True
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing server emojis!")

    @_server.command(pass_context=True, name="remove", aliases=["off"])        
    async def rem_server(self,ctx):
        """Removes server emoji reactions to the server"""
        if ctx.message.server.id not in self.settings:
            self.settings[ctx.message.server.id] = {"unicode":False, "server": False}
        else:
            self.settings[ctx.message.server.id]["server"] = False
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing server emojis!")

    async def on_message(self, message):
        channel = message.channel
        if message.server.id not in self.settings:
            return
        if not self.settings[message.server.id]:
            return
        emoji_list = []
        for word in message.content.split(" "):
            if word.startswith("<:") and word.endswith(">"):
                emoji_list.append(word.rpartition(">")[0].partition("<")[2])
            if word in UNICODE_EMOJI:
                emoji_list.append(word)
        if emoji_list == []:
            return
        for emoji in emoji_list:
            try:
                await self.bot.add_reaction(message, emoji)
            except:
                pass

def check_folders():
    if not os.path.exists("data/emojireact"):
        print("Creating data/emojireact folder...")
        os.makedirs("data/emojireact")

def check_files():
    f = "data/emojireact/settings.json"
    data = {}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(ServerEmojiReact(bot))
