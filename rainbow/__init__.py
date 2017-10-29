from .rainbow import rainbow

def setup(bot):
    n = Rainbow(bot)
    bot.add_cog(n)
