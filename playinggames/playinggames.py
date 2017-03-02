import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
from enum import Enum
import time
import asyncio
import random
import codecs


class playinggames:

    def __init__(self, bot):
        self.bot = bot
        self.games = dataIO.load_json("data/playinggames/games.json")

    @commands.command(hidden=False, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def addgame(self, ctx, message):
        """Add to the list of games TrustyBot is playing
            ;addgame "Hello, world!"
            ;addgame Game-I-Can-Play        
        """
        self.games.append(message)
        dataIO.save_json("data/playinggames/games.json", self.games)
        await self.bot.say("{} added to games list!".format(message))

    @commands.command(pass_context=True)
    async def listgames(self, ctx):
        """lists the games TrustyBot can play"""
        message = "```\n"
        count = 0
        channel = ctx.message.channel
        for game in self.games:
            message += "Playing " + game + "\n"
            count += 1
            if count == 20:
                await self.bot.send_message(channel, message + "```")
                message = "```"
                count = 0
        message += "```"
        await self.bot.send_message(channel, message)

    async def changestatus(self):
            await self.bot.wait_until_ready()
            while not self.bot.is_closed:
                gamesplaying = random.choice(self.games)
                await self.bot.change_presence(
                    game=discord.Game(name=gamesplaying,
                                      status=discord.Status.online))
                await asyncio.sleep(300)


def setup(bot):
    n = playinggames(bot)
    bot.loop.create_task(n.changestatus())
    bot.add_cog(n)