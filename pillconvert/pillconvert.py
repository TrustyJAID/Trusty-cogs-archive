import discord
from discord.ext import commands
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path
from redbot.core.data_manager import cog_data_path
from PIL import Image
from PIL import ImageColor
import numpy as np


class PillConvert:

    def __init__(self, bot):
        self.bot = bot
        self.path = cog_data_path(self)
        self.bundle_path = bundled_data_path(self)

    @commands.command()
    async def printpath(self, ctx):
        print(self.path)

    @commands.command(aliases=["rp"])
    async def redpill(self, ctx):
        """Red Pill"""
        await self.colorconvert("#FF0000")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["bp"])
    async def bluepill(self, ctx):
        """Blue Pill"""
        await self.colorconvert("#0000FF")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["blp"])
    async def blackpill(self, ctx):
        """Black Pill"""
        await self.colorconvert("#008000")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["pp"])
    async def purplepill(self, ctx):
        """Purple Pill"""
        await self.colorconvert("#800080")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["yp"])
    async def yellowpill(self, ctx):
        """Yellow Pill"""
        await self.colorconvert("#FFFF00")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["gp"])
    async def greenpill(self, ctx):
        """Green Pill"""
        await self.colorconvert("#008000")
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)

    async def colorconvert(self, colour="#FF0000"):
        im = Image.open(str(self.bundle_path) + "\\blackpill.png")
        im = im.convert('RGBA')
        colour = ImageColor.getrgb(colour)
        data = np.array(im)
        red, green, blue, alpha = data.T
        white_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
        data[..., :-1][white_areas.T] = colour
        im2 = Image.fromarray(data)
        im2.save(str(self.path) + "\\pill.png")

    @commands.command()
    async def pill(self, ctx, colour="#FF0000"):
        """Converts the pill to any colour with hex codes like #FF0000"""
        await ctx.trigger_typing()
        await self.colorconvert(colour)
        image = discord.File(str(self.path) + "\\pill.png")
        await ctx.send(file=image)
