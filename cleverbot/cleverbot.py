from discord.ext import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import bundled_data_path
import os
import aiohttp
import discord

API_URL = "https://www.cleverbot.com/getreply"


class CleverbotError(Exception):
    pass

class NoCredentials(CleverbotError):
    pass

class InvalidCredentials(CleverbotError):
    pass

class APIError(CleverbotError):
    pass

class OutOfRequests(CleverbotError):
    pass

class OutdatedCredentials(CleverbotError):
    pass


class Cleverbot():
    """Cleverbot"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 127486454786)
        default_global = {"api":None}
        default_guild = {"channel":None, "toggle":False}
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.instances = {}
        self.food = {"sandwich": "/sandwich.jpg", 
                     "asada": "/asada.jpg",
                     "asado": "/asado.jpg",
                     "sushi": "/sushi.jpg",
                     "chicken": "/chicken.jpg"}

    @commands.group(no_pm=True, invoke_without_command=True, pass_context=True)
    async def cleverbot(self, ctx, *, message):
        """Talk with cleverbot"""
        author = ctx.message.author
        channel = ctx.message.channel
        try:
            result = await self.get_response(author, message)
        except NoCredentials:
            await ctx.send("The owner needs to set the credentials first.\n"
                                                 "See: `[p]cleverbot apikey`")
        except APIError:
            await ctx.send("Error contacting the API.")
        except InvalidCredentials:
            await ctx.send("The token that has been set is not valid.\n"
                                                 "See: `[p]cleverbot apikey`")
        except OutOfRequests:
            await ctx.send("You have ran out of requests for this month. "
                                                 "The free tier has a 5000 requests a month limit.")
        except OutdatedCredentials:
            await ctx.send("You need a valid cleverbot.com api key for this to "
                                                 "work. The old cleverbot.io service will soon be no "
                                                 "longer active. See `[p]help cleverbot apikey`")
        else:
            await ctx.send(result)

    @cleverbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def toggle(self, ctx):
        """Toggles reply on mention"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).toggle():
            await self.config.guild(guild).toggle.set(True)
            await ctx.send("I will reply on mention.")
        else:
            await self.config.guild(guild).toggle.set(False)
            await ctx.send("I won't reply on mention anymore.")
    
    @cleverbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.TextChannel=None):
        """Toggles channel for automatic replies"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        await self.config.guild(guild).channel.set(channel.id)
        await ctx.send("I will reply in {}".format(channel))

    @cleverbot.command()
    @checks.is_owner()
    async def apikey(self, ctx, key: str):
        """Sets token to be used with cleverbot.com
        You can get it from https://www.cleverbot.com/api/
        Use this command in direct message to keep your
        token secret"""
        await self.config.api.set(key)
        await ctx.send("Credentials set.")

    async def get_response(self, author, text):
        payload = {}
        payload["key"] = await self.get_credentials()
        payload["cs"] = self.instances.get(str(author.id), "")
        payload["input"] = text
        session = aiohttp.ClientSession()

        async with session.get(API_URL, params=payload) as r:
            if r.status == 200:
                data = await r.json()
                self.instances[str(author.id)] = data["cs"] # Preserves conversation status
            elif r.status == 401:
                raise InvalidCredentials()
            elif r.status == 503:
                raise OutOfRequests()
            else:
                raise APIError()
        await session.close()
        return data["output"]

    async def get_credentials(self):
        key = await self.config.api()
        if key is None:
            raise NoCredentials()
        else:
            return key

    async def on_message(self, message):
        guild = message.guild
        author = message.author
        channel = message.channel
        if not hasattr(author, "guild"):
            return

        if message.author.id != self.bot.user.id:
            to_strip = "@" + author.guild.me.display_name + " "
            text = message.clean_content
            if not text.startswith(to_strip) and message.channel.id != await self.config.guild(guild).channel():
                return
            if str(author.guild.me.id) not in message.content:
                return
            text = text.replace(to_strip, "", 1)
            if "make me" in text.lower() and "sudo" not in text.lower():
                food = text.lower().split(" ")[-1]
                if food in self.food:
                    await channel.trigger_typing()
                    await channel.send("Make your own {}!".format(food))
                    return
            if "sudo make me" in text.lower():
                food = text.lower().split(" ")[-1]
                if food in self.food:
                    if "chicken" in text.lower():
                        await channel.trigger_typing()
                        file = discord.File(str(bundled_data_path(self)) + self.food["chicken"])
                        await channel.send("OK, OK, here's your damn chicken {}!".format(food), file=file)
                        return
                    else:
                        await channel.trigger_typing()
                        file = discord.File(str(bundled_data_path(self)) + self.food[food])
                        await channel.send("OK, OK, here's your damn {}!".format(food), file=file)
                        return
            if text.lower() == "what is your real name?":
                await channel.trigger_typing()
                await channel.send("I'm OpSec. Duh!")
                return
            await channel.trigger_typing()
            try:
                response = await self.get_response(author, text)
            except NoCredentials:
                await channel.send("The owner needs to set the credentials first.\n"
                                                     "See: `[p]cleverbot apikey`")
            except APIError:
                await channel.send("Error contacting the API.")
            except InvalidCredentials:
                await channel.send("The token that has been set is not valid.\n"
                                                     "See: `[p]cleverbot apikey`")
            except OutOfRequests:
                await channel.send("You have ran out of requests for this month. "
                                                     "The free tier has a 5000 requests a month limit.")
            except OutdatedCredentials:
                await channel.send("You need a valid cleverbot.com api key for this to "
                                                     "work. The old cleverbot.io service will soon be no "
                                                     "longer active. See `[p]help cleverbot apikey`")
            else:
                await channel.send(response)
