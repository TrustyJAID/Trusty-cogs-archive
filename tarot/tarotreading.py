import discord
from discord.ext import commands
from .utils.dataIO import dataIO
import aiohttp
import json
import random
from random import sample
from random import choice
import time


class TarotReading:
    """It's time to get your fortune!!!"""

    def __init__(self, bot):
        self.bot = bot
        self.tarot = dataIO.load_json("data/tarot/tarot.json")

    def get_colour(self):
        colour =''.join([choice('0123456789ABCDEF')for x in range(6)])
        return int(colour, 16)

    @commands.group(pass_context=True)
    async def tarots(self, ctx):
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
    
    @tarots.command(name="life", pass_context=True)
    async def _life(self, ctx, user: discord.Member=None):
        card_meaning = ["Past", "Present", "Future", "Potential", "Reason"]
        if user is None:
            user = ctx.message.author
        userseed = user.id
        
        random.seed(int(userseed))
        cards = []
        cards = sample((range(1, 78)), 5)
        
        embed = discord.Embed(title="Tarot reading for {}".format(user.display_name),
                              colour=discord.Colour(value=self.get_colour()))
        number = 0
        for card in cards:
            embed.add_field(name="{0}: {1}".format(card_meaning[number], self.tarot[str(card)]["card_name"]),
                            value=self.tarot[str(card)]["card_meaning"])
            number += 1
        await self.bot.send_message(ctx.message.channel, embed=embed)
    
    @tarots.command(name="reading", pass_context=True)
    async def _reading(self, ctx, user: discord.Member=None):
        card_meaning = ["Past", "Present", "Future", "Potential", "Reason"]
        if user is None:
            user = ctx.message.author
        
        cards = []
        cards = sample((range(1, 78)), 5)
        
        embed = discord.Embed(title="Tarot reading for {}".format(user.display_name),
                              colour=discord.Colour(value=self.get_colour()))
        number = 0
        for card in cards:
            embed.add_field(name="{0}: {1}".format(card_meaning[number], self.tarot[str(card)]["card_name"]),
                            value=self.tarot[str(card)]["card_meaning"])
            number += 1
        await self.bot.send_message(ctx.message.channel, embed=embed)


    @tarots.command(name="card", pass_context=True)
    async def _card(self, ctx, *, msg=None):
        user = ctx.message.author.id
        # msg = message.content
        card = None

        if msg is None:
            card = self.tarot[str(random.randint(1, 78))]

        elif msg.isdigit() and int(msg) > 0 and int(msg) < 79:
            card = self.tarot[str(msg)]
        
        elif not msg.isdigit():
            for cards in self.tarot:
                if msg.lower() in self.tarot[cards]["card_name"].lower():
                    card = self.tarot[cards]
            if card is None:
                await self.bot.say("That card does not exist!")
                return

        embed = discord.Embed(title=card["card_name"],
                              description=card["card_meaning"],
                              colour=discord.Colour(value=self.get_colour()),
                              url=card["card_url"])
        embed.set_image(url=card["card_img"])
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(TarotReading(bot))