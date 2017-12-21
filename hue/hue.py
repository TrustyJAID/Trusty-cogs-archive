from discord.ext import commands
import discord
from redbot.core import Config
from redbot.core import checks
import random
from phue import Bridge



class Hue():

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 3569979897)
        default_global = {"ip": None}
        self.config.register_global(**default_global)
        self.bridge = Bridge(await self.config.ip())
        self.lights = self.bridge.lights

    @commands.group(pass_context=True, name="hue")
    @checks.is_owner()
    async def _hue(self, ctx):
        """Commands for interacting with Hue lights"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @_hue.command(name="connect")
    async def hue_connect(self):
        """Setup command if bridge cannot connect"""
        self.bridge.connect()

    @_hue.command(pass_context=True, name="set")
    async def hue_setup(self, ctx, ip):
        """Set the IP address of the hue bridge"""
        await self.config.ip.set(ip)
        self.bridge = Bridge(await self.config.ip())
        self.lights = self.bridge.lights

    @_hue.command(pass_context=True, name="check")
    async def check_api(self, ctx):
        """Gets light data from bridge and prints to terminal"""
        print(self.bridge.get_api())

    async def max_min_check(self, value, max, min):
        if value > max:
            return max
        if value < min:
            return min
        else:
            return value

    @_hue.command(pass_context=True, name="brightness")
    async def brightness_set(self, ctx, brightness:int=254, *, name=None):
        """Sets the brightness for lights"""
        brightness = await self.max_min_check(brightness, 254, 0)
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.brightness = brightness

    @_hue.command(pass_context=True, name="temp", aliases=["ct", "colourtemp", "temperature"])
    async def colourtemp_set(self, ctx, ct:int=500, *, name=None):
        """Sets the colour temperature for lights"""
        ct = await self.max_min_check(ct, 600, 154)
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.colortemp = ct

    @_hue.command(pass_context=True, name="hue")
    async def hue_set(self, ctx, hue:int=25000, *, name=None):
        """Sets the hue for lights"""
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.hue = hue

    @_hue.command(pass_context=True, name="saturation", aliases=["sat"])
    async def saturation_set(self, ctx, saturation:int=254, *, name=None):
        """Sets the saturation for lights"""
        saturation = await self.max_min_check(saturation, 254, 0)
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.saturation = saturation

    @_hue.command(pass_context=True, name="random")
    async def hue_random_colour(self, ctx, *, name=None):
        """Sets the light to a random colour"""
        colours = [random.random(), random.random()]
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.xy = colours

    @_hue.command(pass_context=True, name="colourloop", aliases=["cl"])
    async def hue_colourloop(self, ctx, *, name=None):
        """Toggles the light on colour looping all colours"""
        for light in self.lights:
            if name is None or light.name.lower() == name.lower():
                if light.effect != "colorloop" and light.on:
                    light.effect = "colorloop"
                    continue
                if light.effect == "colorloop" and light.on:
                    light.effect = "none"
                    continue

    @_hue.group(pass_context=True, name="colour")
    async def _colour(self, ctx):
        """Sets the colour for lights"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    async def rgb_to_xy(self, red:float, green:float, blue:float):
        X = 0.4124*red + 0.3576*green + 0.1805*blue
        Y = 0.2126*red + 0.7152*green + 0.0722*blue
        Z = 0.0193*red + 0.1192*green + 0.9505*blue
        try:
            x = X / (X + Y + Z)
            y = Y / (X + Y + Z)
        except ZeroDivisionError:
            x = 1.0
            y = 1.0
        return x, y

    @_colour.command(pass_context=True, name="rgb")
    async def hue_colour_rgb(self, ctx, red:float, green:float, blue:float, *, name=None):
        """Sets the colour using RGB colour coordinates"""
        x, y = await self.rgb_to_xy(red, green, blue)
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.xy = [x, y]

    @_colour.command(pass_context=True, name="xy", aliases=["xyz"])
    async def hue_colour_xy(self, ctx, x:float, y:float, *, name=None):
        """Sets the colour using RGB colour coordinates"""
        if x > 1.0 or x < 0.0:
            x = 1.0
        if y > 1.0 or y < 0.0:
            y = 1.0
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.xy = [x, y]

    @_colour.command(pass_context=True, name="hex")
    async def hue_colour_hex(self, ctx, hex, *, name=None):
        """Sets the colour using hex codes"""
        if "#" in hex:
            hex.replace("#", "")
        r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2 ,4))
        x, y = await self.rgb_to_xy(r, g, b)
        for light in self.lights:
            if name is None or light.name.lower() == name.lower() and light.on:
                light.xy = [x, y]

    @_hue.command(pass_context=True, name="test")
    async def hue_test(self, ctx, cl1:float, cl2:float):
        """Testing function"""
        for light in self.lights:
            light.xy = [cl1, cl2]

    @_hue.command(pass_context=True, name="switch")
    async def hue_switch(self, ctx, *, name=None):
        """Toggles lights on or off"""
        for light in self.lights:
            if name is None or light.name.lower() == name.lower():
                if light.on:
                    light.on = False
                    continue
                if not light.on:
                    light.on = True
                    continue

    @_hue.command(pass_context=True, name="off")
    async def turn_off(self, ctx, *, name=None):
        """Turns off light"""
        for light in self.lights:
            if name is None or light.name.lower() == name.lower():
                light.on = False

    @_hue.command(pass_context=True, name="on")
    async def turn_on(self, ctx, name=None):
        """Turns on Light"""
        for light in self.lights:
            if name is None or light.name.lower() == name.lower():
                light.on = True
