import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
import os
try:
    from PIL import Image
    importavailable = True
except ImportError:
    importavailable = False


class Reee:

    def __init__(self, bot):
        self.bot = bot
        self.fn = "data/reee/newreee.png"
        self.increment = 2
        self.start_size = (1024, 1024)
        self.smallest = (32, 32)
        self.settings = dataIO.load_json("data/reee/settings.json")
    
    async def on_message(self, message):
        if len(message.content) < 2 or message.channel.is_private:
            return
        if message.server.id not in self.settings:
            return
        if message.author.bot:
            return
        msg = message.content.lower()
        if "reee" in msg:
            for word in msg.split(" "):
                if "reee" in word:
                    await self.change_size(len(word)-3)
            print("uploads photo {}".format(self.fn))
            await self.bot.send_file(message.channel, self.fn)

    async def change_size(self, size):
        length, width = self.smallest
        im = Image.open("data/reee/reee.png")
        im.thumbnail((length*size, width*size), Image.ANTIALIAS)
        im.save("data/reee/newreee.png")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def setreee(self, ctx):
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings.append(server.id)
            await self.bot.say("REEE images will now be posted in {}!".format(server.name))
        elif server.id in self.settings:
            self.settings.remove(server.id)
            await self.bot.say("REEE images will no longer be posted in {}!".format(server.name))
        dataIO.save_json("data/reee/settings.json", self.settings)

def check_folder():
    if not os.path.exists("data/reee"):
        print("Creating data/reee folder")
        os.makedirs("data/reee")

def check_file():
    data = []
    f = "data/reee/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    if not importavailable:
        raise NameError("You need to run `pip3 install pillow` and `pip3 install numpy`")
    n = Reee(bot)
    bot.add_cog(n)

