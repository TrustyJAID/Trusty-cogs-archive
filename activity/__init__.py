from .activity import ActivityChecker


def setup(bot):
    n = ActivityChecker(bot)
    bot.add_cog(n)