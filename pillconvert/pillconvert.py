import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path
from PIL import Image
from PIL import ImageColor
import numpy as np
import asyncio
import functools
from io import BytesIO


class PillConvert:

    def __init__(self, bot):
        self.bot = bot

    def colour_convert(self, colour="#FF0000"):
        im = Image.open(str(bundled_data_path(self)) + "/blackpill.png")
        im = im.convert('RGBA')
        colour = ImageColor.getrgb(colour)
        data = np.array(im)
        red, green, blue, alpha = data.T
        white_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 255)
        data[..., :-1][white_areas.T] = colour
        im2 = Image.fromarray(data)
        temp = BytesIO()
        im2.save(temp, format="PNG")
        temp.name = "pill.png"
        return temp

    @commands.command(aliases=["rp"])
    async def redpill(self, ctx):
        """Red Pill"""
        pill_image = await self.make_colour("#FF0000")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    @commands.command(aliases=["bp"])
    async def bluepill(self, ctx):
        """Blue Pill"""
        pill_image = await self.make_colour("#0000FF")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    @commands.command(aliases=["blp"])
    async def blackpill(self, ctx):
        """Black Pill"""
        pill_image = await self.make_colour("#008000")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    @commands.command(aliases=["pp"])
    async def purplepill(self, ctx):
        """Purple Pill"""
        pill_image = await self.make_colour("#800080")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    @commands.command(aliases=["yp"])
    async def yellowpill(self, ctx):
        """Yellow Pill"""
        pill_image = await self.make_colour("#FFFF00")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    @commands.command(aliases=["gp"])
    async def greenpill(self, ctx):
        """Green Pill"""
        pill_image = await self.make_colour("#008000")
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)

    async def make_colour(self, colour):
        task = functools.partial(self.colour_convert,colour=colour)
        task = self.bot.loop.run_in_executor(None, task)
        try:
            image = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return
        image.seek(0)
        return image

    @commands.command()
    async def pill(self, ctx, colour="#FF0000"):
        """Converts the pill to any colour with hex codes like #FF0000"""
        await ctx.trigger_typing()
        pill_image = await self.make_colour(colour)
        if pill_image is None:
                await ctx.send("Something went wrong sorry!")
                return
        image = discord.File(pill_image)
        await ctx.send(file=image)
