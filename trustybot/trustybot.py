import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from cogs.utils import checks
from random import choice
import random
import urllib.request
import hashlib
import aiohttp
import asyncio


class TrustyBot:
    def __init__(self, bot):
        self.bot = bot
        self.text = dataIO.load_json("data/trustybot/messages.json")
        self.links = dataIO.load_json("data/trustybot/links.json")
        self.faces = dataIO.load_json("data/trustybot/CIAJapaneseStyleFaces.json")
        self.images = dataIO.load_json("data/trustybot/images.json")

    def first_word(self, msg):
        return msg.split(" ")[0]

    def get_prefix(self, server, msg):
        prefixes = self.bot.settings.get_prefixes(server)
        for p in prefixes:
            if msg.startswith(p):
                return p
        return None

    def part_of_existing_command(self, alias, server):
        '''Command or alias'''
        for command in self.bot.commands:
            if alias.lower() == command.lower():
                return True
        return False

    async def on_message(self, message):
        if len(message.content) < 2 or message.channel.is_private:
            return

        msg = message.content
        server = message.server
        channel = message.channel
        prefix = self.get_prefix(server, msg)

        if message.attachments != [] and ";addimage" in msg.split(" ")[0]:
            filename = message.attachments[0]["filename"]
            directory = "data/trustybot/img/" + filename
            try:
                command = msg.split(" ")[1]
            except IndexError:
                command = filename.split(".")[0]

            if command in self.images or self.part_of_existing_command(command, server):
                await self.bot.say("{} is already in the list, try another!".format(command))
                return

            if directory not in self.images.values():
                self.images[command] = directory
                dataIO.save_json("data/trustybot/images.json", self.images)
                with aiohttp.ClientSession() as session:
                    async with session.get(message.attachments[0]["url"]) as resp:
                        test = await resp.read()
                        with open(self.images[command], "wb") as f:
                            f.write(test)
                await self.bot.send_message(channel, "{} has been added to my files!".format(command))

        if not prefix:
            return

        alias = self.first_word(msg[len(prefix):]).lower()
        if alias in self.images:
            image = self.images[alias]
            await self.bot.send_file(channel, image)

    @commands.command(pass_context=True, aliases=["db"])
    async def dickbutt(self, ctx):
        """DickButt"""
        ext = ["png", "gif"]
        if ctx.message.server.id != "261565811309674499":
            await self.bot.upload(self.images["dickbutt"]
                                  .format(choice(ext)))

    @commands.command(pass_context=True)
    async def cookie(self, ctx, user=None):
        """cookie"""
        msg = "Here's a cookie {}! :smile:"
        if user is None:
            await self.bot.upload(self.images["cookie"])
        else:
            await self.bot.upload(self.images["cookie"],
                                  content=msg.format(user))

    @commands.command(pass_context=True, aliases=["tf"])
    async def tinfoil(self, ctx):
        """Liquid Metal Embrittlement"""
        await self.bot.upload(self.images["tinfoil"]
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
            await self.bot.upload(gabimg)
            await self.bot.say(msg.format(gabcoin))
        else:
            await self.bot.upload(img)
            await self.bot.say(msg.format(DONATION))

    # Text Commands #
    @commands.command(hidden=False)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def grep(self):
        """Get the fuck out of here with grep!"""
        await self.bot.say("Get the fuck out of here with grep!")

    @commands.command(hidden=False)
    async def passphrase(self):
        """Wikileaks Vault7 Part 1 passphrase"""
        await self.bot.say("`SplinterItIntoAThousandPiecesAndScatterItIntoTheWinds`")

    @commands.command(hidden=False)
    async def torrent(self):
        """Wikileaks Vault7 Part 1 torrent file"""
        await self.bot.say("https://t.co/gpBxJAoYD5")

    @commands.command(hidden=False)
    async def vault7(self):
        """Wikileaks Vault7"""
        await self.bot.say("https://wikileaks.org/ciav7p1/")

    @commands.command()
    async def github(self):
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

    @commands.command(hidden=True, name="kara", aliases=["nevercomedown2"])
    async def kara(self):
        """I don't care if I ever come down!"""
        await self.bot.say(self.links["kara"])

    @commands.command(hidden=True, aliases=["elder", "phoenix"])
    async def elderphoenix(self):
        """lol"""
        await self.bot.say(choice(self.links["elder"]))

    @commands.command(hidden=True, aliases=["directthecheckerd"])
    async def elmyr(self):
        """lol"""
        await self.bot.say(choice(self.links["elmyr"]))

    @commands.command(name="straya", aliases=["ec", "embassycat", "thorium", "sympoz"])
    async def straya(self):
        """Straya"""
        await self.bot.say(choice(self.links["straya"]))

    @commands.command(hidden=True, name="kingdonald", aliases=["KD", "kd"])
    async def kingdonald(self):
        """KingDonald"""
        await self.bot.say(choice(self.links["KingDonald"]))

    @commands.command(hidden=True, name="wsa", aliases=["WSA"])
    async def wsa(self):
        """lol"""
        await self.bot.say(self.links["wsa"])

    @commands.command(hidden=True, name="neon", aliases=["NEON"])
    async def neon(self):
        """lol"""
        await self.bot.say(self.links["neon"])

    @commands.command(name="death", aliases=["DEATH"])
    async def death(self):
        """lol"""
        await self.bot.say(self.links["death"])

    @commands.command(hidden=True, name="ventucky", aliases=["ven"])
    async def ventucky(self):
        """lol"""
        await self.bot.say(choice(self.links["ventucky"]))

    @commands.command(hidden=False)
    async def lenny(self):
        """Lenny"""
        await self.bot.say(self.text["lenny"])

    @commands.command(hidden=True, pass_context=True, aliases=["meme_queen"])
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
    async def party(self):
        """Party"""
        await self.bot.say(self.text["party"])

    @commands.command(hidden=False)
    async def takeaction(self):
        """Take Action"""
        await self.bot.say(self.text["takeaction"])

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

    @commands.command(pass_context=True, aliases=["japaneseface"])
    async def face(self, ctx, number=None):
        """Japanese Faces at random courtesy of the CIA"""
        if number is None:
            await self.bot.say(choice(self.faces))
            return
        if "<@" in str(number):
            if "245862769054711809" in number:
                await self.bot.say(self.faces[328])
                return
            else:
                random.seed(number.strip("<@!>"))
                userface = self.faces[random.randint(0, len(self.faces))]
                await self.bot.say(userface)
                return
        if number.isdigit():
            if int(number) <= len(self.faces):
                await self.bot.say(self.faces[int(number)-1])
                return
            else:
                await self.bot.say("That number is too large, pick less than {}!"
                                   .format(len(self.faces)))
                return
        if not number.isdigit() and "<@!" not in number:
            await self.bot.say(self.faces[len(number)])


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
