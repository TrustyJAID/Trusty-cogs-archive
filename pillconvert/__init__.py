from .pillconvert import PillConvert


def setup(bot):
    n = PillConvert(bot)
    bot.add_cog(n)