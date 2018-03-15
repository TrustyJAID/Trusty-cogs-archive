from .feels import Feels
from redbot.core import data_manager

def setup(bot):
    cog = Feels(bot)
    data_manager.load_bundled_data(cog, __file__)
    bot.add_cog(cog)