import discord
from discord.ext import commands
from random import choice, randint
import asyncio
import aiohttp
import glob


class TrustyAvatar:
    """Changes the bot's image every so often"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.images = glob.glob("data/trustyavatar/*.png")
        self.loop = bot.loop.create_task(self.change_avatar())
        self.status ={
                    "neutral"    : discord.Status.online,
                    "happy"    : discord.Status.online,
                    "are you kidding me"      : discord.Status.idle,
                    "quizzical"      : discord.Status.idle,
                    "sad"      : discord.Status.dnd,
                    "angry"       : discord.Status.dnd,
                    "watching"       : discord.Status.dnd,
                   }
    
    def __unload(self):
        self.session.close()
        self.loop.cancel()
    
    async def change_avatar(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("TrustyAvatar"):
            data = None
            server = self.bot.get_server(id="321105104931389440")
            current_game = server.me.game if server is not None else None

            try:
                # async with self.session.get(choice(self.url)) as r:
                    # data = await r.read()
                new_avatar = choice(self.images)
                image_name = new_avatar.split("/")[-1].split(".")[0]
                with open(new_avatar, "rb") as image:
                    data = image.read()
                if image_name.lower() in self.status:
                    status = self.status.get(image_name.lower(), None)
                    await self.bot.change_presence(status=status, game=current_game)
                print("changing avatar to {}".format(image_name))
                await self.bot.edit_profile(avatar=data)
            except Exception as e:
                print(e)
            await asyncio.sleep(randint(1000, 2000))

def setup(bot):
    n = TrustyAvatar(bot)
    bot.add_cog(n)
