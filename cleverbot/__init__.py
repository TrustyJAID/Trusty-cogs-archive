from .cleverbot import Cleverbot
from redbot.core import data_manager

def setup(bot):
    cog = Cleverbot(bot)
    data_manager.load_bundled_data(cog, __file__)
    bot.add_cog(cog)