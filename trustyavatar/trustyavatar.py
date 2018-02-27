import discord
from discord.ext import commands
from redbot.core.data_manager import bundled_data_path
from random import choice, randint
import asyncio
import aiohttp
import glob


class TrustyAvatar:
    """Changes the bot's image every so often"""

    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop.create_task(self.change_avatar())
        self.status ={
                    "neutral": {"status":discord.Status.online, "game":["Please Remain Calm", "Mind the Gap"]},
                    "happy": {"status":discord.Status.online, "game":["Take it to Make it"]},
                    "are you kidding me": {"status":discord.Status.idle, "game":["Obey Posted Limits"]},
                    "quizzical": {"status": discord.Status.idle, "game":["Yellow Means Yield"]},
                    "sad": {"status": discord.Status.dnd, "game":["No Public Access"]},
                    "angry": {"status":discord.Status.dnd, "game":["Hitchhickers May Be Escaping Inmates"]},
                    "watching": {"status":discord.Status.dnd, "game":[]},
                   }
    
    def __unload(self):
        self.loop.cancel()
    
    async def change_avatar(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("TrustyAvatar"):
            self.images = glob.glob(str(bundled_data_path(self)) + "/regular/*.png")
            data = None
            # server = self.bot.get_server(id=321105104931389440)
            # current_game = server.me.game if server is not None else None

            try:
                # async with self.session.get(choice(self.url)) as r:
                    # data = await r.read()
                new_avatar = choice(self.images)
                image_name = new_avatar.split("/")[-1].split(".")[0]
                with open(new_avatar, "rb") as image:
                    data = image.read()
                status = self.status.get(image_name.lower(), None)
                try:
                    game_name = choice(status["game"])
                    game = discord.Game(name=game_name)
                except:
                    pass
                await self.bot.change_presence(status=status["status"], game=game)
                print("changing avatar to {}".format(image_name))
                await self.bot.user.edit(avatar=data)
            except Exception as e:
                print(e)
            await asyncio.sleep(randint(1000, 1500))
