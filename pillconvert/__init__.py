from .pillconvert import PillConvert
from redbot.core import data_manager


def setup(bot):
    n = PillConvert(bot)
    data_manager.load_bundled_data(n, __file__)
    bot.add_cog(n)