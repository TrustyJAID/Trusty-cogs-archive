from .gab import Gab

def setup(bot):
    n = Gab(bot)
    bot.add_cog(n)