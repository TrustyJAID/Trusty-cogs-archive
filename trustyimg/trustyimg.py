import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
from random import choice
import urllib.request
import hashlib
import aiohttp
import asyncio


class TrustyIMG:

    def __init__(self, bot):
        self.bot = bot
        self.images = dataIO.load_json("data/trustyimg/images.json")

    # Image Commands #
    @commands.command(pass_context=True)
    async def kappa(self, ctx):
        """kappa"""
        await self.bot.send_file(ctx.message.channel, self.images["kappa"])

    @commands.command(pass_context=True)
    async def cheers(self, ctx):
        """cheers!"""
        await self.bot.send_file(ctx.message.channel, self.images["cheers"])

    @commands.command(pass_context=True, aliases=["btcup"])
    async def tothemoon(self, ctx):
        """To the moon!!"""
        await self.bot.send_file(ctx.message.channel, self.images["ttm"])

    @commands.command(pass_context=True)
    async def btcdown(self, ctx):
        """NOT To the moon!!"""
        await self.bot.send_file(ctx.message.channel, self.images["nttm"])

    @commands.command(pass_context=True, aliases=["hacker"])
    async def hackerman(self, ctx):
        """Hackerman"""
        await self.bot.send_file(ctx.message.channel, self.images["hackerman"])

    @commands.command(pass_context=True)
    async def kiddo(self, ctx):
        """kiddo"""
        await self.bot.send_file(ctx.message.channel, self.images["kiddo"])

    @commands.command(pass_context=True)
    async def nsa(self, ctx):
        """NSA"""
        await self.bot.send_file(ctx.message.channel, self.images["nsa"])
    
    @commands.command(pass_context=True)
    async def cia(self, ctx):
        """CIA"""
        await self.bot.send_file(ctx.message.channel, self.images["cia"])

    @commands.command(pass_context=True)
    async def wikileaks(self, ctx):
        """wikileaks"""
        await self.bot.send_file(ctx.message.channel, self.images["wikileaks"])

    @commands.command(pass_context=True, aliases=["openyoureyes"])
    async def woke(self, ctx):
        """Posts tim and eric gif"""
        await self.bot.send_file(ctx.message.channel, self.images["woke"])

    @commands.command(pass_context=True)
    async def canary(self, ctx):
        """TrustyBot Canary"""
        await self.bot.send_file(ctx.message.channel, self.images["canary"])

    @commands.command(pass_context=True)
    async def wtf(self, ctx):
        """lol"""
        await self.bot.send_file(ctx.message.channel, self.images["wtf"])

    @commands.command(pass_context=True)
    async def vapormaga(self, ctx):
        """lol"""
        await self.bot.send_file(ctx.message.channel, self.images["vapormaga"])

    @commands.command(pass_context=True)
    async def thisisfine(self, ctx):
        """lol"""
        await self.bot.send_file(ctx.message.channel, self.images["thisisfine"])

    @commands.command(pass_context=True, aliases=["gg"])
    async def gremblygunk(self, ctx):
        """Gremblygunk"""
        await self.bot.send_file(ctx.message.channel, self.images["gremblygunk"])

    @commands.command(pass_context=True)
    async def badge(self, ctx):
        """WIA Badge"""
        await self.bot.send_file(ctx.message.channel, self.images["badge"])

    @commands.command(pass_context=True)
    async def wrong(self, ctx):
        """Wrong gif"""
        await self.bot.send_file(ctx.message.channel, self.images["wrong"])

    @commands.command(pass_context=True)
    async def ohno(self, ctx):
        """ohno"""
        await self.bot.send_file(ctx.message.channel, self.images["ohno"])

    @commands.command(pass_context=True, aliases=["ay", "duck"])
    async def awyiss(self, ctx):
        """Aw Yiss Duck"""
        await self.bot.send_file(ctx.message.channel, self.images["awyiss"])

    @commands.command(pass_context=True, aliases=["buildthewall", "build"])
    async def wall(self, ctx):
        """Pepe Wall"""
        await self.bot.send_file(ctx.message.channel, self.images["wall"])

    @commands.command(pass_context=True, aliases=["trustyjaid"])
    async def trusty(self, ctx):
        """Trusty Meme"""
        await self.bot.send_file(ctx.message.channel, self.images["trusty"])

    @commands.command(pass_context=True, aliases=["takemetobernie"])
    async def bernie(self, ctx):
        """bernie Meme"""
        await self.bot.send_file(ctx.message.channel, self.images["bernie"])

    @commands.command(pass_context=True, aliases=["JAK"])
    async def juliankills(self, ctx):
        """JA Kills"""
        await self.bot.send_file(ctx.message.channel, self.images["jakills"])

    @commands.command(pass_context=True, aliases=["whereisassange"])
    async def wia(self, ctx):
        """wia Meme"""
        await self.bot.send_file(ctx.message.channel, self.images["wia"])

    @commands.command(pass_context=True, aliases=["Julian"])
    async def jakek(self, ctx):
        """Julian Assange kek"""
        await self.bot.send_file(ctx.message.channel, self.images["jakek"])

    @commands.command(pass_context=True)
    async def getout(self, ctx):
        """get out pepe"""
        await self.bot.send_file(ctx.message.channel, self.images["getout"])

    @commands.command(pass_context=True)
    async def kek(self, ctx):
        """kek"""
        await self.bot.send_file(ctx.message.channel, self.images["kek"])

    @commands.command(pass_context=True, aliases=["fgm"])
    async def feelsgoodman(self, ctx):
        """Feels good man"""
        await self.bot.send_file(ctx.message.channel, self.images["feelsgoodman"])

    @commands.command(pass_context=True, aliases=["troll"])
    async def trollface(self, ctx):
        """Troll Face"""
        await self.bot.send_file(ctx.message.channel, self.images["troll"])

    @commands.command(pass_context=True)
    async def problem(self, ctx):
        """Problem"""
        await self.bot.send_file(ctx.message.channel, self.images["problem"])

    @commands.command(pass_context=True)
    async def thinking(self, ctx):
        """Thinking"""
        await self.bot.send_file(ctx.message.channel, self.images["thinking"])

    @commands.command(pass_context=True, aliases=["db"])
    async def dickbutt(self, ctx):
        """DickButt"""
        ext = ["png", "gif"]
        if ctx.message.server.id != "261565811309674499":
            await self.bot.send_file(ctx.message.channel, self.images["dickbutt"]
                                     .format(choice(ext)))

    @commands.command(pass_context=True)
    async def cookie(self, ctx, user=None):
        """cookie"""
        msg = "Here's a cookie {}! :smile:"
        if user is None:
            await self.bot.send_file(ctx.message.channel, self.images["cookie"])
        else:
            await self.bot.send_file(ctx.message.channel, self.images["cookie"],
                                     content=msg.format(user))

    @commands.command(pass_context=True, aliases=["tf"])
    async def tinfoil(self, ctx):
        """Liquid Metal Embrittlement"""
        await self.bot.send_file(ctx.message.channel, self.images["tinfoil"]
                                 .format(choice(["1", "2"])))

    @commands.command(pass_context=True,)
    async def donate(self, ctx):
        """Donate some bitcoin!"""
        gabcoin = "1471VCzShn9kBSrZrSX1Y3KwjrHeEyQtup"
        DONATION = "1DMfQgbyEW1u6M2XbUt5VFP6JARNs8uptQ"
        msg = "Feel free to send bitcoin donations to `{}` :smile:"
        gabimg = "data/trustybot/gabbtc.jpg"
        img = "data/trustybot/btc.png"
        if ctx.message.server.id == "261565811309674499":
            await self.bot.send_file(ctx.message.channel, gabimg)
            await self.bot.say(msg.format(gabcoin))
        else:
            await self.bot.send_file(ctx.message.channel, img)
            await self.bot.say(msg.format(DONATION))


def setup(bot):
    n = TrustyIMG(bot)
    bot.add_cog(n)
