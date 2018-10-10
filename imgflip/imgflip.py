from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from random import choice
import asyncio
import aiohttp

class Imgflip(getattr(commands, "Cog", object)):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 356889977)
        default_global = {"username": "", "password": ""}
        self.config.register_global(**default_global)
        self.url = "https://api.imgflip.com/caption_image?template_id={0}&username={1}&password={2}"
        self.search = "https://api.imgflip.com/get_memes?username={0}&password={1}"
        self.session = aiohttp.ClientSession(loop=self.bot.loop)


    async def get_meme_id(self, meme):
        url = self.search.format(await self.config.username(), await self.config.password())
        try:
            async with self.session.get(self.search) as r:
                results = await r.json()
            for memes in results["data"]["memes"]:
                if meme.lower() in memes["name"].lower():
                    return memes["id"]
        except:
            await self.get_memes()

    @commands.command(alias=["listmemes"])
    async def getmemes(self, ctx):
        """List memes with names that can be used"""
        await ctx.trigger_typing()
        await self.get_memes(ctx)

    async def get_memes(self, ctx):
        url = self.search.format(await self.config.username(), await self.config.password())
        memelist = "```[p]meme or id;text1;text2\n\n"
        async with self.session.get(self.search) as r:
            results = await r.json()
        for memes in results["data"]["memes"]:
            memelist += memes["name"] + ", "
            if len(memelist) > 1500:
                await ctx.send(memelist + "```")
                memelist = "```"
        await ctx.send(memelist[:len(memelist)-2] + 
                           "``` Find a meme https://imgflip.com/memetemplates click blank template and get the Template ID for more!")

    @commands.command()
    async def meme(self, ctx, *, memeText: str):
        """ Pulls a custom meme from imgflip"""
        msg = memeText.split(";")
        await ctx.trigger_typing()
        if len(msg) == 1:
            meme, text1, text2 = msg[0], " ", " "
        if len(msg) == 2:
            meme, text1, text2 = msg[0], msg[1], " "
        if len(msg) == 3:
            meme, text1, text2 = msg[0], msg[1], msg[2]
        else:
            await ctx.send("Too many text entries! Imgflip allows a maximum of 2 text fields in their API.")
            return

        text_lines = len(msg) - 1
        meme = msg.pop(0)
        
        text1 = text1[:20] if len(text1) > 20 else text1
        text2 = text1[:20] if len(text2) > 20 else text2
        username = await self.config.username()
        password = await self.config.password()
        if not meme.isdigit():
            meme = await self.get_meme_id(meme)
        url = self.url.format(meme, username, password)
        for i in range(0, text_lines):
            url += "&text{}={}".format(i, msg[i])
        if text_lines == 0:
            url += "&text0=%20"
        try:
            async with self.session.get(url) as r:
                result = await r.json()
            if result["data"] != []:
                url = result["data"]["url"]
                await ctx.send(url)
        except:
            await ctx.send("That meme wasn't found!")

    @commands.group(name='imgflipset', aliases=["memeset"])
    @checks.is_owner()
    async def imgflip_set(self, ctx, username:str, password:str):
        """Command for setting required access information for the API"""
        await self.config.username.set(username)
        await self.config.password.set(password)
        await ctx.send("Credentials set!")

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
