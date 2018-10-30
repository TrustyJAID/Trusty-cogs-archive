import discord
from redbot.core import commands
import re

class Covfefe(getattr(commands, "Cog", object)):

    def __init__(self, bot):
        self.bot = bot
    
    async def covfefe(self, x, k='aeiouy])'):
        try:
            b,c,v=re.findall(f'(.*?[{k}([^{k}.*?([{k}',x)[0];return b+c+(('bcdfgkpstvz'+c)['pgtvkgbzdfs'.find(c)]+v)*2
        except:
            return None
    
    @commands.command()
    async def covefy(self, ctx, msg):
        """Convert almost any word into covfefe"""
        newword = await self.covfefe(msg)
        if newword is not None:
            await ctx.send(newword)
        else:
            await ctx.send("I cannot covfefeify that word")
