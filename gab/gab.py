import discord
from discord.ext import commands
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
        default_user = {"gab_tag":None}
        default_guild = {"channel":None, "role_add":None, "role_remove":None, "require_gab":False}
        default_global = {"login":{"username":"", "password":""}, "cookies":{}}
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.api_link = "https://gab.ai/auth/login"
        self.search_user = "https://gab.ai/users/{}"

    @commands.group(pass_context=True)
    async def gab(self, ctx, usertag=""):
        """Add your gab tag to receive the role Anonymous"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.register_gab, usertag)


    def get_roles(self, ctx, role):
        return {r.id: r for r in ctx.message.guild.roles}[role]

    async def addgabrole(self, ctx, role):
        await ctx.message.author.add_roles(self.get_roles(ctx, role))
        return

    async def check_gab_usernames(self, username):
        """Checks the gab user feed of a user to see if it exists"""
        with aiohttp.ClientSession() as session:
            async with session.get(self.api_link) as resp:
                data = await resp.text()
                soup = BeautifulSoup(data, "html.parser")
                token = soup.find("input", {"name": "_token"}).get("value")
                login = {"username":await self.config.login.username(), 
                         "password":await self.config.login.password(), 
                         "_token":token, 
                         "remember": True}
            async with session.post(self.api_link, data=login) as resp:
                await self.config.cookies.set(resp.cookies)
            async with session.get(self.search_user.format(username)) as resp:
                data = await resp.json()
                if "status" in data:
                    return False
                else:
                    return True
    
    @gab.command(pass_context=True)
    async def set(self, ctx, channel: discord.TextChannel, role_add: discord.Role, role_remove: discord.Role=None):
        guild = ctx.message.guild
        await self.config.guild(guild).channel.set(channel.id)
        await self.config.guild(guild).role_add.set(role_add.id)
        await self.config.guild(guild).role_remove.set(role_remove)
        await self.config.guild(guild).require_gab.set(True)
        await ctx.send("Accepting gab tags in {} and applying role {}".format(channel, role_add))

    @gab.command()
    async def toggle(self, ctx):
        guild = ctx.message.guild
        if await self.config.guild(guild).require_gab():
            await self.config.guild(guild).require_gab.set(False)
            await ctx.send("Accepting gab tags now.")
        else:
            await self.config.guild(guild).require_gab.set(True)
            await ctx.send("Not accepting gab tags now.")

    @gab.command()
    async def login(self, ctx, username, password):
        await self.config.login.username.set(username)
        await self.config.login.password.set(password)
        await ctx.send("Login info set for gab.")

    @gab.command(pass_context=True)
    async def register_gab(self, ctx, usertag:str):
        guild = ctx.message.guild
        guildname = ctx.message.guild.name
        channel = ctx.message.channel
        if not await self.config.guild(guild).require_gab():
            return
        correct_channel = guild.get_channel(await self.config.guild(guild).channel())
        if channel != correct_channel:
            await ctx.send("Please supply the gab tag in {}!".format(correct_channel.mention))
            return

        if "<@" in usertag:
            usertag = ctx.message.author.display_name
        author = ctx.message.author

        is_real_account = await self.check_gab_usernames(usertag)

        if not is_real_account:
            await ctx.send("That gab account does not exist! Please try again or ask for some help.")
            return

        await self.config.user(author).gab_tag.set(usertag)
        await self.addgabrole(ctx, await self.config.guild(guild).role_add())
        await ctx.send("Hello {0}, welcome to {1}!"
                           .format(ctx.message.author.mention, guildname))
        if await self.config.guild(guild).role_remove() is not None:
            await ctx.message.author.role_remove(self.get_roles(ctx, await self.config.guild(guild).role_remove()))
