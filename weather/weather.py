import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
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
import os



class weather:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/weather/settings.json")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": "°F"},
            "metric": {"code": ["m", "c"], "speed": "km/h", "temp": "°C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/h", "temp": "°K"}}

    @commands.command(pass_context=True, name="weather", aliases=["we"])
    async def weather(self, ctx, *, location):
        await self.bot.send_typing(ctx.message.channel)
        await self.getweather(ctx, location)

    @commands.group(pass_context=True, name="weatherset")
    async def weather_set(self, ctx):
        """Set user or server default units"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @weather_set.command(pass_context=True, name="server")
    async def set_server(self, ctx, units):
        """Sets the server default weather units use imperial, metric, or kelvin"""
        server = ctx.message.server
        if units in self.unit:
            self.settings["server"][server.id] = units
            dataIO.save_json("data/weather/settings.json", self.settings)
            await self.bot.send_message(ctx.message.channel, "Default units set to {} in {}.".format(units, server.name))

    @weather_set.command(pass_context=True, name="user")
    async def set_user(self, ctx, units):
        """Sets the user default weather units use imperial, metric, or kelvin"""
        author = ctx.message.author
        if units in self.unit:
            self.settings["user"][author.id] = units
            dataIO.save_json("data/weather/settings.json", self.settings)
            await self.bot.send_message(ctx.message.channel, "Default units set to {} in {}.".format(units, author.name))

    async def getweather(self, ctx, location):
        server = ctx.message.server
        author = ctx.message.author
        if server is not None:
            if server.id in self.settings["server"]:
                units = self.settings["server"][server.id]
        if author.id in self.settings["user"]:
            units = self.settings["user"][author.id]
        else:
            units = "imperial"
        if units == "kelvin":
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units=metric".format(location)
        else:
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units={1}".format(location, units)
        async with self.session.get(url) as resp:
            data = await resp.json()
        try:
            if data["message"] == "city not found":
                await self.bot.send_message(ctx.message.channel, "City not found.")
                return
        except:
            pass
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

def check_folder():
    if not os.path.exists("data/weather"):
        print("Creating data/weather folder")
        os.makedirs("data/weather")

def check_file():
    data = {"server":{}, "user":{}}
    f = "data/weather/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    n = weather(bot)
    bot.add_cog(n)
