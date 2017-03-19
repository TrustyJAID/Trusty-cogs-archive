import discord
from discord.ext import commands
from .utils.chat_formatting import *
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import json
import hashlib
import datetime
import time
import aiohttp
import asyncio


class weather:

    def __init__(self, bot):
        self.bot = bot
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": "°F"},
            "metric": {"code": ["m", "c"], "speed": "km/s", "temp": "°C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/s", "temp": "°K"}}

    @commands.command(pass_context=True, name="weather", aliases=["we"])
    async def weather(self, ctx, city, country="", units="imperial"):
        await self.bot.send_typing(ctx.message.channel)
        await self.getweather(ctx, city, country, units)

    async def getweather(self, ctx, city, country="", units="imperial"):
        if country != "":
            for key, value in self.unit.items():
                if country.lower() in value["code"] or country.lower() == key:
                    units = key
        if units == "kelvin":
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units=metric".format(city+country)
        else:
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units={1}".format(city+country, units)
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        currenttemp = data["main"]["temp"]
        mintemp = data["main"]["temp_min"]
        maxtemp = data["main"]["temp_max"]
        city = data["name"]
        country = data["sys"]["country"]
        lat, lon = data["coord"]["lat"], data["coord"]["lon"]
        condition = ', '.join(info["main"] for info in data["weather"])
        windspeed = str(data["wind"]["speed"]) + " " + self.unit[units]["speed"]
        if units == "kelvin":
            currenttemp = abs(currenttemp - 273.15)
            mintemp = abs(maxtemp - 273.15)
            maxtemp = abs(maxtemp - 273.15)
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="🌍 **Location**", value="{0}, {1}".format(city, country))
        embed.add_field(name="📏 **Lat,Long**", value="{0}, {1}".format(lat, lon))
        embed.add_field(name="☁ **Condition**", value=condition)
        embed.add_field(name="😓 **Humidity**", value=data["main"]["humidity"])
        embed.add_field(name="💨 **Wind Speed**", value="{0}".format(windspeed))
        embed.add_field(name="🌡 **Temperature**", value="{0:.2f}{1}"
                        .format(currenttemp, self.unit[units]["temp"]))
        embed.add_field(name="🔆 **Min - Max**", value="{0:.2f}{1} to {2:.2f}{3}"
                        .format(mintemp, self.unit[units]["temp"], maxtemp, self.unit[units]["temp"]))
        embed.add_field(name="🌄 **Sunrise (utc)**", value=sunrise)
        embed.add_field(name="🌇 **Sunset (utc)**", value=sunset)
        embed.set_footer(text="Powered by http://openweathermap.org")
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    n = weather(bot)
    bot.add_cog(n)
