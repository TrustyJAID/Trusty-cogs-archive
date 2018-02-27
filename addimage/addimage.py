from random import choice, randint
import random
import aiohttp
import discord
import asyncio
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
import os
import string

class AddImage:
    def __init__(self, bot):
        self.bot = bot
        self.images = dataIO.load_json("data/addimage/settings.json")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    async def first_word(self, msg):
        return msg.split(" ")[0].lower()

    async def get_prefix(self, server, msg):
        prefixes = self.bot.settings.get_prefixes(server)
        for p in prefixes:
            if msg.startswith(p):
                return p
        return None       

    async def part_of_existing_command(self, alias, server):
        '''Command or alias'''
        for command in self.bot.commands:
            if alias.lower() == command.lower():
                return True
        return False

    async def make_server_folder(self, server):
        if not os.path.exists("data/addimage/{}".format(server.id)):
            print("Creating server folder")
            os.makedirs("data/addimage/{}".format(server.id))

    async def on_message(self, message):
        if len(message.content) < 2 or message.channel.is_private:
            return

        msg = message.content
        server = message.server
        channel = message.channel
        prefix = await self.get_prefix(server, msg)
        if not prefix:
            return
        alias = await self.first_word(msg[len(prefix):])

        if alias in self.images["global"]:
            image = self.images["global"][alias]
            await self.bot.send_typing(channel)
            await self.bot.send_file(channel, image)
        if server.id not in self.images["server"]:
            return
        elif alias in self.images["server"][server.id]:
            image = self.images["server"][server.id][alias]
            await self.bot.send_typing(channel)
            await self.bot.send_file(channel, image)

    async def check_command_exists(self, command, server):
        if command in self.images["server"][server.id]:
            return True
        elif await self.part_of_existing_command(command, server):
            return True
        elif command in self.images["global"]:
            return True
        else:
            return False

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def listimages(self, ctx):
        """List images for the server or globally"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.listimages_server)

    @listimages.command(pass_context=True, name="server")
    async def listimages_server(self, ctx):
        """List images added to bot"""
        msg = ""
        server = ctx.message.server
        channel = ctx.message.channel
        if server.id not in self.images["server"]:
            await self.bot.say("{} does not have any images saved!".format(server.name))
            return
        
        for image in self.images["server"][server.id].keys():
            msg += image + ", "
        em = discord.Embed(timestamp=ctx.message.timestamp)
        em.description = msg[:len(msg)-2]
        em.set_author(name=server.name, icon_url=server.icon_url)
        await self.bot.send_message(channel, embed=em)

    @listimages.command(pass_context=True, name="global", aliases=["all"])
    async def listimages_global(self, ctx):
        """List images added to bot"""
        msg = ""
        server = ctx.message.server
        channel = ctx.message.channel
        
        for image in self.images["global"].keys():
            msg += image + ", "
        em = discord.Embed(timestamp=ctx.message.timestamp)
        em.description = msg[:len(msg)-2]
        em.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        await self.bot.send_message(channel, embed=em)

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def remimage(self, ctx, cmd):
        """Add images for the bot to upload per server"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.rem_image_server, cmd=cmd)

    @remimage.command(pass_context=True, name="server")
    async def rem_image_server(self, ctx, cmd):
        """Remove a selected images"""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        cmd = cmd.lower()
        if server.id not in self.images["server"]:
            await self.bot.say("I have no images on this server!")
            return
        if cmd not in self.images["server"][server.id]:
            await self.bot.say("{} is not an image for this server!".format(cmd))
            return
        os.remove(self.images["server"][server.id][cmd])
        del self.images["server"][server.id][cmd]
        dataIO.save_json("data/addimage/settings.json", self.images)
        await self.bot.say("{} has been deleted from this server!".format(cmd))

    @checks.is_owner()
    @remimage.command(hidden=True, pass_context=True, name="global")
    async def rem_image_global(self, ctx, cmd):
        """Remove a selected images"""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        cmd = cmd.lower()
        if cmd not in self.images["global"]:
            await self.bot.say("{} is not a global image!".format(cmd))
            return
        os.remove(self.images["global"][cmd])
        del self.images["global"][cmd]
        dataIO.save_json("data/addimage/settings.json", self.images)
        await self.bot.say("{} has been deleted globally!".format(cmd))


    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def addimage(self, ctx, cmd):
        """Add images for the bot to upload per server"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.add_image_server, cmd=cmd)

    @addimage.command(pass_context=True, name="server")
    async def add_image_server(self, ctx, cmd):
        """Add an image to direct upload."""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        prefix = await self.get_prefix(server, ctx.message.content)
        msg = ctx.message
        if server.id not in self.images["server"]:
            await self.make_server_folder(server)
            self.images["server"][server.id] = {}
        if cmd is not "":
            if await self.check_command_exists(cmd, server):
                await self.bot.say("{} is already in the list, try another!".format(cmd))
                return
            else:
                await self.bot.say("{} added as the command!".format(cmd))
        await self.bot.say("Upload an image for me to use!")
        while msg is not None:
            msg = await self.bot.wait_for_message(author=author, timeout=60)
            if msg is None:
                await self.bot.say("No image uploaded then.")
                break

            if msg.attachments != []:
                filename = msg.attachments[0]["filename"][-5:]
                
                directory = "data/addimage/{}/{}".format(server.id, filename)
                if cmd is None:
                    cmd = filename.split(".")[0]
                cmd = cmd.lower()
                seed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                directory = "data/addimage/{}/{}-{}".format(server.id, seed, filename)
                self.images["server"][server.id][cmd] = directory
                dataIO.save_json("data/addimage/settings.json", self.images)
                async with self.session.get(msg.attachments[0]["url"]) as resp:
                    test = await resp.read()
                    with open(self.images["server"][server.id][cmd], "wb") as f:
                        f.write(test)
                await self.bot.send_message(channel, "{} has been added to my files!"
                                            .format(cmd))
                break
            if msg.content.lower().strip() == "exit":
                await self.bot.say("Your changes have been saved.")
                break

    @checks.is_owner()
    @addimage.command(hidden=True, pass_context=True, name="global")
    async def add_image_global(self, ctx, cmd):
        """Add an image to direct upload."""
        author = ctx.message.author
        server = ctx.message.server
        channel = ctx.message.channel
        prefix = await self.get_prefix(server, ctx.message.content)
        msg = ctx.message
        if cmd is not "":
            if await self.check_command_exists(cmd, server):
                await self.bot.say("{} is already in the list, try another!".format(cmd))
                return
            else:
                await self.bot.say("{} added as the command!".format(cmd))
        await self.bot.say("Upload an image for me to use!")
        while msg is not None:
            msg = await self.bot.wait_for_message(author=author, timeout=60)
            if msg is None:
                await self.bot.say("No image uploaded then.")
                break

            if msg.attachments != []:
                filename = msg.attachments[0]["filename"][-5:]
                
                directory = "data/addimage/global/{}".format(filename)
                if cmd is None:
                    cmd = filename.split(".")[0]
                cmd = cmd.lower()
                seed = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                directory = "data/addimage/{}/{}-{}".format(server.id, seed, filename)
                self.images["global"][cmd] = directory
                dataIO.save_json("data/addimage/settings.json", self.images)
                async with self.session.get(msg.attachments[0]["url"]) as resp:
                    test = await resp.read()
                    with open(self.images["global"][cmd], "wb") as f:
                        f.write(test)
                await self.bot.send_message(channel, "{} has been added to my files!"
                                            .format(cmd))
                break
            if msg.content.lower().strip() == "exit":
                await self.bot.say("Your changes have been saved.")
                break

def check_folder():
    if not os.path.exists("data/addimage"):
        print("Creating data/addimage folder")
        os.makedirs("data/addimage")
    if not os.path.exists("data/addimage/global"):
        print("Creating data/addimage/global folder")
        os.makedirs("data/addimage/global")

def check_file():
    data = {"global":{}, "server":{}}
    f = "data/addimage/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    n = AddImage(bot)
    bot.add_cog(n)
