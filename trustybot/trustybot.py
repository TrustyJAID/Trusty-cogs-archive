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
import random
import codecs
import json

DONATION = "1DMfQgbyEW1u6M2XbUt5VFP6JARNs8uptQ"

BTCCONVERT = "https://blockchain.info/tobtc?currency={0}&value={1}"

class TrustyBot:
        def __init__(self, bot):
            self.bot = bot
            self.poll_sessions = []

        @commands.command(hidden=False)
        async def penis(self):
            """What do you thin?!"""
            await self.bot.say(":eggplant: :sweat_drops:")

        @commands.command(hidden=False)
        async def grep(self):
            """Get the fuck out of here with grep!"""
            await self.bot.say("Get the fuck out of here with grep!")

        @commands.command(name="repos", aliases=["github", "WLFF", "wlff"])
        async def repos(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce")

        @commands.command(hidden=False)
        async def python(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/Blockchain-downloader")

        @commands.command(hidden=False)
        async def go(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/local-blockchain-parser")

        @commands.command(hidden=False)
        async def documentation(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/documentation")

        @commands.command(name="pineal", aliases=["pineal gland"])
        async def pinealGland(self, message=None):
            """Links to github"""
            if message == "calcification" or message == "calcified":
                await self.bot.say("https://upload.wikimedia.org/wikipedia/commons/f/f0/Pineal.jpg")
            if message == "healthy":
                await self.bot.say("https://upload.wikimedia.org/wikipedia/commons/d/d6/Pineal_gland_-_very_high_mag.jpg")
            if message == None:
                await self.bot.say("https://en.wikipedia.org/wiki/Pineal_gland")

        @commands.command(pass_context=True, name="openyoureyes", aliases=["OpenYourEyes", "woke", "fluoride"])
        async def OpenYourEyes(self, ctx):
            """Posts tim and eric gif"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/tim-and-eric-mind-blown.gif", filename="tim-and-eric-mind-blown.gif")

        @commands.command(pass_context=True,)
        async def canary(self, ctx):
            """TrustyBot Canary"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/warrant-canary.jpg", filename="warrant-canary.jpg")

        @commands.command(pass_context=True,)
        async def trusty(self, ctx):
            """Trusty Meme"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/trustymeme.png", filename="trustymeme.png")

        @commands.command(pass_context=True)
        async def testserver(self, ctx):
            await self.bot.say(ctx.message.server.id)

        @commands.command(pass_context=True,)
        async def donate(self, ctx):
            """Donate some bitcoin!"""
            gabcoin = "1471VCzShn9kBSrZrSX1Y3KwjrHeEyQtup"
            if ctx.message.server.id == "261565811309674499":
                await self.bot.send_file(ctx.message.channel, "data/trustybot/gabbtc.jpg", filename="gabanonbtc.jpg")
                await self.bot.say("Feel free to send bitcoin donations to `{}` :smile:".format(gabcoin))
            else:
                await self.bot.send_file(ctx.message.channel, "data/trustybot/btc.png", filename="btc.png")
                await self.bot.say("Feel free to send bitcoin donations to `{}` :smile:".format(DONATION))

        @commands.command(hidden=False)
        async def wew(self):
            """wew"""
            wew = codecs.open("data/trustybot/wew.txt", encoding="utf8")
            await self.bot.say(wew.read())
            wew.close()
        
        @commands.command(hidden=False)
        async def test(self):
            """wew"""
            wew = codecs.open("data/trustybot/wew.txt", encoding="utf8")
            await self.bot.say(wew.read())
            wew.close()

        @commands.command(hiddent=False, pass_context=True)
        async def illuminati(self, ctx):
            """o.o"""
            emilum = ["\U0001F4A1", "\U000026A0", "\U0000203C", "\U000026D4"]
            ilum = ":bulb: :warning: :bangbang: :no_entry:"
            msg = await self.bot.say(ilum)
            for i in emilum:
                await self.bot.add_reaction(msg, emoji=i)

        @commands.command(pass_context=True)
        async def kappa(self, ctx):
            """kappa"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/kappa.png", filename="kappa.png")

        @commands.command(pass_context=True)
        async def cheers(self, ctx):
            """cheers!"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/cheers.png", filename="cheers.png")

        @commands.command(hidden=False)
        async def party(self):
            """PARTY"""
            party = codecs.open("data/trustybot/party.txt", encoding="utf8")
            await self.bot.say(party.read())
            party.close()

        @commands.command(hidden=True, pass_context=True)
        async def rekt(self, ctx, endcount=30):
            """REKT"""
            rektemoji = ["\u2611", "\U0001F1F7", "\U0001F1EA", "\U0001F1F0", "\U0001F1F9"]
            rekt = codecs.open("data/trustybot/rekt.txt", encoding="utf8")
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.add_field(name="NOT REKT", value="⬜ Not Rekt", inline=True)
            count = 0
            count2 = 0
            message = ""
            for line in rekt.readlines():
                if count2 == 10:
                    embed.add_field(name="REKT", value=message, inline=True)
                    count2 = 0
                    message = ""

                message += line
                count += 1
                count2 += 1
                if count == endcount:
                    break
            if message != "":
                embed.add_field(name="REKT", value=message, inline=True)
            msg = await self.bot.send_message(ctx.message.channel, embed=embed)
            for emoji in rektemoji:
                await self.bot.add_reaction(msg, emoji=emoji)
            rekt.close()

        @commands.command(hidden=False)
        async def halp(self):
            """How to ask for help!"""
            await self.bot.say("Please type `;help` to be PM'd all my commands! :smile:")

        @commands.command(hidden=False)
        async def goodshit(self):
            """GOODSHIT"""
            goodshit = codecs.open("data/trustybot/goodshit.txt", encoding="utf8")
            await self.bot.say(goodshit.read())
            goodshit.close()

        @commands.command(pass_context=True)
        async def gamesplaying(self, ctx):
            """lists the games TrustyBot can play"""
            gamesplaying = codecs.open("data/trustybot/games.txt", encoding="utf8")
            message = "```\n"
            for game in gamesplaying.read().split("\n"):
                message += "Playing " + game + "\n"
            message += "```"
            await self.bot.send_message(ctx.message.channel, message)

        @commands.command(name="maga", aliases=["MAGA", "nevercomedown"])
        async def maga(self):
            """I don't care if I ever come down!"""
            await self.bot.say("https://www.youtube.com/watch?v=zxXfHxceMg4")

        @commands.command(hidden=False)
        async def converttobtc(self, ammount=1, currency="USD"):
            """converts to BTC from a given currency."""
            try:
                conversion = urllib.request.urlopen(BTCCONVERT.format(currency, ammount))
                for line in conversion:
                    await self.bot.say("{0} {1} is {2} BTC ₿".format(ammount, currency, line.decode('utf8')))
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False)
        async def btc(self, ammount=1.0, currency="USD"):
            """converts from BTC to a given currency."""
            try:
                conversion = urllib.request.urlopen(BTCCONVERT.format(currency, 1))
                for line in conversion:
                    conversion = (1/float(line.decode('utf8')))*float(ammount)
                    await self.bot.say("{0} BTC is {1:.2f} {2}".format(ammount, conversion, currency))
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False)
        async def gold(self, ammount=1, currency="USD"):
            """converts gold in ounces to a given currency."""
            GOLD = "https://www.quandl.com/api/v3/datasets/WGC/GOLD_DAILY_{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(GOLD.format(currency))
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                await self.bot.say("{0} oz of Gold is {1:.2f} {2}".format(ammount, price, currency))
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False)
        async def silver(self, ammount=1, currency="USD"):
            """converts silver in ounces to a given currency."""
            SILVER = "https://www.quandl.com/api/v3/datasets/PERTH/SLVR_USD_D.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(SILVER.format(currency))
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                await self.bot.say("{0} oz of Silver is {1:.2f} {2}".format(ammount, price, currency))
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False)
        async def platinum(self, ammount=1):
            """converts platinum in ounces to a given currency."""
            PLATINUM = "https://www.quandl.com/api/v3/datasets/JOHNMATT/PLAT.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(PLATINUM)
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                await self.bot.say("{0} oz of Platinum is {1:.2f} {2}".format(ammount, price, "USD"))
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")
            """TODO: add feeder cattle, coffee, sugar AND PLATINUM CONVERSION FOR NEONNEXUS"""

        @commands.command(hidden=False)
        async def lenny(self):
            """Lenny"""
            await self.bot.say("( ͡° ͜ʖ ͡°)")

        @commands.command(hidden=False)
        async def kawaii(self):
            """kawaii"""
            await self.bot.say("(◕‿◕✿)")

        @commands.command(hidden=False, name="fbi", aliases=["cia", "nsa", "gchq", "rcmp", "mi5", "mi6", "mossad", "kgb", "kfc"])
        async def FBI(self):
            """Not FBI"""
            await self.bot.say("I am not, nor have I ever been, in contact with the FBI, CIA, NSA, GCHQ, MI5, MI6, MOSSAD, KGB, RCMP, or any other private or government run intelligence agencies! :smile:")

        @commands.command(pass_context=True)
        async def kek(self, ctx):
            """kek"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/kek.gif", filename="kek.gif")

        @commands.command(pass_context=True, name="gabanon", aliases=["g", "gaba"])
        async def gabanon(self, ctx):
            """GabAnon"""
            await self.bot.send_file(ctx.message.channel, "data/trustybot/gabanon.png", filename="gabanon.png")

        @commands.command(hidden=False)
        async def hewillnotdivideus(self):
            """He will not divide us"""
            await self.bot.say("HE WILL NOT DIVIDE US! http://www.hewillnotdivide.us/")

        @commands.command(hidden=False)
        @checks.is_owner()
        async def crash(self):
            """wew"""
            iOSCrash = codecs.open("data/trustybot/ioscrash.txt", encoding="utf8")
            await self.bot.say(iOSCrash.read())
            iOSCrash.read()

        @commands.command(hidden=False)
        async def fuckyou(self):
            """What did you fucking say about me"""
            fuckyou = codecs.open("data/trustybot/fuckyou.txt", encoding="utf8")
            await self.bot.say(fuckyou.read())
            fuckyou.close()

        @commands.command(hidden=False)
        async def dreams(self):
            """don't let your dreams be dreams"""
            Dreams = codecs.open("data/trustybot/dreams.txt", encoding="utf8")
            await self.bot.say(Dreams.read().format("dreams"))
            Dreams.close()

        @commands.command(hidden=False)
        async def memes(self):
            """don't let your memes be dreams"""
            Dreams = codecs.open("data/trustybot/dreams.txt", encoding="utf8")
            await self.bot.say(Dreams.read().format("memes"))
            Dreams.close()

        @commands.command(hidden=False)
        async def awsum(self):
            """awsum"""
            awsum = codecs.open("data/trustybot/awsum.txt", encoding="utf8")
            await self.bot.say(awsum.read())
            awsum.close()

        @commands.command(hidden=False)
        async def wut(self):
            """wut"""
            wut = codecs.open("data/trustybot/wut.txt", encoding="utf8")
            await self.bot.say(wut.read())
            wut.close()

        @commands.command(hidden=False, pass_context=True)
        async def shrug(self, ctx):
            """shrug"""
            await self.bot.say("¯\_(ツ)_/¯")

        @commands.command(pass_context=True, name="soon", aliases=["s"])
        async def soon(self, ctx):
            """Soon™"""
            await self.bot.say("Soon™")

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
