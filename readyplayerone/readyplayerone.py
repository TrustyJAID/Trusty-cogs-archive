import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from cogs.utils import checks
from random import choice
from binascii import unhexlify
from datetime import timedelta
import time
import random
import hashlib
import aiohttp
import asyncio
import string
import re

class ReadyPlayerOne:

    def __init__(self, bot):
        self.bot = bot
        self.clues = ["***Three hidden keys open three secret gates\nWherein the errant will be tested for worthy traits\nAnd those with the skill to survive these straits\nWill reach The End where the prize awaits***",
                      "***The Copper Key awaits explorers\nIn a tomb filled with horrors\nBut you have much to learn\nIf you hope to earn\nA place among the high scorers***",
                      "***What you seek lies hidden in the trash on the deepest level of Daggorath.***",
                      "***The captain conceals the Jade Key\nin a dwelling long neglected\nBut you can only blow the whistle\nonce the trophies are all collected***",
                      "***Continue your quest by taking the test.***",
                      "data/trustybot/img/clue.jpg",
                      "***The first was ringed in red metal\nThe second, in green stone\nThe third is clearest crystal\nAnd cannot be unlocked alone***"]

    @commands.command(pass_context=True)
    async def rpomovie(self, ctx):
        time_left = timedelta(seconds=abs(1522368000 - time.time()), microseconds=0)
        time_left = time_left - timedelta(microseconds=time_left.microseconds)
        embed = discord.Embed(title="{}".format(time_left),
                              description="Until Ready Player One The Movie!",
                              url="https://youtu.be/0h3zL-IA_KI",
                              timestamp=ctx.message.timestamp)
        embed.set_image(url="https://images-na.ssl-images-amazon.com/images/M/MV5BMjM0MzkxMzU2M15BMl5BanBnXkFtZTgwODg2NTg5MjI@._V1_SY1000_CR0,0,674,1000_AL_.jpg")
        await self.bot.send_message(ctx.message.channel, embed=embed)
    
    @commands.command(pass_context=True)
    async def clue(self, ctx, number="1"):
        channel = ctx.message.channel
        if not number.isdigit():
            for clue in self.clues:
                if number in clue:
                    await self.bot.send_typing(channel)
                    await self.bot.say(clue)
        if number.isdigit() and (int(number) < 0 or int(number) > 7):
            await self.bot.send_typing(channel)
            await self.bot.say("There are only 7 clues.")
        if number.isdigit() and (int(number) > 0 or int(number) < 7):
            if ".jpg" in self.clues[int(number)-1]:
                await self.bot.send_typing(channel)
                await self.bot.send_file(channel, self.clues[int(number)-1])
            else:
                await self.bot.send_typing(channel)
                await self.bot.say(self.clues[int(number)-1])
        else:
            await self.bot.send_typing(channel)
            await self.bot.say("I could not find that clue.")
        

def setup(bot):
    n = ReadyPlayerOne(bot)
    bot.add_cog(n)
