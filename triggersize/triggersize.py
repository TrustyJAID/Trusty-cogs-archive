import discord
from redbot.core import commands, checks, Config
from redbot.core.data_manager import bundled_data_path
import aiohttp
from io import BytesIO
import functools
import asyncio
from PIL import Image



class Triggersize(getattr(commands, "Cog", object)):
    """
        Generate different sized images based on length of specific keywords
    """

    def __init__(self, bot):
        self.bot = bot
        self.increment = 2
        self.start_size = (1024, 1024)
        self.smallest = (32, 32)
        self.config = Config.get_conf(self, 1545234853)
        default_guild = {"zio":False, "reee":False, "tank":False, "christian":False}
        self.config.register_guild(**default_guild)
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
    
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return
        msg = message.content.lower()
        guild = message.guild
        channel = message.channel

        if "reee" in msg and await self.config.guild(guild).reee():
            for word in msg.split(" "):
                if "reee" in word:
                    await channel.trigger_typing()
                    task = functools.partial(self.change_size_reee, size=len(word)-3)
                    task = self.bot.loop.run_in_executor(None, task)
                    try:
                        file = await asyncio.wait_for(task, timeout=60)
                    except asyncio.TimeoutError:
                        return
                    await message.channel.send(file=file)
                    return
        if "zioo" in msg and await self.config.guild(guild).zio():
            for word in msg.split(" "):
                if "zioo" in word:
                    await channel.trigger_typing()
                    task = functools.partial(self.change_size_zio, size=len(word)-3)
                    task = self.bot.loop.run_in_executor(None, task)
                    try:
                        file = await asyncio.wait_for(task, timeout=60)
                    except asyncio.TimeoutError:
                        return
                    await message.channel.send(file=file)
                    return
        if "taaa" in msg and "nk" in msg and await self.config.guild(guild).tank():
            for word in msg.split(" "):
                if "taaa" in word:
                    url = guild.icon_url_as(format="png", size=64)
                    async with self.session.get(url) as resp:
                        guild_icon = await resp.read()
                    icon = BytesIO(guild_icon)
                    await channel.trigger_typing()
                    task = functools.partial(self.change_size_tank, size=len(word)-3, guild_icon=icon)
                    task = self.bot.loop.run_in_executor(None, task)
                    try:
                        file = await asyncio.wait_for(task, timeout=60)
                    except asyncio.TimeoutError:
                        return
                    await message.channel.send(file=file)
                    return
        if "fuck" in msg.lower() and await self.config.guild(guild).christian():
            async with channel.typing():
                file = discord.File(str(bundled_data_path(self)) + "/christian.jpg")
                await channel.send(file=file)
            
    def change_size_reee(self, size):
        length, width = self.smallest
        if size <=10:
            im = Image.open(str(bundled_data_path(self)) + "/reee.png")
            im.thumbnail((length*size, width*size), Image.ANTIALIAS)
        else:
            size = size-10
            im = Image.open(str(bundled_data_path(self)) + "/reee2.png")
            im.thumbnail((length*size, width*size), Image.ANTIALIAS)
        # im.save("data/reee/newreee.png")
        byte_array = BytesIO()
        im.save(byte_array, format="PNG")
        return discord.File(byte_array.getvalue(), filename="reeee.png")

    def change_size_zio(self, size):
        length, width = self.smallest
        im = Image.open(str(bundled_data_path(self)) + "/zio.jpg")
        im.thumbnail((length*size, width*size), Image.ANTIALIAS)
        byte_array = BytesIO()
        im.save(byte_array, format="PNG")
        return discord.File(byte_array.getvalue(), filename="zio.png")

    def change_size_tank(self, size, guild_icon):
        icon = Image.open(guild_icon)
        icon.convert("RGBA")
        # icon.thumbnail((190, 190), Image.ANTIALIAS)
        length, width = self.smallest
        im = Image.open(str(bundled_data_path(self)) + "/tank.png")
        im.convert("RGBA")
        im.paste(icon, (362,174))
        im.thumbnail((length*size, width*size), Image.ANTIALIAS)
        byte_array = BytesIO()
        im.save(byte_array, format="PNG")
        return discord.File(byte_array.getvalue(), filename="tank.png")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def setreee(self, ctx):
        """Posts various sized reee's when reee is posted"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).reee():
            await self.config.guild(guild).reee.set(True)
            await ctx.send("I will post REEE images on this guild now.")
        else:
            await self.config.guild(guild).reee.set(False)
            await ctx.send("I will not post REEE images on this guild now.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def setzio(self, ctx):
        """Posts various sized zio's when zioo isposted"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).zio():
            await self.config.guild(guild).zio.set(True)
            await ctx.send("I will post zio images on this guild now.")
        else:
            await self.config.guild(guild).zio.set(False)
            await ctx.send("I will not post zio images on this guild now.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def setchristian(self, ctx):
        """Posts various sized zio's when zioo isposted"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).christian():
            await self.config.guild(guild).christian.set(True)
            await ctx.send("I will post this is a christian server images on this guild now.")
        else:
            await self.config.guild(guild).christian.set(False)
            await ctx.send("I will not post this is a christian server images on this guild now.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def settank(self, ctx):
        """Posts various sized tanks when taaank is posted"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).tank():
            await self.config.guild(guild).tank.set(True)
            await ctx.send("I will post tank images on this guild now.")
        else:
            await self.config.guild(guild).tank.set(False)
            await ctx.send("I will not post tank images on this guild now.")

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
