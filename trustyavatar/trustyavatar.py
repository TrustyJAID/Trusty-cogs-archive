import discord
from discord.ext import commands
from random import choice, randint
import asyncio
import aiohttp


class TrustyAvatar:
    """Changes the bot's image every so often"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = ["https://imgur.com/5BzptFg.png", 
                    "https://imgur.com/b4Qpz6V.png",
                    "https://imgur.com/nJXLjip.png",
                    "https://imgur.com/Pwz7rzs.png",
                    "https://imgur.com/bvh93u4.png",
                    "https://imgur.com/VXIUHMb.png",
                    "https://imgur.com/0aVJqlS.png"]
        self.loop = bot.loop.create_task(self.change_avatar())
    
    def __unload(self):
        self.session.close()
        self.loop.cancel()
    
    async def change_avatar(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("TrustyAvatar"):
            try:
                async with self.session.get(choice(self.url)) as r:
                    data = await r.read()
                await self.bot.edit_profile(self.bot.settings.password, avatar=data)
            except Exception as e:
                print(e)
            await asyncio.sleep(randint(1000, 2000))

def setup(bot):
    n = TrustyAvatar(bot)
    bot.add_cog(n)
