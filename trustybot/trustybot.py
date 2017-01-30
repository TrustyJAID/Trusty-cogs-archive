import discord
from discord.ext import commands
from .utils.chat_formatting import *
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import hashlib
import datetime
import time
import aiohttp
import asyncio

WEW = """⢀⢀⢀⢀⢀⣤⠖⠚⠉⠉⠳⣦⢀⢀⢀⢀⢀⢀⢀⢀⣼⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣀⣀⡀⢀⢀⢀⣀⣀ ⢀⢀⢀⡴⢋⣀⡀⢀⢀⢀⢀⢻⣷⢀⢀⢀⢀⢀⢀⣼⠇⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣠⣾⠿⠛⠉⠁⢀⣴⡟⠁⢀⡇⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣠⣤ ⢀⢀⠎⣰⣿⠿⣿⡄⢀⢀⢀⢸⣿⡆⢀⢀⢀⢀⣾⡿⢀⢀⢀⢀⡀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣰⡟⠁⢀⢀⢀⢀⣾⡟⢀⢀⢀⡟⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢠⣿⡿ ⢀⠏⢰⣿⡟⢀⣿⡇⢀⢀⢀⣿⣿⡇⢀⢀⢀⢮⣿⠇⢀⢀⢠⠞⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢰⠏⢀⢀⢀⢀⢀⣿⣿⠁⢀⢀⢸⠇⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣼⣿⠃ ⡜⢀⣾⡿⠃⢠⣿⠁⢀⢀⢸⣿⣿⠁⢀⢀⢊⣿⡟⢀⢀⡰⠃⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⡿⢀⢀⢀⢀⢀⣾⣿⠇⢀⢀⢠⠏⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢠⣿⡟ ⡇⢀⠋⢀⢀⣾⡏⢀⢀⢀⣿⣿⡏⢀⠠⠃⣾⣿⠇⢀⡴⠁⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⡇⢀⢀⢀⢀⣼⣿⡟⢀⢀⣰⠋⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣼⣿⠁ ⠹⣄⣀⣤⣿⠟⢀⢀⢀⣾⣿⡟⢀⡐⠁⣼⣿⡟⢀⡰⣡⣶⡶⣆⢀⢀⣀⣀⢀⢀⣀⣀⢀⢀⣀⣀⢀⢀⢀⢀⢀⢀⢀⢷⢀⢀⢀⢸⣿⣿⠃⣠⠞⢁⣴⣶⣠⣶⡆⢀⢀⢀⣠⣶⣶⣰⣿⡏ ⢀⠈⠉⠉⢀⢀⢀⢀⣼⣿⡟⠁⠄⢀⢰⣿⣿⠃⣰⣿⣿⠏⢀⣿⢀⣸⣿⠏⢀⢸⣿⠃⢀⣼⣿⠇⢀⢀⢀⢀⢀⢀⢀⢀⠑⢀⢠⣿⣿⣿⠋⠁⣰⣿⡟⠁⣿⣿⢀⢀⢀⣴⣿⠟⢀⣿⡿ ⢀⢀⢀⢀⢀⢀⢀⣼⣿⠟⡀⢀⢀⢀⣿⣿⡟⢠⣿⣿⡟⢀⣰⠇⢀⣿⡿⢀⢀⣿⡏⢀⢰⣿⡏⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢰⣿⣿⠃⢀⣼⣿⡟⢀⣸⣿⠃⢀⢀⣼⣿⡏⢀⣼⣿⠃ ⢀⢀⢀⢀⢀⢀⣼⡿⠋⢀⢀⢀⢀⢸⣿⣿⠃⣿⣿⣿⠁⣰⠏⢀⣼⣿⠃⢀⣾⡿⢀⢠⣿⡟⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣿⣿⡏⢀⣰⣿⣿⠁⢠⣿⡏⢀⢀⣸⣿⡿⢀⢰⣿⠇ ⢀⢀⢀⢀⢀⣾⣟⠕⠁⢀⢀⢀⢀⢸⣿⣿⣼⣿⣿⡿⠊⠁⣰⢣⣿⡟⢀⣰⣿⠃⢀⣾⣿⠁⡼⢀⢀⢀⣰⡾⠿⠿⣿⣶⣦⣾⣿⡟⢀⢀⣿⣿⡇⢀⣾⡿⢀⡞⢰⣿⣿⠇⢠⣿⡟⢠⡏ ⢀⢀⢀⢠⣾⡿⠁⢀⢀⢀⢀⢀⢀⢸⣿⣿⠃⣿⣿⢀⢀⡴⠃⣾⣿⣧⣰⣿⣿⣄⣾⣿⣧⡼⠁⢀⢀⢀⣿⢀⢀⢀⢀⢹⣿⣿⣟⢀⢀⢸⣿⣿⣧⣾⣿⣷⡾⠁⣼⣿⣿⣤⣿⣿⣷⡟ ⢀⢀⢀⠟⠉⢀⢀⢀⢀⢀⢀⢀⢀⢀⠻⠋⢀⢿⣿⣶⠟⠁⢀⠻⣿⡿⠛⣿⣿⠏⢿⣿⠟⠁⢀⢀⢀⢀⠘⠦⣤⣤⡶⠟⢻⣿⣿⢀⢀⠘⣿⣿⠋⢿⣿⠟⢀⢀⠸⣿⡿⠋⣿⣿⠏ ⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢿⣿⣇⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⣀⣠⣤⣤⣤⣤⣀⡀ ⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⠈⢿⣿⣆⢀⢀⢀⢀⢀⢀⣠⡤⠶⠛⠛⠛⠻⢿⣿⣿⣿⣿⣶⣄ ⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⢀⠙⠿⣷⣤⣤⠶⠞⠋⠁⢀⢀⢀⢀⢀⢀⠈⠻"""

