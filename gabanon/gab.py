import discord
from discord.ext import commands
from .utils.chat_formatting import *
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

    def checktags(self, usertag):
        with open("data/gab/gabtags.json", "rb") as taglist:
            tags = json.loads(taglist.read())
        return " ".join("{}".format(value) for key, value in tags.items() if value in usertag)

    def checkuser(self, username):
        with open("data/gab/gabtags.json", "rb") as taglist:
            tags = json.loads(taglist.read())
        return " ".join("{}".format(key) for key, value in tags.items() if key in username)

    def savetags(self, usertag, username):
        with open("data/gab/gabtags.json", "r") as infile:
            tags = json.loads(infile.read())
        with open("data/gab/gabtags.json", "w") as outfile:
            tags[username] = usertag
            json.dump(tags, outfile)
        return

    @commands.command(hidden=False)
    async def patreon(self):
        """Help on petreon!"""
        await self.bot.say("Support @CZΛR  and his server/work here: https://www.patreon.com/gabanon")
    
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
    async def listgab(self, ctx):
        """Lists all received gab tags"""
        if ctx.message.server.id == "261565811309674499" or ctx.message.channel.id == "268584315401666561":
            message = "```"
            with open("data/gab/gabtags.json", "r") as taglist:
                tags = json.loads(taglist.read())
                for key, value in tags.items():
                    message += "{0} | {1} \n".format(key, value)
                await self.bot.say(message + "```")
        else:
            await self.bot.say("This only works in the gabanon server!")

    @commands.command(pass_context=True)
    async def gab(self, ctx, usertag):
        """Add your gab tag to receive the role Anonymous"""
        if ctx.message.channel.id == "266384992718946305" or ctx.message.channel.id == "268584315401666561":
            username = str(ctx.message.author)
            checktags = self.checktags(usertag)
            checkuser = self.checkuser(username)
            if checktags == "" and checkuser != "":
                await self.bot.say("You have already supplied a gab tag {}!".format(ctx.message.author.mention))
            if checktags == usertag and checkuser == "":
                await self.bot.say("{} That Gab tag is already in use!".format(ctx.message.author.mention))
            if checktags != usertag and checkuser == "":
                self.savetags(usertag, username)
                if ctx.message.channel.id != "268584315401666561":
                    await self.bot.add_roles(ctx.message.author, {r.name: r for r in ctx.message.server.roles}['Anonymous'])
                await self.bot.say("Hello {}, welcome to #GabAnon!".format(ctx.message.author.mention))
                time.sleep(2)
                if ctx.message.channel.id != "268584315401666561":
                    await self.bot.remove_roles(ctx.message.author, {r.name: r for r in ctx.message.server.roles}['newcomer'])
            if checktags != "" and checkuser != "":
                await self.bot.say("You have already supplied the same gab tag {}!".format(ctx.message.author.mention))
        else:
            await self.bot.say("Please supply the gab tag in #gab-tags!")


def setup(bot):
    n = GabBot(bot)
    # bot.add_listener(n.gab, "on_message")
    bot.add_cog(n)

