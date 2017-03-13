import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import urllib.request
import hashlib
import datetime
import time
import aiohttp
import asyncio
import json

class Gab:

    GABSEARCH = "https://gab.ai/search/{}"

    def __init__(self, bot):
        self.bot = bot
        self.tags = dataIO.load_json("data/gab/gabtags.json")
        self.servers = ["261565811309674499", "261636805370183691", "288845138887704576"]

    def savetags(self, server, usertag, username):
        self.tags[server][username] = usertag
        dataIO.save_json("data/gab/gabtags.json", self.tags)
        return

    @commands.command(hidden=False)
    async def patreon(self):
        """Help on petreon!"""
        await self.bot.say("Support <@142525247357321216>  and their\
                            server/work here: https://www.patreon.com/gabanon")

    @commands.command(hiddent=False, pass_context=True)
    async def invite(self, ctx):
        """Invite link to gabanon"""
        if ctx.message.server.id in self.servers:
            await self.bot.say("https://discord.gg/WswbEcJ")

    @commands.command(pass_context=True, name="gabanon", aliases=["g", "gaba"])
    async def gabanon(self, ctx):
        """GabAnon"""
        if ctx.message.server.id in self.servers:
            chn = ctx.message.channel
            fn = "data/gab/gabanon.png"
            await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def freedomfriday(self, ctx):
        """FreedomFriday"""
        if ctx.message.server.id in self.servers:
            chn = ctx.message.channel
            fn = "data/gab/freedomfriday.jpg"
            await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def changegab(self, ctx, usertag, username: discord.Member=None):
        """Lets a user change their gab tag"""
        server = ctx.message.server.id
        if server not in self.servers:
            await self.bot.say("This only works on the GabAnon Server!")
            return

            if username is None:
                username = str(ctx.message.author)
            if username in self.tags[server]:
                await self.bot.say("You have not supplied a gab tag before, please \
                                   type `;gab gabtag` to be added to the list!")
            if usertag not in self.tags[server]:
                self.savetags(server, usertag, username)
                if username == "":
                    msg = "{0} Your gab tag has been updated to {1}!"
                    await self.bot.say(msg.format(ctx.message.author.mention,
                                                  usertag))
                else:
                    msg = "@{0} Your gab tag has been updated to {1}!"
                    await self.bot.say(msg.format(username, usertag))

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remuser(self, ctx, *, username: discord.Member=None):
        """Remomves gab tag and user"""
        server = ctx.message.server.id
        if server in self.servers:
            if str(username.id) in self.tags[server]:
                del self.tags[server][str(username.id)]
                await self.bot.say("{} has been removed from the list!"
                                   .format(username))
                dataIO.save_json("data/gab/gabtags.json", self.tags)
            else:
                msg = "That username is not in the list or has already been removed!"
                await self.bot.say(msg)

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remgab(self, ctx, gabtag):
        """Remomves gab tag and user"""
        server = ctx.message.server.id
        tags = self.tags[server]
        if ctx.message.server.id in self.servers:
            if gabtag in tags.values():
                for key, value in tags.items():
                    if gabtag in value:
                        del tags[key]
                        break
                await self.bot.say("{} has been removed from the list!".format(gabtag))
                dataIO.save_json("data/gab/gabtags.json", self.tags)
            else:
                msg = "That gab tag is not in the list or has already been removed!"
                await self.bot.say(msg)

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def listgab(self, ctx):
        """Lists all received gab tags"""
        server = ctx.message.server.id
        if server in self.servers:
            message = "```"
            username = ""
            gabtag = ""
            arrow = ""
            count = 0
            for key, value in self.tags[server].items():
                try:
                    username += ctx.message.server.get_member(key).name + "\n"
                except AttributeError:
                    username += key + "\n"
                gabtag += "⟶  " + value + "\n"
                if count == 50:
                    await self.posttags(username, gabtag)
                    username = ""
                    gabtag = ""
                    count = 0
                count += 1
            if count != 20:
                await self.posttags(username, gabtag)
        else:
            await self.bot.say("This only works in the gabanon server!")

    async def posttags(self, username, gabtag):
        embed = discord.Embed(description="Gab Tags", colour=discord.Colour.dark_grey())
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="⟶  Gab Tag", value=gabtag, inline=True)
        await self.bot.say(embed=embed)

    async def getname(self, ctx, id):
        name = ctx.message.server.get_member(id)
        await self.bot.say(name.name)

    @commands.command(pass_context=True)
    async def getid(self, ctx, username):
        name = ctx.message.server.get_member_named(username)
        await self.bot.say(name)

    def getroles(self, ctx, role):
        return {r.name: r for r in ctx.message.server.roles}[role]

    async def addgabrole(self, ctx, role):
        await asyncio.sleep(2)
        await self.bot.add_roles(ctx.message.author, self.getroles(ctx, role))
        return

    @commands.command(pass_context=True, aliases=["Gab", "GAB"])
    async def gab(self, ctx, usertag):
        """Add your gab tag to receive the role Anonymous"""
        server = ctx.message.server.id
        servername = ctx.message.server.name
        if server not in self.servers:
            await self.bot.say("Please supply the gab tag in <#266384992718946305>!")
            return

        try:
            self.tags[server]
        except KeyError:
            self.tags[server] = {}

        if "<@" in usertag:
            usertag = ctx.message.author.name
        username = ctx.message.author.id
        if username in self.tags[server]:
            await self.bot.say("You have already supplied a gab tag {}!"
                               .format(ctx.message.author.mention))
            return

        if usertag in self.tags[server].values():
            await self.bot.say("{} That Gab tag is already in use!"
                               .format(ctx.message.author.mention))
            return
        else:
            self.savetags(server, usertag, username)
            if server == "261565811309674499":
                await self.addgabrole(ctx, "Anonymous")
                await self.addgabrole(ctx, "Guest")
            await self.bot.say("Hello {0}, welcome to {1}!"
                               .format(ctx.message.author.mention, servername))
            asyncio.sleep(2)
            if server == "261565811309674499":
                await self.bot.remove_roles(ctx.message.author, self.getroles(ctx, "newcomer"))

        # TODO: Remove gab tag after message sent

def check_folder():
    if not os.path.exists("data/gab"):
        print("Creating data/gab folder")
        os.makedirs("data/gab")


def check_file():
    data = {"": {"": ""}}
    f = "data/gab/gabtags.json"
    if not dataIO.is_valid_json(f):
        print("Creating default gabtags.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Gab(bot))

