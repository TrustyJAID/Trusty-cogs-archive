import discord
from discord.ext import commands
import datetime
import aiohttp
import asyncio
import json


class Conversions:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(pass_context=True, aliases=["bitcoin", "BTC"])
    async def btc(self, ctx, ammount:float=1.0, currency="USD", full=True):
        """converts from BTC to a given currency."""
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, "BTC", ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, "BTC", ammount, currency, False)
        embed.colour = discord.Colour.gold()
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["ethereum", "ETH"])
    async def eth(self, ctx, ammount:float=1.0, currency="USD", full=True):
        """converts from ETH to a given currency."""
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, "ETH", ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, "ETH", ammount, currency, False)
        embed.colour = discord.Colour.dark_grey()
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["litecoin", "LTC"])
    async def ltc(self, ctx, ammount:float=1.0, currency="USD", full=True):
        """converts from LTC to a given currency."""
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, "LTC", ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, "LTC", ammount, currency, False)
        embed.colour = discord.Colour.dark_grey()
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["monero", "XMR"])
    async def xmr(self, ctx, ammount:float=1.0, currency="USD", full=True):
        """converts from LTC to a given currency."""
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, "XMR", ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, "XMR", ammount, currency, False)
        embed.colour = discord.Colour.orange()
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["bitcoin-cash", "BCH"])
    async def bch(self, ctx, ammount:float=1.0, currency="USD", full=True):
        """converts from LTC to a given currency."""
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, "BCH", ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, "BCH", ammount, currency, False)
        embed.colour = discord.Colour.orange()
        await self.bot.send_message(ctx.message.channel, embed=embed)
    
    async def checkcoins(self, base):
        link = "https://api.coinmarketcap.com/v1/ticker/"
        async with self.session.get(link) as resp:
            data = await resp.json()
        for coin in data:
            if base.upper() == coin["symbol"].upper() or base.lower() == coin["name"].lower():
                return coin 
        return None

    @commands.command(pass_context=True)
    async def crypto(self, ctx, coin, ammount:float=1.0, currency="USD", full=True):
        if ammount == 1.0:
            embed = await self.crypto_embed(ctx, coin, ammount, currency, full)
        else:
            embed = await self.crypto_embed(ctx, coin, ammount, currency, False)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    async def crypto_embed(self, ctx, coin, ammount=1.0, currency="USD", full=True):
        """Gets crypto currency information."""
        coin_data = await self.checkcoins(coin)
        if coin_data is None:
            await self.bot.send_message(ctx.message.channel, "{} is not in my list of currencies!".format(coin))
            return      
        price = float(coin_data["price_usd"]) * ammount
        market_cap = float(coin_data["market_cap_usd"])
        volume_24h = float(coin_data["24h_volume_usd"])
        coin_image = "https://files.coinmarketcap.com/static/img/coins/128x128/{}.png".format(coin_data["id"])
        coin_url = "https://coinmarketcap.com/currencies/{}".format(coin_data["id"])
        if currency.upper() != "USD":
            conversionrate = await self.conversionrate("USD", currency.upper())
            price = conversionrate * price
            market_cap = conversionrate * market_cap
            volume_24h = conversionrate * volume_24h
        msg = "{0} {3} is {1:.2f} {2}".format(ammount, price, currency.upper(), coin_data["symbol"])
        embed = discord.Embed(description=msg, colour=discord.Colour.dark_grey())
        embed.set_footer(text="As of")
        embed.set_author(name=coin_data["name"], url=coin_url, icon_url=coin_image)
        embed.timestamp = datetime.datetime.utcfromtimestamp(int(coin_data["last_updated"]))
        if full:
            embed.set_thumbnail(url=coin_image)
            embed.add_field(name="Market Cap", value="{} {}".format(market_cap, currency.upper()), inline=True)
            embed.add_field(name="24 Hour Volue", value="{} {}".format(volume_24h, currency.upper()))
            embed.add_field(name="Available Supply", value=coin_data["available_supply"], inline=True)
            embed.add_field(name="Max Supply", value=coin_data["max_supply"], inline=True)
            embed.add_field(name="Total Supply", value=coin_data["total_supply"], inline=True)
            embed.add_field(name="Change 1 hour", value="{}%".format(coin_data["percent_change_1h"]), inline=True)
            embed.add_field(name="Change 24 hours", value="{}%".format(coin_data["percent_change_24h"]), inline=True)
            embed.add_field(name="Change 7 days", value="{}%".format(coin_data["percent_change_7d"]), inline=True)
        return embed

    @commands.command(pass_context=True, aliases=["au", "AU", "Au", "GOLD"])
    async def gold(self, ctx, ammount=1, currency="USD"):
        """converts gold in ounces to a given currency."""
        GOLD = "https://www.quandl.com/api/v3/datasets/WGC/GOLD_DAILY_{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
        async with self.session.get(GOLD.format(currency.upper())) as resp:
            data = await resp.json()
        price = (data["dataset"]["data"][0][1]) * ammount
        msg = "{0} oz of Gold is {1:.2f} {2}".format(ammount, price, currency.upper())
        embed = discord.Embed(descirption="Gold", colour=discord.Colour.gold())
        embed.add_field(name="Gold", value=msg)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d7/Gold-crystals.jpg")
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["ag", "AG", "Ag", "SILVER"])
    async def silver(self, ctx, ammount=1, currency="USD"):
        """converts silver in ounces to a given currency."""
        SILVER = "https://www.quandl.com/api/v3/datasets/LBMA/SILVER.json?api_key=EKvr5W-sJUFVSevcpk4v"
        async with self.session.get(SILVER) as resp:
            data = await resp.json()
        price = (data["dataset"]["data"][0][1]) * ammount
        if currency != "USD":
            price = await self.conversionrate("USD", currency.upper()) * price
        msg = "{0} oz of Silver is {1:.2f} {2}".format(ammount, price, currency.upper())
        embed = discord.Embed(descirption="Silver", colour=discord.Colour.lighter_grey())
        embed.add_field(name="Silver", value=msg)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/5/55/Silver_crystal.jpg")
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["pt", "PT", "Pt", "PLATINUM"])
    async def platinum(self, ctx, ammount=1, currency="USD"):
        """converts platinum in ounces to a given currency."""
        PLATINUM = "https://www.quandl.com/api/v3/datasets/JOHNMATT/PLAT.json?api_key=EKvr5W-sJUFVSevcpk4v"
        async with self.session.get(PLATINUM) as resp:
            data = await resp.json()
        price = (data["dataset"]["data"][0][1]) * ammount
        if currency != "USD":
            price = await self.conversionrate("USD", currency.upper()) * price
        msg = "{0} oz of Platinum is {1:.2f} {2}".format(ammount, price, currency.upper())
        embed = discord.Embed(descirption="Platinum", colour=discord.Colour.dark_grey())
        embed.add_field(name="Platinum", value=msg)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/6/68/Platinum_crystals.jpg")
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True, aliases=["ticker"])
    async def stock(self, ctx, ticker, currency="USD"):
        """Gets current ticker symbol price."""
        stock = "https://www.quandl.com/api/v3/datasets/WIKI/{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
        async with self.session.get(stock.format(ticker.upper())) as resp:
            data = await resp.json()
        convertrate = 1
        if currency != "USD":
            convertrate = self.conversionrate("USD", currency.upper())
        price = (data["dataset"]["data"][0][1]) * convertrate
        msg = "{0} is {1:.2f} {2}".format(ticker.upper(), price, currency.upper())
        embed = discord.Embed(descirption="Stock Price", colour=discord.Colour.lighter_grey())
        embed.add_field(name=ticker.upper(), value=msg)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def convert(self, ctx, ammount:float=1.0, currency1="USD", currency2="GBP"):
        """Converts between different currencies"""
        conversion = await self.conversionrate(currency1.upper(), currency2.upper()) 
        conversion = conversion * ammount
        await self.bot.send_message(ctx.message.channel, "{0} {1} is {2:.2f} {3}".format(ammount, currency1, conversion, currency2))

    async def conversionrate(self, currency1, currency2):
        """Function to convert different currencies"""
        CONVERSIONRATES = "http://api.fixer.io/latest?base={}".format(currency1.upper())
        try:
            async with self.session.get(CONVERSIONRATES) as resp:
                data = await resp.json()
            conversion = (data["rates"][currency2.upper()])
            return conversion
        except:
            return None
        """TODO: add feeder cattle, coffee, and sugar"""


def setup(bot):
    n = Conversions(bot)
    bot.add_cog(n)
