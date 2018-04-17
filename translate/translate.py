import aiohttp
import discord
from discord.ext import commands
from redbot.core import Config
from redbot.core import checks
from redbot.core.data_manager import bundled_data_path
import json
from .flags import flags

'''Translator cog 

Cog credit to aziz#5919 for the idea and 
 
Links

Wiki                                                https://goo.gl/3fxjSA
Github                                              https://goo.gl/oQAQde
Support the developer                               https://goo.gl/Brchj4
Invite the bot to your guild                       https://goo.gl/aQm2G7
Join the official development guild                https://discord.gg/uekTNPj
'''


class Translate:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://translation.googleapis.com"
        self.config = Config.get_conf(self, 156434873547)
        default_guild = {"enabled":False}
        default = {"api_key":None}
        self.config.register_guild(**default_guild)
        self.config.register_global(**default)
        # with open(str(cog_data_path(self) + "/flags.json"), "r") as file:
            # self.flags = json.loads(file.read())
        self.flags = flags
        # self.settings = dataIO.load_json("data/translate/settings.json")

    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, message):
        if await self.config.api_key() is None:
            await ctx.send("The bot owner needs to set an api key first!")
            return
        if to_language in self.flags:
            language_code = self.flags[to_language]["code"]
        else:
            try:
                language_code = [self.flags[lang]["code"] for lang in self.flags if (self.flags[lang]["name"].lower() in to_language.lower()) or (self.flags[lang]["country"].lower() in to_language.lower())][0]
            except IndexError:
                await ctx.send("{} is not an available language!".format(to_language))
                return
        
        from_lang = await self.detect_language(message)
        translated_text = await self.translate_text(from_lang[0][0]["language"], language_code, message)
        author = ctx.message.author
        em = discord.Embed(colour=author.top_role.colour, description=translated_text)
        em.set_author(name=author.display_name, icon_url=author.avatar_url)
        em.set_footer(text="{} to {}".format(from_lang[0][0]["language"].upper(), language_code.upper()))
        await ctx.send(embed=em)

    async def detect_language(self, text):
        async with self.session.get(self.url + "/language/translate/v2/detect", params={"q":text, "key":await self.config.api_key()}) as resp:
                data = await resp.json()
        return data["data"]["detections"]


    async def translate_text(self, from_lang, target, text):
        formatting = "text"
        params = {"q":text, "target":target,"key":await self.config.api_key(), "format":formatting, "source":from_lang}
        try:
            async with self.session.get(self.url + "/language/translate/v2", params=params) as resp:
                data = await resp.json()
        except:
            return None
        if "data" in data:
            translated_text = data["data"]["translations"][0]["translatedText"]
            return translated_text

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def translatereact(self, ctx):
        """Set the bot to post reaction self.flags to translate messages on this guild"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await self.config.guild(guild).enabled.set(True)
            await ctx.send("{} has been added to post translated responses!".format(guild.name))
        elif await self.config.guild(guild).enabled():
            await self.config.guild(guild).enabled.set(False)
            await ctx.send("{} has been removed from translated responses!".format(guild.name))

    async def on_raw_reaction_add(self, payload):
        """Translates the message based off the flag added"""
        channel = self.bot.get_channel(id=payload.channel_id)
        try:
            guild = channel.guild
            message = await channel.get_message(id=payload.message_id)
        except:
            return
        if await self.config.api_key() is None:
            return
        # check_emoji = lambda emoji: emoji in self.flags
        if str(payload.emoji) not in self.flags:
            return
        if not await self.config.guild(guild).enabled():
            return
        if message.embeds != []:
            to_translate = message.embeds[0].description
        else:
            to_translate = message.clean_content
        num_emojis = 0
        for reaction in message.reactions:
            if reaction.emoji == str(payload.emoji):
                num_emojis = reaction.count
        if num_emojis > 1:
            return
        target = self.flags[str(payload.emoji)]["code"]
        from_lang = await self.detect_language(to_translate)
        translated_text = await self.translate_text(from_lang[0][0]["language"], target, to_translate)
        author = message.author
        em = discord.Embed(colour=author.top_role.colour, description=translated_text)
        em.set_author(name=author.display_name, icon_url=author.avatar_url)
        em.set_footer(text="{} to {}".format(from_lang[0][0]["language"].upper(), target.upper()))
        await channel.send(embed=em)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def translateset(self, ctx, api_key):
        """You must get an API key from google to set this up
        https://console.cloud.google.com/apis/library/translate.googleapis.com/?q=translate&id=c22f20ba-6a29-40ae-9084-8bc264a97fc2&project=dameznet-158219
        """
        await self.config.api_key.set(api_key)
        await ctx.send("API key set.")
