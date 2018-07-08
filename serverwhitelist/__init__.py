from .serverwhitelist import ServerWhitelist

def setup(bot):
    n = ServerWhitelist(bot)
    bot.add_cog(n)
