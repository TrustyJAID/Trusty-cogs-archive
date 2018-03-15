from PIL import Image
from PIL import ImageColor
from PIL import ImageSequence
import numpy as np
import glob
import os
import json
import numpy as np
import os
import aiohttp
import discord
from discord.ext import commands
from redbot.core.data_manager import bundled_data_path
from io import BytesIO, StringIO
import sys
import functools
import asyncio

class Feels:
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.files = "data/feels/"

    def __unload(self):
        self.session.close()

    async def dl_image(self, url):
        async with self.session.get(url) as resp:
            test = await resp.read()
            return BytesIO(test)

    @commands.command(pass_context=True)
    async def feels(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.message.author
        async with ctx.channel.typing():
            feels_img = await self.make_feels(user)
            if feels_img is None:
                await ctx.send("sorry something went wrong!")
                return
            file = discord.File(feels_img)
            # ext = await self.make_feels(user)
            await ctx.send(file=file)

    def make_animated_gif(self, user, avatar):
        gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
        img_list = []
        num = 0
        temp = None
        for frame in gif_list:
            template = Image.open(str(bundled_data_path(self)) + "/pepetemplate.png")
            template = template.convert("RGBA")
            colour = user.top_role.colour.to_rgb()
            transparency = template.split()[-1].getdata()
            data = np.array(template)
            red, green, blue, alpha = data.T
            blue_areas = (red == 0) & (blue > 205) & (green == 0) & (alpha > 50)
            data[..., :-1][blue_areas.T] = colour
            temp2 = Image.fromarray(data)
            frame = frame.convert("RGBA")
            frame = frame.rotate(-30, expand=True)
            frame = frame.resize((150, 150), Image.ANTIALIAS)
            temp2.paste(frame, (150, 60), frame)
            # temp2.thumbnail((320, 320), Image.ANTIALIAS)
            img_list.append(temp2)
            num += 1
            temp = BytesIO()
            temp2.save(temp, format="GIF", save_all=True, append_images=img_list, duration=0, loop=0, transparency=0)
            temp.name = "{}.gif".format(user.display_name)
            if sys.getsizeof(temp) < 8000000 and sys.getsizeof(temp) > 7000000:
                break
        return temp

    def make_feels_img(self, user, avatar):
        template = Image.open(str(bundled_data_path(self)) + "/pepetemplate.png")
        # print(template.info)
        template = template.convert("RGBA")
        colour = user.top_role.colour.to_rgb()
        print(colour)
        # avatar = Image.open(self.files + "temp." + ext)
        transparency = template.split()[-1].getdata()
        data = np.array(template)
        red, green, blue, alpha = data.T
        blue_areas = (red == 0) & (blue == 255) & (green == 0) & (alpha == 255)
        data[..., :-1][blue_areas.T] = colour
        temp2 = Image.fromarray(data)
        temp2 = temp2.convert("RGBA")
        avatar = avatar.convert("RGBA")
        avatar = avatar.rotate(-30, expand=True)
        avatar = avatar.resize((150, 150), Image.ANTIALIAS)
        temp2.paste(avatar, (150, 60), avatar)
        temp = BytesIO()
        temp2.save(temp, format="PNG")
        temp.name = "{}.png".format(user.display_name)
        return temp


    async def make_feels(self, user):

        if user.is_avatar_animated():
            avatar = Image.open(await self.dl_image(user.avatar_url_as(format="gif")))
            task = functools.partial(self.make_animated_gif, user=user, avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return
        else:
            avatar = Image.open(await self.dl_image(user.avatar_url_as(format="png")))
            task = functools.partial(self.make_feels_img, user=user, avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return
        temp.seek(0)
        return temp
