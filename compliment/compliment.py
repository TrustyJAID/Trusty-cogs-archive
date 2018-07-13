import discord
from discord.ext import commands
from random import choice
import os
from .compliments import compliments


class Compliment:

    """Airenkun's Insult Cog"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def compliment(self, ctx, user : discord.Member=None):
        """Insult the user"""

        msg = ' '
        if user != None:

            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = [" Hey, I appreciate the compliment! :smile:", "No ***YOU'RE*** awesome! :smile:"]
                await ctx.send(user.mention + choice(msg))

            else:
                await ctx.send(user.mention + msg + choice(compliments))
        else:
            await ctx.send(ctx.message.author.mention + msg + choice(compliments))
