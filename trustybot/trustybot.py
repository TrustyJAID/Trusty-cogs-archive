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
import random
import codecs
import json


class TrustyBot:
    def __init__(self, bot):
        self.bot = bot
        self.poll_sessions = []
        self.text = dataIO.load_json("data/trustybot/messages.json")
        self.links = dataIO.load_json("data/trustybot/links.json")

    # Text Commands #
    @commands.command(hidden=False)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def grep(self):
        """Get the fuck out of here with grep!"""
        await self.bot.say("Get the fuck out of here with grep!")

    @commands.command(name="repos", aliases=["github"])
    async def repos(self):
        """Links to github"""
        await self.bot.say(self.links["github"])

    @commands.command(name="wlff", aliases=["WLFF"])
    async def wlff(self):
        """Links to github"""
        await self.bot.say(self.links["wlff"])

    @commands.command(name="pol", aliases=["POL", "proofoflife"])
    async def pol(self):
        """Links to Proof of life timeline"""
        await self.bot.say(self.links["pol"])

    @commands.command(name="disinfo", aliases=["DISINFO"])
    async def disinfo(self):
        """Links to disinfo thread"""
        await self.bot.say(self.links["disinfo"])

    @commands.command(hidden=False)
    async def python(self):
        """Links to github"""
        await self.bot.say(self.links["python"])

    @commands.command(hidden=False)
    async def go(self):
        """Links to github"""
        await self.bot.say(self.links["go"])

    @commands.command(hidden=False)
    async def documentation(self):
        """Links to github"""
        await self.bot.say(self.links["documentation"])

    @commands.command(hidden=False)
    async def btcchina(self):
        """Bitcoin China Comic"""
        await self.bot.say(self.links["btcchina"])

    @commands.command(hidden=False)
    async def smarm(self):
        """Gawker Smarm Article"""
        await self.bot.say(self.links["smarm"])

    @commands.command(name="pineal", aliases=["pineal gland"])
    async def pinealGland(self, message=None):
        """Links to pineal gland"""
        if message == "calcification" or message == "calcified":
            await self.bot.say(self.links["pineal"][1])
        if message == "healthy":
            await self.bot.say(self.links["pineal"][2])
        if message is None:
            await self.bot.say(self.links["pineal"][0])

    @commands.command(hidden=False, pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def wew(self, ctx):
        """wew"""
        await self.bot.say(self.text["wew"])

    @commands.command(hiddent=False, pass_context=True)
    async def illuminati(self, ctx):
        """o.o"""
        emilum = ["\U0001F4A1", "\U000026A0", "\U0000203C", "\U000026D4"]
        ilum = ":bulb: :warning: :bangbang: :no_entry:"
        msg = await self.bot.say(ilum)
        for i in emilum:
            await self.bot.add_reaction(msg, emoji=i)

    @commands.command(hidden=False)
    async def halp(self, user=None):
        """How to ask for help!"""
        msg = "{} please type `;help` to be PM'd all my commands! :smile:"
        if user is None:
            await self.bot.say(msg.format(""))
        else:
            await self.bot.say(msg.format(user))
    
    @commands.command(hidden=False)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def goodshit(self):
        """GOODSHIT"""
        await self.bot.say(self.text["goodshit"])

    @commands.command(name="maga", aliases=["MAGA", "nevercomedown"])
    async def maga(self):
        """I don't care if I ever come down!"""
        await self.bot.say(self.links["maga"])

    @commands.command(name="kara", aliases=["nevercomedown2"])
    async def kara(self):
        """I don't care if I ever come down!"""
        await self.bot.say(self.links["kara"])

    @commands.command(aliases=["elder", "phoenix"])
    async def elderphoenix(self):
        """lol"""
        await self.bot.say(choice(self.links["elder"]))

    @commands.command(aliases=["directthecheckerd"])
    async def elmyr(self):
        """lol"""
        await self.bot.say(choice(self.links["elmyr"]))

    @commands.command(name="straya", aliases=["ec", "embassycat", "thorium", "sympoz"])
    async def straya(self):
        """Straya"""
        await self.bot.say(choice(self.links["straya"]))

    @commands.command(name="kingdonald", aliases=["KD", "kd"])
    async def kingdonald(self):
        """KingDonald"""
        await self.bot.say(choice(self.links["KingDonald"]))

    @commands.command(name="wsa", aliases=["WSA"])
    async def wsa(self):
        """lol"""
        await self.bot.say(self.links["wsa"])

    @commands.command(name="neon", aliases=["NEON"])
    async def neon(self):
        """lol"""
        await self.bot.say(self.links["neon"])

    @commands.command(name="death", aliases=["DEATH"])
    async def death(self):
        """lol"""
        await self.bot.say(self.links["death"])

    @commands.command(name="ventucky", aliases=["ven"])
    async def ventucky(self):
        """lol"""
        await self.bot.say(choice(self.links["ventucky"]))

    @commands.command(hidden=False)
    async def lenny(self):
        """Lenny"""
        await self.bot.say(self.text["lenny"])

    @commands.command(hidden=False, pass_context=True, aliases=["meme_queen"])
    async def mq(self, ctx):
        """Lol"""
        await self.bot.say("You're cute <@245862769054711809> :smile:")

    @commands.command(hidden=False)
    async def kawaii(self):
        """kawaii"""
        await self.bot.say(self.text["kawaii"])

    @commands.command(hidden=False)
    @checks.is_owner()
    async def crash(self):
        """wew"""
        await self.bot.say(self.text["iOSCrash"])

    @commands.command(hidden=False)
    async def fuckyou(self):
        """What did you fucking say about me"""
        await self.bot.say(self.text["fuckyou"])

    @commands.command(hidden=False)
    async def dreams(self):
        """don't let your dreams be dreams"""
        await self.bot.say(self.text["dreams"].format("dreams"))

    @commands.command(hidden=False)
    async def memes(self):
        """don't let your memes be dreams"""
        await self.bot.say(self.text["dreams"].format("memes"))

    @commands.command(hidden=False)
    async def awsum(self):
        """awsum"""
        await self.bot.say(self.text["awsum"])

    @commands.command(hidden=False)
    async def wut(self):
        """wut"""
        await self.bot.say(self.text["wut"])

    @commands.command(hidden=False, pass_context=True)
    async def shrug(self, ctx):
        """shrug"""
        await self.bot.say(self.text["shrug"])

    @commands.command(pass_context=True, name="soon", aliases=["s"])
    async def soon(self, ctx):
        """Soon™"""
        await self.bot.say(self.text["soon"])

    @commands.command(pass_context=True, aliases=["areyoukiddingme"])
    async def aykm(self, ctx):
        """ಠ_ಠ"""
        await self.bot.say(self.text["aykm"])

    @commands.command(pass_context=True)
    async def topkek(self, ctx):
        """topkek"""
        await self.bot.say(self.text["topkek"])

    # Image Commands #
    @commands.command(pass_context=True)
    async def kappa(self, ctx):
        """kappa"""
        chn = ctx.message.channel
        fn = "data/trustybot/kappa.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def cheers(self, ctx):
        """cheers!"""
        chn = ctx.message.channel
        fn = "data/trustybot/cheers.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["btcup"])
    async def tothemoon(self, ctx):
        """To the moon!!"""
        chn = ctx.message.channel
        fn = "data/trustybot/roller-coaster-guy.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def btcdown(self, ctx):
        """NOT To the moon!!"""
        chn = ctx.message.channel
        fn = "data/trustybot/roller-coaster-guy-down.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["hacker"])
    async def hackerman(self, ctx):
        """Hackerman"""
        chn = ctx.message.channel
        fn = "data/trustybot/hackerman.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def kiddo(self, ctx):
        """kiddo"""
        chn = ctx.message.channel
        fn = "data/trustybot/kiddo.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def nsa(self, ctx):
        """NSA"""
        chn = ctx.message.channel
        fn = "data/trustybot/nsa.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def wikileaks(self, ctx):
        """wikileaks"""
        chn = ctx.message.channel
        fn = "data/trustybot/wikileaks.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["openyoureyes"])
    async def woke(self, ctx):
        """Posts tim and eric gif"""
        chn = ctx.message.channel
        fn = "data/trustybot/tim-and-eric-mind-blown.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def canary(self, ctx):
        """TrustyBot Canary"""
        chn = ctx.message.channel
        fn = "data/trustybot/warrant-canary.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def wtf(self, ctx):
        """lol"""
        chn = ctx.message.channel
        fn = "data/trustybot/wtf.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def vapormaga(self, ctx):
        """lol"""
        chn = ctx.message.channel
        fn = "data/trustybot/vapormaga.jpeg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def thisisfine(self, ctx):
        """lol"""
        chn = ctx.message.channel
        fn = "data/trustybot/thisisfine.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["gg"])
    async def gremblygunk(self, ctx):
        """Gremblygunk"""
        chn = ctx.message.channel
        fn = "data/trustybot/gremblygunk.jpeg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def badge(self, ctx):
        """WIA Badge"""
        chn = ctx.message.channel
        fn = "data/trustybot/Badge.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def wrong(self, ctx):
        """Wrong gif"""
        chn = ctx.message.channel
        fn = "data/trustybot/wrong.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def ohno(self, ctx):
        """Pepe Wall"""
        chn = ctx.message.channel
        fn = "data/trustybot/ohno.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["ay", "duck"])
    async def awyiss(self, ctx):
        """Aw Yiss Duck"""
        chn = ctx.message.channel
        fn = "data/trustybot/awyiss.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["buildthewall", "build"])
    async def wall(self, ctx):
        """Pepe Wall"""
        chn = ctx.message.channel
        fn = "data/trustybot/wall.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["trustyjaid"])
    async def trusty(self, ctx):
        """Trusty Meme"""
        chn = ctx.message.channel
        fn = "data/trustybot/trustymeme.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["takemetobernie"])
    async def bernie(self, ctx):
        """bernie Meme"""
        chn = ctx.message.channel
        fn = "data/trustybot/bernie.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["JAK"])
    async def juliankills(self, ctx):
        """wia Meme"""
        chn = ctx.message.channel
        fn = "data/trustybot/juliankills.jpg"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["whereisassange"])
    async def wia(self, ctx):
        """wia Meme"""
        chn = ctx.message.channel
        fn = "data/trustybot/whereisassange.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["Julian"])
    async def jakek(self, ctx):
        """Julian Assange kek"""
        chn = ctx.message.channel
        fn = "data/trustybot/JAkek.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def getout(self, ctx):
        """get out pepe"""
        chn = ctx.message.channel
        fn = "data/trustybot/getout.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def kek(self, ctx):
        """kek"""
        chn = ctx.message.channel
        fn = "data/trustybot/kek.gif"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["fgm"])
    async def feelsgoodman(self, ctx):
        """Feels good man"""
        chn = ctx.message.channel
        fn = "data/trustybot/feelsgoodman.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["troll"])
    async def trollface(self, ctx):
        """Troll Face"""
        chn = ctx.message.channel
        fn = "data/trustybot/Trollface.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def problem(self, ctx):
        """Problem"""
        chn = ctx.message.channel
        fn = "data/trustybot/problem.png"
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True, aliases=["db"])
    async def dickbutt(self, ctx):
        """DickButt"""
        extension = ["png", "gif"]
        fn = "data/trustybot/dickbutt.{}".format(choice(extension))
        chn = ctx.message.channel
        if ctx.message.server.id != "261565811309674499":
            await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def cookie(self, ctx, user=None):
        """cookie"""
        chn = ctx.message.channel
        fn = "data/trustybot/cookie2.png"
        msg = "Here's a cookie {}! :smile:"
        if user is None:
            await self.bot.send_file(chn, fn)
        else:
            await self.bot.send_file(chn, fn, content=msg.format(user))

    @commands.command(pass_context=True,)
    async def donate(self, ctx):
        """Donate some bitcoin!"""
        gabcoin = "1471VCzShn9kBSrZrSX1Y3KwjrHeEyQtup"
        DONATION = "1DMfQgbyEW1u6M2XbUt5VFP6JARNs8uptQ"
        msg = "Feel free to send bitcoin donations to `{}` :smile:"
        gabimg = "data/trustybot/gabbtc.jpg"
        img = "data/trustybot/btc.png"
        chn = ctx.message.channel
        if ctx.message.server.id == "261565811309674499":
            await self.bot.send_file(chn, gabimg)
            await self.bot.say(msg.format(gabcoin))
        else:
            await self.bot.send_file(chn, img)
            await self.bot.say(msg.format(DONATION))

    @commands.command(pass_context=True, aliases=["tf"])
    async def tinfoil(self, ctx):
        """Liquid Metal Embrittlement"""
        fn = "data/trustybot/tinfoil{}.gif".format(choice(["1", "2"]))
        chn = ctx.message.channel
        await self.bot.send_file(chn, fn)

    @commands.command(pass_context=True)
    async def flipm(self, ctx, *message):
        """Flips a message"""
        msg = ""
        name = ""
        for user in message:
            char = "abcdefghijklmnopqrstuvwxyz - ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz - ∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name += user.translate(table) + " "
        await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])


def setup(bot):
    n = TrustyBot(bot)
    bot.add_cog(n)
