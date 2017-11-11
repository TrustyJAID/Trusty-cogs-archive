import discord
from discord.ext import commands
from redbot.core import checks
from redbot.core.data_manager import cog_data_path
from PIL import Image
from PIL import ImageColor
import numpy as np


class PillConvert:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rp"])
    async def redpill(self, ctx):
        """Red Pill"""
        await self.colorconvert("#FF0000")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["bp"])
    async def bluepill(self, ctx):
        """Blue Pill"""
        await self.colorconvert("#0000FF")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["blp"])
    async def blackpill(self, ctx):
        """Black Pill"""
        await self.colorconvert("#008000")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["pp"])
    async def purplepill(self, ctx):
        """Purple Pill"""
        await self.colorconvert("#800080")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["yp"])
    async def yellowpill(self, ctx):
        """Yellow Pill"""
        await self.colorconvert("#FFFF00")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    @commands.command(aliases=["gp"])
    async def greenpill(self, ctx):
        """Green Pill"""
        await self.colorconvert("#008000")
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)

    async def colorconvert(self, colour="#FF0000"):
        im = Image.open(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\blackpill.png")
        im = im.convert('RGBA')
        colour = ImageColor.getrgb(colour)
        data = np.array(im)
        red, green, blue, alpha = data.T
        white_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
        data[..., :-1][white_areas.T] = colour
        im2 = Image.fromarray(data)
        im2.save(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")

    @commands.command()
    async def pill(self, ctx, colour="#FF0000"):
        """Converts the pill to any colour with hex codes like #FF0000"""
        await ctx.trigger_typing()
        await self.colorconvert(colour)
        image = discord.File(str(await self.bot.cog_mgr.install_path()) + "\\pillconvert\\pill.png")
        await ctx.send(file=image)
