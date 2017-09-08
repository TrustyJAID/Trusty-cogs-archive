import discord
from random import choice
import random
from discord.ext import commands
from .utils.dataIO import dataIO

class Faces:

    def __init__(self, bot):
        self.bot = bot
        self.faces = dataIO.load_json("data/faces/CIAJapaneseStyleFaces.json")
    
    @commands.command(pass_context=True, aliases=["japaneseface"])
    async def face(self, ctx, number=None):
        """Japanese Faces at random courtesy of the CIA"""
        if number is None:
            await self.bot.say(choice(self.faces))
            return
        if "<@" in str(number):
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

def setup(bot):
    bot.add_cog(Faces(bot))