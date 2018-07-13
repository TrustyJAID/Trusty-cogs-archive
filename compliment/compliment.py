import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from random import choice as randchoice
import os


class Compliment:

    """Airenkun's Insult Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.compliments = fileIO("data/insult/compliment.json", "load")

    @commands.command(pass_context=True, no_pm=True, aliases=["cpl"])
    async def compliment(self, ctx, user : discord.Member=None):
        """Compliment the user"""

        msg = ' '
        if user != None:

            if ctx.message.author.id == "218773382617890828" and user.id == "245862769054711809":
                await self.bot.say(user.mention + " you're cute! :smile:")
                return

            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = [" Hey I appreciate the compliment! :smile:", "No ***YOU'RE*** awesome! :smile:"]
                await self.bot.say(user.mention + randchoice(msg))

            else:
                await self.bot.say(user.mention + msg + randchoice(self.compliments))
        else:
            await self.bot.say(ctx.message.author.mention + msg + randchoice(self.compliments))


def check_folders():
    folders = ("data", "data/compliment/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    """Moves the file from cogs to the data directory. Important -> Also changes the name to insults.json"""
    insults = {"You ugly as hell damn. Probably why most of your friends are online right?"}

    if not os.path.isfile("data/compliment/compliments.json"):
        if os.path.isfile("cogs/put_in_cogs_folder.json"):
            print("moving default insults.json...")
            os.rename("cogs/put_in_cogs_folder.json", "data/compliment/compliments.json")
        else:
            print("creating default compliments.json...")
            fileIO("data/compliment/compliments.json", "save", insults)


def setup(bot):
    check_folders()
    check_files()
    n = Compliment(bot)
    bot.add_cog(n)
