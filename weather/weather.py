import discord
from redbot.core import commands
from redbot.core import Config
from random import randint
from random import choice
from enum import Enum
import json
import datetime
import aiohttp
import asyncio

class Weather(getattr(commands, "Cog", object)):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 138475464)
        default = {"units":"imperial"}
        self.config.register_guild(**default)
        self.config.register_user(**default)
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": "°F"},
            "metric": {"code": ["m", "c"], "speed": "km/h", "temp": "°C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/h", "temp": "°K"}}

    @commands.command(pass_context=True, name="weather", aliases=["we"])
    async def weather(self, ctx, *, location):
        await ctx.trigger_typing()
        await self.getweather(ctx, location)

    @commands.group(pass_context=True, name="weatherset")
    async def weather_set(self, ctx):
        """Set user or guild default units"""
        pass
    @weather_set.command(pass_context=True, name="guild")
    async def set_guild(self, ctx, units):
        """Sets the guild default weather units use imperial, metric, or kelvin"""
        guild = ctx.message.guild
        if units in self.unit:
            await self.config.guild(guild).units.set(units)
            await ctx.send("Default units set to {} in {}.".format(units, guild.name))

    @weather_set.command(pass_context=True, name="user")
    async def set_user(self, ctx, units):
        """Sets the user default weather units use imperial, metric, or kelvin"""
        author = ctx.message.author
        if units in self.unit:
            await self.config.user(author).units.set(units)
            await ctx.send("Default units set to {} in {}.".format(units, author.name))

    async def getweather(self, ctx, location):
        guild = ctx.message.guild
        author = ctx.message.author
        guild_units = await self.config.guild(guild).units()
        user_units = await self.config.user(author).units()
        units = "imperial"
        if guild_units != "imperial" and guild_units != user_units:
            units = guild_units
        if user_units != "imperial" and user_units != guild_units:
            units = user_units
        
        if units == "kelvin":
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units=metric".format(location)
        else:
            url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units={1}".format(location, units)
        async with self.session.get(url) as resp:
            data = await resp.json()
        try:
            if data["message"] == "city not found":
                await ctx.send("City not found.")
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
        embed.add_field(name="🌄 **Sunrise (UTC)**", value=sunrise)
        embed.add_field(name="🌇 **Sunset (UTC)**", value=sunset)
        embed.set_footer(text="Powered by https://openweathermap.org")
        await ctx.send(embed=embed)

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
