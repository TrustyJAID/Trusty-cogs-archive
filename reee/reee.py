import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks

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
    
    async def on_message(self, message):
        if len(message.content) < 2 or message.channel.is_private:
            return
        if message.server.id == "133049272517001216":
            return
        if message.author == self.bot.user:
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


def setup(bot):
    if not importavailable:
        raise NameError("You need to run `pip3 install pillow` and `pip3 install numpy`")
    n = Reee(bot)
    bot.add_cog(n)

