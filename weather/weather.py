import discord
from discord.ext import commands
from .utils.chat_formatting import *
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import urllib.request
import json
import hashlib
import datetime
import time
import aiohttp
import asyncio


class weather:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="weather", aliases=["we"])
    async def weather(self, ctx, city, country="", units="imperial"):
        if country == "metric" or country == "imperial" or country == "kelvin":
            units = country
        if country == "m" or country == "i" or country == "k":
            unitconvert = {"i":"imperial", "m":"metric", "k": "kelvin"}
            units = unitconvert[country]
        if units == "m" or units == "i" or units == "k":
            unitconvert = {"i":"imperial", "m":"metric", "k": "kelvin"}
            units = unitconvert[units]
        if units == "kelvin":
            data = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units=metric".format(city+country)
        else:
            data = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units={1}".format(city+country, units)
        data = urllib.request.urlopen(data)
        data = json.loads(data.read())
        speed = {"metric":"km/h", "imperial":"mph", "kelvin": "km/h"}
        temp = {"metric":"°C", "imperial":"°F", "kelvin": "°K"}
        currenttemp = data["main"]["temp"]
        mintemp = data["main"]["temp_min"]
        maxtemp = data["main"]["temp_max"]
        if units == "kelvin":
            currenttemp = currenttemp - 273.15
            mintemp = maxtemp - 273.15
            maxtemp = maxtemp - 273.15
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="🌍 **Location**", value=data["name"] + ", " + data["sys"]["country"], inline=True)
        embed.add_field(name="📏 **Lat,Long**", value=str(data["coord"]["lat"]) + ", " + str(data["coord"]["lon"]), inline=True)
        embed.add_field(name="☁ **Condition**", value=', '.join(info["main"] for info in data["weather"]), inline=True)
        embed.add_field(name="😓 **Humidity**", value=data["main"]["humidity"], inline=True)
        embed.add_field(name="💨 **Wind Speed**", value=str(data["wind"]["speed"]) + speed[units], inline=True)
        embed.add_field(name="🌡 **Temperature**", value=str(currenttemp) + temp[units], inline=True)
        embed.add_field(name="🔆 **Min - Max**", value=str(mintemp) + temp[units]+ " - " + str(maxtemp) + temp[units], inline=True)
        embed.add_field(name="🌄 **Sunrise (utc)**", value=sunrise, inline=True)
        embed.add_field(name="🌇 **Sunset (utc)**", value=sunset, inline=True)
        embed.set_footer(text="Powered by http://openweathermap.org")
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    n = weather(bot)
    bot.add_cog(n)
