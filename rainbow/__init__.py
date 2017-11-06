from .rainbow import Rainbow

def setup(bot):
    n = Rainbow(bot)
    bot.add_cog(n)
