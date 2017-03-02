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

class GabBot:

    GABSEARCH = "https://gab.ai/search/{}"

    def __init__(self, bot):
        self.bot = bot
        self.tags = dataIO.load_json("data/gab/gabtags.json")

    def checktags(self, usertag):
        return " ".join(value for key, value in self.tags.items() if value in usertag)

    def checkuser(self, username):
        return " ".join(key for key, value in self.tags.items() if key in username)

    def gettags(self, usertag):
        return " ".join(value for key, value in self.tags.items() if key in usertag)

    def getuser(self, username):
        return " ".join(key for key, value in self.tags.items() if value in username)

    def savetags(self, usertag, username):
        self.tags[username] = usertag
        dataIO.save_json("data/gab/gabtags.json", self.tags)
        return

    @commands.command(hidden=False)
    async def patreon(self):
        """Help on petreon!"""
        await self.bot.say("Support <@142525247357321216>  and their server/work here: https://www.patreon.com/gabanon")

    @commands.command(hiddent=False, pass_context=True)
    async def invite(self, ctx):
        """Invite link to gabanon"""
        if ctx.message.server.id == "261565811309674499" or ctx.message.channel.id == "268584315401666561":
            await self.bot.say("https://discord.gg/WswbEcJ")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def changegab(self, ctx, usertag, username=""):
        """Lets a user change their gab tag"""
        if ctx.message.channel.id == "266384992718946305" or ctx.message.channel.id == "268584315401666561":
            if username == "":
                username = str(ctx.message.author)
            checktags = self.checktags(usertag)
            checkuser = self.checkuser(username)
            if checkuser != username:
                await self.bot.say("You have not supplied a gab tag before, please type `;gab gabtag` to be added to the list!")
            if checktags != usertag and username == checkuser:
                self.savetags(usertag, username)
                if username == "":
                    await self.bot.say("{0} Your gab tag has been updated to {1}!".format(ctx.message.author.mention, usertag))
                else:
                    await self.bot.say("@{0} Your gab tag has been updated to {1}!".format(username, usertag))

        else:
            await self.bot.say("This only works in the #gab-tags channel!")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remuser(self, ctx, *, username: discord.Member=None):
        """Remomves gab tag and user"""
        if ctx.message.server.id == "261565811309674499" or ctx.message.channel.id == "268584315401666561":
            checkuser = self.checkuser(str(username))
            if checkuser != "":
                del self.tags[checkuser]
                await self.bot.say("{} has been removed from the list!".format(username))
                dataIO.save_json("data/gab/gabtags.json", self.tags)
            else:
                await self.bot.say("That username is not in the list or has already been removed!")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remgab(self, ctx, gabtag):
        """Remomves gab tag and user"""
        if ctx.message.server.id == "261565811309674499" or ctx.message.channel.id == "268584315401666561":
            checktag = self.checktags(gabtag)
            getuser = self.getuser(gabtag)
            if checktag != "":
                del self.tags[getuser]
                await self.bot.say("{} has been removed from the list!".format(gabtag))
                dataIO.save_json("data/gab/gabtags.json", self.tags)
            else:
                await self.bot.say("That gab tag is not in the list or has already been removed!")

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def listgab(self, ctx):
        """Lists all received gab tags"""
        if ctx.message.server.id == "261565811309674499" or ctx.message.channel.id == "268584315401666561":
            message = "```"
            username = ""
            gabtag = ""
            arrow = ""
            count = 0
            for key, value in self.tags.items():
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
        if ctx.message.channel.id == "266384992718946305" or ctx.message.channel.id == "268584315401666561":
            if "<@" in usertag:
                usertag = ctx.message.author.name
            username = ctx.message.author.id
            checktags = self.checktags(usertag)
            checkuser = self.checkuser(username)
            if checktags == "" and checkuser != "":
                await self.bot.say("You have already supplied a gab tag {}!".format(ctx.message.author.mention))
            if checktags == usertag and checkuser == "":
                await self.bot.say("{} That Gab tag is already in use!".format(ctx.message.author.mention))
            if checktags != usertag and checkuser == "":
                self.savetags(usertag, username)
                if ctx.message.channel.id != "268584315401666561":
                    await self.addgabrole(ctx, "Anonymous")
                    await self.addgabrole(ctx, "Guest")
                await self.bot.say("Hello {}, welcome to #GabAnon!".format(ctx.message.author.mention))
                asyncio.sleep(2)
                if ctx.message.channel.id != "268584315401666561":
                    await self.bot.remove_roles(ctx.message.author, self.getroles(ctx, "newcomer"))
            if checktags != "" and checkuser != "":
                await self.bot.say("You have already supplied the same gab tag {}!"
                                   .format(ctx.message.author.mention))
        else:
            await self.bot.say("Please supply the gab tag in <#266384992718946305>!")
        # TODO: Remove gab tag after message sent


def setup(bot):
    n = GabBot(bot)
    # bot.add_listener(n.gab, "on_message")
    bot.add_cog(n)

