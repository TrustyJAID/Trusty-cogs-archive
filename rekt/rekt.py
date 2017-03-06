import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
import time
import asyncio


class rekt:
    def __init__(self, bot):
        self.bot = bot
        self.STARTTIME = time.time()
        self.rektlist = dataIO.load_json("data/rekt/rekt.json")

    @commands.command(hidden=False, pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def rekt(self, ctx, endcount=10):
        """REKT"""
        server = str(ctx.message.server.id)
        user = ctx.message.author.id
        rektemoji = ["\u2611", "\U0001F1F7", "\U0001F1EA", "\U0001F1F0", "\U0001F1F9"]
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="NOT REKT", value="⬜ Not Rekt", inline=True)
        count = 0
        count2 = 0
        message = ""
        for line in self.rektlist:
            if count2 == 10:
                embed.add_field(name="REKT", value=message, inline=True)
                count2 = 0
                message = ""

            message += line + "\n"
            count += 1
            count2 += 1
            if count == endcount:
                break
        if message != "":
            embed.add_field(name="REKT", value=message, inline=True)
        embed.set_author(name="Are you REKT?")
        msg = await self.bot.send_message(ctx.message.channel, embed=embed)
        for emoji in rektemoji:
            await self.bot.add_reaction(msg, emoji=emoji)


def setup(bot):
    n = rekt(bot)
    bot.add_cog(n)
