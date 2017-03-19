import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import requests
import hashlib
import datetime
import time
import aiohttp
import asyncio
import random
import codecs
import json


class Conversions:

    def __init__(self, bot):
        self.bot = bot
        self.btcurl = "https://blockchain.info/tobtc?currency={0}&value={1}"

    @commands.command(hidden=False)
    async def converttobtc(self, ammount=1.0, currency="USD"):
        """converts to BTC from a given currency."""
        url = self.btcurl.format(currency.upper(), ammount)
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
            msg = "{0} {1} is {2} BTC ₿".format(ammount, currency.upper(), float(data))
            embed = discord.Embed(descirption="BTC", colour=discord.Colour.gold())
            embed.add_field(name="Bitcoin", value=msg)
            embed.set_thumbnail(url="https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

    @commands.command(hidden=False, aliases=["bitcoin", "BTC"])
    async def btc(self, ammount=1.0, currency="USD"):
        """converts from BTC to a given currency."""
        url = self.btcurl.format(currency.upper(), 1)
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
            conversion = (1/float(data))*float(ammount)
            msg = "{0} BTC is {1:.2f} {2}".format(ammount, conversion, currency.upper())
            embed = discord.Embed(descirption="BTC", colour=discord.Colour.gold())
            embed.add_field(name="Bitcoin", value=msg)
            embed.set_thumbnail(url="https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

    @commands.command(hidden=False, aliases=["ethereum", "ETH"])
    async def eth(self, ammount=1.0, currency="USD"):
        """converts from ETH to a given currency."""
        ETH = "https://etherchain.org/api/statistics/price"
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(ETH) as resp:
                    data = await resp.json()
            price = data["data"][-1]["usd"] * ammount
            if currency.upper() != "USD":
                price = await self.conversionrate("USD", currency.upper()) * price
            msg = "{0} ETH is {1:.2f} {2}".format(ammount, price, currency.upper())
            embed = discord.Embed(descirption="BTC", colour=discord.Colour.dark_grey())
            embed.add_field(name="Etherium", value=msg)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/ETHEREUM-YOUTUBE-PROFILE-PIC.png/768px-ETHEREUM-YOUTUBE-PROFILE-PIC.png")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")


    @commands.command(hidden=False, aliases=["au", "AU", "Au", "GOLD"])
    async def gold(self, ammount=1, currency="USD"):
        """converts gold in ounces to a given currency."""
        GOLD = "https://www.quandl.com/api/v3/datasets/WGC/GOLD_DAILY_{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(GOLD.format(currency.upper())) as resp:
                    data = await resp.json()
            price = (data["dataset"]["data"][0][1]) * ammount
            msg = "{0} oz of Gold is {1:.2f} {2}".format(ammount, price, currency.upper())
            embed = discord.Embed(descirption="Gold", colour=discord.Colour.gold())
            embed.add_field(name="Gold", value=msg)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d7/Gold-crystals.jpg")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

    @commands.command(hidden=False, aliases=["ag", "AG", "Ag", "SILVER"])
    async def silver(self, ammount=1, currency="USD"):
        """converts silver in ounces to a given currency."""
        SILVER = "https://www.quandl.com/api/v3/datasets/LBMA/SILVER.json?api_key=EKvr5W-sJUFVSevcpk4v"
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(SILVER) as resp:
                    data = await resp.json()
            price = (data["dataset"]["data"][0][1]) * ammount
            if currency != "USD":
                price = await self.conversionrate("USD", currency.upper()) * price
            msg = "{0} oz of Silver is {1:.2f} {2}".format(ammount, price, currency.upper())
            embed = discord.Embed(descirption="Silver", colour=discord.Colour.lighter_grey())
            embed.add_field(name="Silver", value=msg)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/5/55/Silver_crystal.jpg")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

    @commands.command(hidden=False, aliases=["pt", "PT", "Pt", "PLATINUM"])
    async def platinum(self, ammount=1, currency="USD"):
        """converts platinum in ounces to a given currency."""
        PLATINUM = "https://www.quandl.com/api/v3/datasets/JOHNMATT/PLAT.json?api_key=EKvr5W-sJUFVSevcpk4v"
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(PLATINUM) as resp:
                    data = await resp.json()
            price = (data["dataset"]["data"][0][1]) * ammount
            if currency != "USD":
                price = await self.conversionrate("USD", currency.upper()) * price
            msg = "{0} oz of Platinum is {1:.2f} {2}".format(ammount, price, currency.upper())
            embed = discord.Embed(descirption="Platinum", colour=discord.Colour.dark_grey())
            embed.add_field(name="Platinum", value=msg)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/6/68/Platinum_crystals.jpg")
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a regular integer and standard currency, please! :smile:")

    @commands.command(hidden=False, aliases=["ticker"])
    async def stock(self, ticker, currency="USD"):
        """Gets current ticker symbol price."""
        stock = "https://www.quandl.com/api/v3/datasets/WIKI/{}.json?api_key=EKvr5W-sJUFVSevcpk4v"
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(stock.format(ticker.upper())) as resp:
                    data = await resp.json()
            convertrate = 1
            if currency != "USD":
                convertrate = self.conversionrate("USD", currency.upper())
            price = (data["dataset"]["data"][0][1]) * convertrate
            msg = "{0} is {1:.2f} {2}".format(ticker.upper(), price, currency.upper())
            embed = discord.Embed(descirption="Stock Price", colour=discord.Colour.lighter_grey())
            embed.add_field(name=ticker.upper(), value=msg)
            await self.bot.say(embed=embed)
        except:
            await self.bot.say("Pick a correct ticker symbol!")

    @commands.command(hidden=False)
    async def convert(self, ammount=1, currency1="USD", currency2="GBP"):
        """Converts between different currencies"""
        try:
            conversion = await self.conversionrate(currency1.upper(), currency2.upper()) * ammount
            await self.bot.say("{0} {1} is {2:.2f} {3}".format(ammount, currency1, conversion, currency2))
        except:
            await self.bot.say("Please enter a proper integer and standard currency! :smile:")

    async def conversionrate(self, currency1, currency2):
        """Function to convert different currencies"""
        CONVERSIONRATES = "http://api.fixer.io/latest?base={}".format(currency1.upper())
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(CONVERSIONRATES) as resp:
                    data = await resp.json()
            conversion = (data["rates"][currency2.upper()])
            return conversion
        except:
            return "That currency is not valid"
        """TODO: add feeder cattle, coffee, and sugar"""


def setup(bot):
    n = Conversions(bot)
    bot.add_cog(n)
