import discord
from discord.ext import commands
import datetime
import aiohttp
import asyncio


class Weather:

    def __init__(self, bot):
        self.bot = bot
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": "°F"},
            "metric": {"code": ["m", "c"], "speed": "km/s", "temp": "°C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/s", "temp": "°K"}}
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "http://api.openweathermap.org/data/2.5/weather?q={0}&appid=88660f6af079866a3ef50f491082c386&units={1}"

    @commands.command(pass_context=True, name="weather", aliases=["we"])
    async def weather(self, ctx, location, units="imperial"):
        await ctx.trigger_typing()
        await self.getweather(ctx, location, units)

    async def getweather(self, ctx, location, units="imperial"):
        for key, value in self.unit.items():
            if units.lower() in value["code"] or units.lower() == key:
                units = key
        if units == "kelvin":
            url = self.url.format(location, "metric")
        else:
            url = self.url.format(location, units)
        async with self.session.get(url) as resp:
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
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)



