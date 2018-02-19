import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from redbot.core import checks
from redbot.core import Config
import asyncio
import os
import urllib.request
import aiohttp
import json
from bs4 import BeautifulSoup

class Gab:

    def __init__(self, bot):
        self.bot = bot
        # self.tags = dataIO.load_json("data/gab/gabtags.json")
        self.config = Config.get_conf(self, 17864784635)
        default_user = {"gab_tag":""}
        default_guild = {"channel":None, "role_add":None, "role_remove":None, "require_gab":False}
        default_global = {"login":{"username":"", "password":""}}
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.guilds = ["261565811309674499", "321105104931389440"]
        self.api_link = "https://gab.ai/auth/login"
        # self.settings = dataIO.load_json("data/gab/settings.json")
        self.search_user = "https://gab.ai/users/{}"

    @commands.group(pass_context=True)
    async def gab(self, ctx, usertag=""):
        """Add your gab tag to receive the role Anonymous"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.register_gab)    

    @gab.command(hidden=True)
    async def patreon(self):
        """Help on petreon!"""
        msg = "Support <@142525247357321216>  and their guild/work here: https://www.patreon.com/gabanon"
        await ctx.send(msg)

    @gab.command(hidden=True, pass_context=True)
    async def invite(self, ctx):
        """Invite link to gabanon"""
        if ctx.message.guild.id in self.guilds:
            await ctx.send("https://discord.gg/WswbEcJ")

    @gab.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def change(self, ctx, usertag, username: discord.Member=None):
        """Lets a user change their gab tag"""
        guild = ctx.message.guild.id
        if guild not in self.guilds:
            await ctx.send("This only works on the GabAnon guild!")
            return

            if username is None:
                username = str(ctx.message.author)
            if username in self.tags[guild]:
                await ctx.send("You have not supplied a gab tag before, please \
                                   type `;gab gabtag` to be added to the list!")
            if usertag not in self.tags[guild]:
                self.save_tags(guild, usertag, username)
                if username == "":
                    msg = "{0} Your gab tag has been updated to {1}!"
                    await ctx.send(msg.format(ctx.message.author.mention,
                                                  usertag))
                else:
                    msg = "@{0} Your gab tag has been updated to {1}!"
                    await ctx.send(msg.format(username, usertag))

    @gab.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove(self, ctx, gabtag):
        """Remomves gab tag and user"""
        guild = ctx.message.guild.id
        tags = self.tags[guild]
        if gabtag in tags.values():
            for key, value in tags.items():
                if gabtag in value:
                    del tags[key]
                    break
            await ctx.send("{} has been removed from the list!".format(gabtag))
            dataIO.save_json("data/gab/gabtags.json", self.tags)
        else:
            msg = "That gab tag is not in the list or has already been removed!"
            await ctx.send(msg)


    def get_roles(self, ctx, role):
        return {r.name: r for r in ctx.message.guild.roles}[role]

    async def addgabrole(self, ctx, role):
        await asyncio.sleep(2)
        await self.bot.add_roles(ctx.message.author, self.get_roles(ctx, role))
        return

    async def check_gab_usernames(self, username):
        """Checks the gab user feed of a user to see if it exists"""
        with aiohttp.ClientSession() as session:
            async with session.get(self.api_link) as resp:
                data = await resp.text()
                soup = BeautifulSoup(data, "html.parser")
                token = soup.find("input", {"name": "_token"}).get("value")
                login = {"username":self.settings["login"]["username"], 
                         "password":self.settings["login"]["password"], 
                         "_token":token, 
                         "remember": True}
            async with session.post(self.api_link, data=login) as resp:
                self.settings["cookies"] = resp.cookies
                dataIO.save_json("data/gab/settings.json", self.settings)
            async with session.get(self.search_user.format(username)) as resp:
                data = await resp.json()
                if "status" in data:
                    return False
                else:
                    return True
    
    @gab.command(pass_context=True)
    async def set(self, ctx, channel: discord.Channel, role_add: discord.Role, role_remove: discord.Role=None):
        guild = ctx.message.guild
        if guild.id not in self.tags:
            self.tags[guild.id] = {}
        self.save_tags(guild.id, role_add.name, "role_add")
        self.save_tags(guild.id, channel.id, "channel")
        if role_remove is not None:
            self.save_tags(guild.id, role_remove.name, "role_remove")
        await ctx.send("Accepting gab tags in {} and applying role {}".format(channel, role_add))

    @gab.command(pass_context=True)
    async def register_gab(self, ctx, usertag:str):
        guild = ctx.message.guild
        guildname = ctx.message.guild.name
        channel = ctx.message.channel.id
        if not await self.config.guild(guild).require_gab:
            return
        correct_channel = self.bot.get_channel(id=await self.config.guild(guild).channel)
        if channel != correct_channel.id:
            await ctx.send("Please supply the gab tag in {}!".format(correct_channel.mention))
            return

        if "<@" in usertag:
            usertag = ctx.message.author.display_name
        author = ctx.message.author

        is_real_account = await self.check_gab_usernames(usertag)

        if not is_real_account:
            await ctx.send("That gab account does not exist! Please try again or ask for some help.")
            return

        if await self.config.user(author) != "":
            await ctx.send("You have already supplied a gab tag {}!"
                               .format(ctx.message.author.mention))
            return

        else:
            self.save_tags(guild, usertag, username)
            await self.addgabrole(ctx, self.tags[guild]["role_add"])
            if guild == "261565811309674499":
                # await self.addgabrole(ctx, "Anonymous")
                await self.addgabrole(ctx, "Guest")
            await ctx.send("Hello {0}, welcome to {1}!"
                               .format(ctx.message.author.mention, guildname))
            if "role_remove" in self.tags[guild]:
                await self.bot.role_remove(ctx.message.author, self.get_roles(ctx, self.tags[guild]["role_remove"]))

    async def on_member_join(self, member):
        guild = member.guild
        if await self.config.guild(guild).require_gab:
            if await self.config.user(author) != "":
                await self.addgabrole(ctx, await self.config.guild(guild).add_role)
                if await self.config.guild(guild).role_remove != None:
                    await member.role_removes(self.get_roles(await self.config.guild(guild).role_remove))