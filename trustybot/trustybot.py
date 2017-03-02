import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO
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
            self.STARTTIME = time.time()
            self.ENDTIME = {"wew": 0.0, "rekt": 0.0}
            self.COOLDOWNTIMER = 60
            self.LASTBTC = 1000.00

        @commands.command(hidden=False)
        async def grep(self):
            """Get the fuck out of here with grep!"""
            await self.bot.say("Get the fuck out of here with grep!")

        @commands.command(name="repos", aliases=["github"])
        async def repos(self):
            """Links to github"""
            await self.bot.say("https://github.com/TrustyJAID/TrustyBot-cogs")

        @commands.command(name="wlff", aliases=["WLFF"])
        async def wlff(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce")

        @commands.command(name="pol", aliases=["POL", "proofoflife"])
        async def pol(self):
            """Links to Proof of life timeline"""
            await self.bot.say("https://www.reddit.com/r/WhereIsAssange/comments/5qywrd/proof_of_life_location_timeline_of_julian_assange/")

        @commands.command(name="disinfo", aliases=["DISINFO"])
        async def disinfo(self):
            """Links to disinfo thread"""
            await self.bot.say("https://www.reddit.com/r/WhereIsAssange/comments/5q78r8/disinfo_campaign_mega_thread/")

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

        @commands.command(hidden=False)
        async def btcchina(self):
            """Bitcoin China Comic"""
            await self.bot.say("http://imgur.com/a/KDwtE")

        @commands.command(hidden=False)
        async def smarm(self):
            """Gawker Smarm Article"""
            await self.bot.say("http://gawker.com/on-smarm-1476594977")

        @commands.command(name="pineal", aliases=["pineal gland"])
        async def pinealGland(self, message=None):
            """Links to pineal gland"""
            if message == "calcification" or message == "calcified":
                await self.bot.say("https://upload.wikimedia.org/wikipedia/commons/f/f0/Pineal.jpg")
            if message == "healthy":
                await self.bot.say("https://upload.wikimedia.org/wikipedia/commons/d/d6/Pineal_gland_-_very_high_mag.jpg")
            if message == None:
                await self.bot.say("https://en.wikipedia.org/wiki/Pineal_gland")

        @commands.command(pass_context=True, aliases=[ "fluoride", "OpenYourEyes", "openyoureyes"])
        async def woke(self, ctx):
            """Posts tim and eric gif"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/tim-and-eric-mind-blown.gif",
                                     filename="tim-and-eric-mind-blown.gif")

        @commands.command(pass_context=True)
        async def canary(self, ctx):
            """TrustyBot Canary"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/warrant-canary.jpg",
                                     filename="warrant-canary.jpg")
        
        @commands.command(pass_context=True, aliases=["gg"])
        async def gremblygunk(self, ctx):
            """Gremblygunk"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/gremblygunk.jpeg",
                                     filename="gremblygunk.jpeg")

        @commands.command(pass_context=True)
        async def badge(self, ctx):
            """WIA Badge"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/Badge.gif",
                                     filename="Badge.gif")

        @commands.command(pass_context=True)
        async def wrong(self, ctx):
            """Wrong gif"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/wrong.gif",
                                     filename="wrong.gif")

        @commands.command(pass_context=True)
        async def ohno(self, ctx):
            """Pepe Wall"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/ohno.jpg",
                                     filename="ohno.jpg")

        @commands.command(pass_context=True, aliases=["ay", "duck"])
        async def awyiss(self, ctx):
            """Aw Yiss Duck"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/awyiss.jpg",
                                     filename="awyiss.jpg")

        @commands.command(pass_context=True, aliases=["buildthewall", "build"])
        async def wall(self, ctx):
            """Pepe Wall"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/wall.png",
                                     filename="wall.png")

        @commands.command(pass_context=True, aliases=["trustyjaid"])
        async def trusty(self, ctx):
            """Trusty Meme"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/trustymeme.png",
                                     filename="trustymeme.png")

        @commands.command(pass_context=True, aliases=["takemetobernie"])
        async def bernie(self, ctx):
            """bernie Meme"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/bernie.jpg",
                                     filename="bernie.jpg")

        @commands.command(pass_context=True, aliases=["JAK"])
        async def juliankills(self, ctx):
            """wia Meme"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/juliankills.jpg",
                                     filename="juliankills.jpg")

        @commands.command(pass_context=True, aliases=["whereisassange"])
        async def wia(self, ctx):
            """wia Meme"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/whereisassange.png",
                                     filename="whereisassange.png")

        @commands.command(pass_context=True, aliases=["rp"])
        async def redpill(self, ctx):
            """Red Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/redpill.png",
                                     filename="redpill.png")

        @commands.command(pass_context=True, aliases=["bp"])
        async def bluepill(self, ctx):
            """Blue Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/bluepill.png",
                                     filename="bluepill.png")

        @commands.command(pass_context=True, aliases=["blp"])
        async def blackpill(self, ctx):
            """Black Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/blackpill.png",
                                     filename="blackpill.png")

        @commands.command(pass_context=True, aliases=["pp"])
        async def purplepill(self, ctx):
            """Purple Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/purplepill.png",
                                     filename="purplepill.png")

        @commands.command(pass_context=True, aliases=["yp"])
        async def yellowpill(self, ctx):
            """Yellow Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/yellowpill.png",
                                     filename="yellowpill.png")

        @commands.command(pass_context=True, aliases=["gp"])
        async def greenpill(self, ctx):
            """Green Pill"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/greenpill.png",
                                     filename="greenpill.png")

        @commands.command(pass_context=True, aliases=["Julian"])
        async def jakek(self, ctx):
            """Julian Assange kek"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/JAkek.gif",
                                     filename="trustymeme.gif")

        @commands.command(pass_context=True)
        async def getout(self, ctx):
            """get out pepe"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/getout.gif",
                                     filename="getout.gif")

        @commands.command(pass_context=True, aliases=["db"])
        async def dickbutt(self, ctx):
            """Trusty Meme"""
            extension = ["png", "gif"]
            if ctx.message.server.id != "261565811309674499":
                await self.bot.send_file(ctx.message.channel,
                                         "data/trustybot/dickbutt.{}".format(choice(extension),
                                         filename="dickbutt.{}".format(choice(extension))))

        @commands.command(pass_context=True, aliases=["fgm"])
        async def feelsgoodman(self, ctx):
            """Feels good man"""
            await self.bot.send_file(ctx.message.channel,
                                        "data/trustybot/feelsgoodman.png",
                                        filename="feelsgoodman.png")

        @commands.command(pass_context=True, aliases=["troll"])
        async def trollface(self, ctx):
            """Troll Face"""
            await self.bot.send_file(ctx.message.channel,
                                        "data/trustybot/Trollface.png",
                                        filename="Trollface.png")

        @commands.command(pass_context=True)
        async def problem(self, ctx):
            """Problem"""
            await self.bot.send_file(ctx.message.channel,
                                        "data/trustybot/problem.png",
                                        filename="problem.png")

        @commands.command(pass_context=True,)
        async def donate(self, ctx):
            """Donate some bitcoin!"""
            gabcoin = "1471VCzShn9kBSrZrSX1Y3KwjrHeEyQtup"
            if ctx.message.server.id == "261565811309674499":
                await self.bot.send_file(ctx.message.channel,
                                         "data/trustybot/gabbtc.jpg",
                                         filename="gabanonbtc.jpg")
                await self.bot.say("Feel free to send bitcoin donations to `{}` :smile:".format(gabcoin))
            else:
                await self.bot.send_file(ctx.message.channel, "data/trustybot/btc.png", filename="btc.png")
                await self.bot.say("Feel free to send bitcoin donations to `{}` :smile:".format(DONATION))

        def cooldown(self, function):
            self.STARTTIME = time.time()
            if self.STARTTIME >= self.ENDTIME[function]:
                self.ENDTIME[function] = self.STARTTIME+ self.COOLDOWNTIMER
                return True
            else:
                return False

        @commands.command(hidden=False, pass_context=True)
        async def wew(self, ctx):
            """wew"""
            self.STARTTIME = time.time()
            if self.cooldown("wew"):
                wew = codecs.open("data/trustybot/wew.txt", encoding="utf8")
                await self.bot.say(wew.read())
                wew.close()
            else:
                await self.bot.say("Please wait {:.2f}s to reuse this command!".format((self.ENDTIME["wew"]-self.STARTTIME)))

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
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/kappa.png",
                                     filename="kappa.png")

        @commands.command(pass_context=True)
        async def cheers(self, ctx):
            """cheers!"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/cheers.png",
                                     filename="cheers.png")

        @commands.command(pass_context=True, aliases=["btcup"])
        async def tothemoon(self, ctx):
            """To the moon!!"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/roller-coaster-guy.gif",
                                     filename="roller-coaster-guy.gif")

        @commands.command(pass_context=True)
        async def btcdown(self, ctx):
            """NOT To the moon!!"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/roller-coaster-guy-down.gif",
                                     filename="roller-coaster-guy-down.gif")

        @commands.command(pass_context=True, aliases=["hacker"])
        async def hackerman(self, ctx):
            """Hackerman"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/hackerman.png",
                                     filename="hackerman.png")

        @commands.command(pass_context=True)
        async def kiddo(self, ctx):
            """kiddo"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/kiddo.png",
                                     filename="kiddo.png")
        
        @commands.command(pass_context=True)
        async def nsa(self, ctx):
            """kiddo"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/nsa.png",
                                     filename="nsa.png")
        @commands.command(pass_context=True)
        async def wikileaks(self, ctx):
            """wikileaks"""
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/wikileaks.png",
                                     filename="wikileaks.png")

        @commands.command(pass_context=True)
        async def cookie(self, ctx, user=None):
            """cookie"""
            if user == None:
                await self.bot.send_file(ctx.message.channel,
                                         "data/trustybot/cookie2.png",
                                         filename="cookie2.png")
            else:
                await self.bot.send_file(ctx.message.channel,
                                         "data/trustybot/cookie2.png",
                                         filename="cookie2.png",
                                         content="Here's a cookie {}! :smile:".format(user))

        @commands.command(pass_context=True, aliases=["tf"])
        async def tinfoil(self, ctx):
            """Liquid Metal Embrittlement"""
            x = choice(["1", "2"])
            await self.bot.send_file(ctx.message.channel,
                                     "data/trustybot/tinfoil{}.gif".format(x),
                                     filename="tinfoil.gif")

        @commands.command(hidden=False)
        async def party(self):
            """PARTY"""
            party = codecs.open("data/trustybot/party.txt", encoding="utf8")
            await self.bot.say(party.read())
            party.close()

        @commands.command(hidden=True, pass_context=True)
        async def rekt(self, ctx, endcount=10):
            """REKT"""
            self.STARTTIME = time.time()
            if self.cooldown("rekt"):
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
                embed.set_author(name="Are you REKT?")
                msg = await self.bot.send_message(ctx.message.channel, embed=embed)
                for emoji in rektemoji:
                    await self.bot.add_reaction(msg, emoji=emoji)
                rekt.close()
            else:
                await self.bot.say("Please wait {:.2f}s to do more rektoning!".format((self.ENDTIME["rekt"]-self.STARTTIME)))

        @commands.command(hidden=False)
        async def halp(self, user=None):
            """How to ask for help!"""
            if user == None:
                await self.bot.say("Please type `;help` to be PM'd all my commands! :smile:")
            else:
                await self.bot.say("{} please type `;help` to be PM'd all my commands! :smile:".format(user))

        @commands.command(hidden=False)
        async def goodshit(self):
            """GOODSHIT"""
            goodshit = codecs.open("data/trustybot/goodshit.txt", encoding="utf8")
            await self.bot.say(goodshit.read())
            goodshit.close()

        @commands.command(name="maga", aliases=["MAGA", "nevercomedown"])
        async def maga(self):
            """I don't care if I ever come down!"""
            await self.bot.say("https://www.youtube.com/watch?v=zxXfHxceMg4")

        @commands.command(name="kara", aliases=["nevercomedown2"])
        async def kara(self):
            """I don't care if I ever come down!"""
            await self.bot.say("https://youtu.be/yZNtYmdZ-4c")

        @commands.command(aliases=["elder", "phoenix"])
        async def elderphoenix(self):
            """lol"""
            links = ["https://youtu.be/0C_oNMH0GTk", "https://youtu.be/c37xCrEMKpA", "https://youtu.be/EoyFFxCtfXo"]
            await self.bot.say(choice(links))

        @commands.command(aliases=["directthecheckerd"])
        async def elmyr(self):
            """lol"""
            links = ["https://www.youtube.com/watch?v=gJ1Mz7kGVf0", "https://youtu.be/PKeBHzFsoEU", "https://youtu.be/0C_oNMH0GTk"]
            await self.bot.say(choice(links))

        @commands.command(name="embassycat", aliases=["ec", "thorium", "sympoz"])
        async def embassycat(self):
            """I don't care if I ever come down!"""
            links = ["https://youtu.be/rMdbVHPmCW0", "https://youtu.be/uRz8FWPUmpI"]
            await self.bot.say(choice(links))

        @commands.command(name="kingdonald", aliases=["KD", "kd"])
        async def kingdonald(self):
            """KingDonald"""
            links = ["http://i.imgur.com/qoJ4C.jpg", "https://youtu.be/cSSwXvsEX_c"]
            await self.bot.say(choice(links))

        @commands.command(name="wsa", aliases=["WSA"])
        async def wsa(self):
            """lol"""
            await self.bot.say("https://youtu.be/SxBKD5wpFFg")

        @commands.command(name="neon", aliases=["NEON"])
        async def neon(self):
            """lol"""
            await self.bot.say("https://youtu.be/XutaTTNihe0")
        
        @commands.command(name="death", aliases=["DEATH"])
        async def death(self):
            """lol"""
            await self.bot.say("https://www.youtube.com/watch?v=q6-ZGAGcJrk")

        @commands.command(name="ventucky", aliases=["ven"])
        async def ventucky(self):
            """lol"""
            links = ["https://youtu.be/ePsOP7N2Vfk", "https://youtu.be/ltvjljbrnIs"]
            await self.bot.say(choice(links))

        @commands.command(hidden=False)
        async def converttobtc(self, ammount=1.0, currency="USD"):
            """converts to BTC from a given currency."""
            try:
                conversion = urllib.request.urlopen(BTCCONVERT.format(currency.upper(), ammount))
                for line in conversion:
                    msg = "{0} {1} is {2} BTC ₿".format(ammount, currency.upper(), line.decode('utf8'))
                    embed = discord.Embed(descirption="BTC", colour=discord.Colour.gold())
                    embed.add_field(name="Bitcoin", value=msg)
                    embed.set_thumbnail(url="https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png")
                    await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False, aliases=["bitcoin", "BTC"])
        async def btc(self, ammount=1.0, currency="USD"):
            """converts from BTC to a given currency."""
            try:
                conversion = urllib.request.urlopen(BTCCONVERT.format(currency.upper(), 1))
                for line in conversion:
                    conversion = (1/float(line.decode('utf8')))*float(ammount)
                    msg = "{0} BTC is {1:.2f} {2}".format(ammount, conversion, currency.upper())
                    embed = discord.Embed(descirption="BTC", colour=discord.Colour.gold())
                    embed.add_field(name="Bitcoin", value=msg)
                    embed.set_thumbnail(url="https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png")
                    await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False, aliases=["au", "AU", "Au", "GOLD"])
        async def gold(self, ammount=1, currency="USD"):
            """converts gold in ounces to a given currency."""
            GOLD = "https://www.quandl.com/api/v3/datasets/WGC/GOLD_DAILY_{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(GOLD.format(currency.upper()))
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                msg = "{0} oz of Gold is {1:.2f} {2}".format(ammount, price, currency.upper())
                embed = discord.Embed(descirption="Gold", colour=discord.Colour.gold())
                embed.add_field(name="Gold", value=msg)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d7/Gold-crystals.jpg")
                await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False, aliases=["ag", "AG", "Ag", "SILVER"])
        async def silver(self, ammount=1, currency="USD"):
            """converts silver in ounces to a given currency."""
            SILVER = "https://www.quandl.com/api/v3/datasets/LBMA/SILVER.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(SILVER)
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                if currency != "USD":
                    price = price * self.conversionrate("USD", currency.upper())
                msg = "{0} oz of Silver is {1:.2f} {2}".format(ammount, price, currency.upper())
                embed = discord.Embed(descirption="Silver", colour=discord.Colour.lighter_grey())
                embed.add_field(name="Silver", value=msg)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/5/55/Silver_crystal.jpg")
                await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False, aliases=["pt", "PT", "Pt", "PLATINUM"])
        async def platinum(self, ammount=1, currency="USD"):
            """converts platinum in ounces to a given currency."""
            PLATINUM = "https://www.quandl.com/api/v3/datasets/JOHNMATT/PLAT.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(PLATINUM)
                conversion = json.loads(conversion.read())
                price = (conversion["dataset"]["data"][0][1]) * ammount
                if currency != "USD":
                    price = self.conversionrate("USD", currency.upper()) * price
                msg = "{0} oz of Platinum is {1:.2f} {2}".format(ammount, price, currency.upper())
                embed = discord.Embed(descirption="Platinum", colour=discord.Colour.dark_grey())
                embed.add_field(name="Platinum", value=msg)
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/6/68/Platinum_crystals.jpg")
                await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

        @commands.command(hidden=False, aliases=["ticker"])
        async def stock(self, ticker, currency="USD"):
            """Gets current ticker symbol price."""
            stock = "https://www.quandl.com/api/v3/datasets/WIKI/{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
            try:
                conversion = urllib.request.urlopen(stock.format(ticker.upper()))
                conversion = json.loads(conversion.read())
                convertrate = 1
                if currency != "USD":
                    convertrate = self.conversionrate("USD", currency.upper())
                price = (conversion["dataset"]["data"][0][1]) * convertrate
                msg = "{0} is {1:.2f} {2}".format(ticker.upper(), price, currency.upper())
                embed = discord.Embed(descirption="Stock Price", colour=discord.Colour.lighter_grey())
                embed.add_field(name=ticker.upper(), value=msg)
                # embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/5/55/Silver_crystal.jpg")
                await self.bot.say(embed=embed)
            except:
                await self.bot.say("Pick a correct ticker symbol!")

        @commands.command(hidden=False)
        async def convert(self, ammount=1, currency1="USD", currency2="GBP"):
            try:
                conversion = self.conversionrate(currency1.upper(), currency2.upper()) * ammount
                await self.bot.say("{0} {1} is {2:.2f} {3}".format(ammount, currency1, conversion, currency2))
            except:
                await self.bot.say("Please enter a proper integer and standard currency! :smile:")

        def conversionrate(self, currency1, currency2):
            """converts platinum in ounces to a given currency."""
            CONVERSIONRATES = "http://api.fixer.io/latest?base={}".format(currency1.upper())
            try:
                conversion = urllib.request.urlopen(CONVERSIONRATES)
                conversion = json.loads(conversion.read())
                conversion = (conversion["rates"][currency2.upper()])
                return conversion
            except:
                return "That currency is not valid"
            """TODO: add feeder cattle, coffee, and sugar"""

        @commands.command(hidden=False)
        async def lenny(self):
            """Lenny"""
            await self.bot.say("( ͡° ͜ʖ ͡°)")

        @commands.command(hidden=False, pass_context=True, aliases=["meme_queen"])
        async def mq(self, ctx):
            """Lol"""
            await self.bot.say("You're cute <@245862769054711809> :smile:")

        @commands.command(hidden=False, pass_context=True)
        async def loveofmylife(self):
            """Lol"""
            userlist = list(discord.Server.members)
            userlist = choice(userlist)
            await self.bot.say("You're cute {} :smile:".format(userlist))

        @commands.command(hidden=True, pass_context=True)
        async def lovemylife(self, ctx):
            """Lol"""
            user = ctx.message.author.mention
            await self.bot.say("I'm glad you love your life {} :smile: you should you're awesome!".format(user))

        @commands.command(hidden=False)
        async def kawaii(self):
            """kawaii"""
            await self.bot.say("(◕‿◕✿)")

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

        @commands.command(pass_context=True, aliases=["areyoukiddingme"])
        async def aykm(self, ctx):
            """ಠ_ಠ"""
            await self.bot.say("ಠ_ಠ")

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