KEK = """__████████__██████
__█░░░░░░░░████░░░░░░█
__█░░░░░░░░░░░█░░░░░░░░░█
__█░░░░░░░███░░░█░░░░░░░░░█
__█░░░░███░░░███░█░░░████░█
__█░░░██░░░░░░░░███░██░░░░██
__█░░░░░░░░░░░░░░░░░█░░░░░░░░███
__█░░░░░░░░░░░░░██████░░░░░████░░█
__█░░░░░░░░░█████░░░████░░██░░██░░█
██░░░░░░░███░░░░░░░░░░█░░░░░░░░███
█░░░░░░░░░░░░░░█████████░░█████████
█░░░░░░░░░░█████████__█████████__█
█░░░░░░░░░░█__█████___████__█
█░░░░░░░░░░░░█__████████__██_██████
░░░░░░░░░░░░░█████████░░░████████░░░█
░░░░░░░░░░░░░░░░█░░░░░█░░░░░░░░░░░░█
░░░░░░░░░░░░░░░░░░░░██░░░░█░░░░░░██
░░░░░░░░░░░░░░░░░░██░░░░░░░███████
░░░░░░░░░░░░░░░░██░░░░░░░░░░█░░░░░█
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
░░░░░░░░░░░█████████░░░░░░░░░░░░░░██
░░░░░░░░░░█▒▒▒▒▒▒▒▒███████████████▒▒█
░░░░░░░░░█▒▒███████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
░░░░░░░░░█▒▒▒▒▒▒▒▒▒█████████████████
░░░░░░░░░░████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
░░░░░░░░░░░░░░░░░░██████████████████
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
██░░░░░░░░░░░░░░░░░░░░░░░░░░░██
▓██░░░░░░░░░░░░░░░░░░░░░░░░██
▓▓▓███░░░░░░░░░░░░░░░░░░░░█
▓▓▓▓▓▓███░░░░░░░░░░░░░░░██
▓▓▓▓▓▓▓▓▓███████████████▓▓█
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█
"""

WhatDidYouFuckingSayAboutMe = """What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals, and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You’re fucking dead, kiddo."""

Dreams = """DO IT, just DO IT! Don’t let your {} be dreams. Yesterday, you said tomorrow. So just. DO IT! Make. your dreams. COME TRUE! Just… do it! Some people dream of success, while you’re gonna wake up and work HARD at it! NOTHING IS IMPOSSIBLE!You should get to the point where anyone else would quit, and you’re not gonna stop there. NO! What are you waiting for? … DO IT! Just… DO IT! Yes you can! Just do it! If you’re tired of starting over, stop. giving. up."""

iOSCrash = """-______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________-"""


class TrustyBot:
        def __init__(self, bot):
            self.bot = bot
            self.poll_sessions = []

        @commands.command(hidden=True)
        async def penis(self):
            """Penis lol"""
            await self.bot.say(":eggplant: :sweat_drops:")

        @commands.command(hidden=True)
        async def grep(self):
            """Grep."""
            await self.bot.say("Grep doesn't make sense inside of Python!")

        @commands.command(name="repos", aliases=["github", "WLFF", "wlff"])
        async def repo(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce")

        @commands.command(hidden=True)
        async def python(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/Blockchain-downloader")

        @commands.command(hidden=True)
        async def go(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/local-blockchain-parser")

        @commands.command(hidden=True)
        async def documentation(self):
            """Links to github"""
            await self.bot.say("https://github.com/WikiLeaksFreedomForce/documentation")

        @commands.command(name="pineal", aliases=["pineal gland"])
        async def pinealGland(self):
            """Links to github"""
            await self.bot.say("http://upliftconnect.com/wp-content/uploads/2016/04/PinealGland.jpg")

        @commands.command(name="openyoureyes", aliases=["OpenYourEyes", "woke", "fluoride"])
        async def OpenYourEyes(self):
            """Links to github"""
            await self.bot.say("http://www.reactiongifs.com/wp-content/uploads/2013/10/tim-and-eric-mind-blown.gif")

        @commands.command(hidden=True)
        async def wew(self):
            """wew"""
            await self.bot.say(WEW)

        @commands.command(hidden=True)
        async def kek(self):
            """kek"""
            await self.bot.say(KEK)

        @commands.command(hidden=True)
        async def crash(self):
            """wew"""
            await self.bot.say("Disabled to prevent malicious behavior.")

        @commands.command(hidden=True)
        async def fuckyou(self):
            """What did you fucking say about me"""
            await self.bot.say(WhatDidYouFuckingSayAboutMe)

        @commands.command(hidden=True)
        async def dreams(self):
            """don't let your dreams be dreams"""
            await self.bot.say(Dreams.format("dreams"))

        @commands.command(hidden=True)
        async def memes(self):
            """don't let your memes be dreams"""
            await self.bot.say(Dreams.format("memes"))

        @commands.command(hidden=True)
        async def shrug(self):
            """shrug"""
            await self.bot.say("¯\_(ツ)_/¯")

        @commands.command(pass_context=True)
        async def flipm(self, ctx, user):
            """Flips a message!

            """
            print(user)
            if user != '':
                msg = ""
                char = "abcdefghijklmnopqrstuvwxyz -"
                tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz -"
                table = str.maketrans(char, tran)
                name = user.translate(table)
                char = char.upper()
                tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z -"
                table = str.maketrans(char, tran)
                name = name.translate(table)
                await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
            else:
                await self.bot.say("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))


def setup(bot):
    n = TrustyBot(bot)
    bot.add_cog(n)
