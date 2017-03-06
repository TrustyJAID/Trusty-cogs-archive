import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks

try:
    from PIL import Image
    from PIL import ImageColor
    import numpy as np
    importavailable = True
except ImportError:
    importavailable = False


class PillConvert:

    def __init__(self, bot):
        self.bot = bot
        self.fn = "data/pillconvert/pill.png"

    @commands.command(pass_context=True, aliases=["rp"])
    async def redpill(self, ctx):
        """Red Pill"""
        await self.colorconvert("#FF0000")
        await self.bot.send_file(ctx.message.channel, self.fn)

    @commands.command(pass_context=True, aliases=["bp"])
    async def bluepill(self, ctx):
        """Blue Pill"""
        await self.colorconvert("#0000FF")
        await self.bot.send_file(ctx.message.channel, self.fn)

    @commands.command(pass_context=True, aliases=["blp"])
    async def blackpill(self, ctx):
        """Black Pill"""
        await self.colorconvert("#008000")
        await self.bot.send_file(ctx.message.channel, self.fn)

    @commands.command(pass_context=True, aliases=["pp"])
    async def purplepill(self, ctx):
        """Purple Pill"""
        await self.colorconvert("#800080")
        await self.bot.send_file(ctx.message.channel, self.fn)

    @commands.command(pass_context=True, aliases=["yp"])
    async def yellowpill(self, ctx):
        """Yellow Pill"""
        await self.colorconvert("#FFFF00")
        await self.bot.send_file(ctx.message.channel, self.fn)

    @commands.command(pass_context=True, aliases=["gp"])
    async def greenpill(self, ctx):
        """Green Pill"""
        await self.colorconvert("#008000")
        await self.bot.send_file(ctx.message.channel, self.fn)

    async def colorconvert(self, colour="#FF0000"):
        im = Image.open("data/pillconvert/blackpill.png")
        im = im.convert('RGBA')
        colour = ImageColor.getrgb(colour)
        data = np.array(im)
        red, green, blue, alpha = data.T
        white_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
        data[..., :-1][white_areas.T] = colour
        im2 = Image.fromarray(data)
        im2.save("data/pillconvert/pill.png")

    @commands.command(hidden=False, pass_context=True)
    async def pill(self, ctx, colour="#FF0000"):
        """Converts the pill to any colour with hex codes like #FF0000"""
        await self.colorconvert(colour)
        await self.bot.send_file(ctx.message.channel, self.fn)


def setup(bot):
    if not importavailable:
        raise NameError("You need to run `pip3 install pillow` and `pip3 install numpy`")
    n = PillConvert(bot)
    bot.add_cog(n)

