import aiohttp
import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import os

'''Translator cog 

Cog credit to aziz#5919 for the idea and 
 
Links

Wiki                                                https://goo.gl/3fxjSA
Github                                              https://goo.gl/oQAQde
Support the developer                               https://goo.gl/Brchj4
Invite the bot to your server                       https://goo.gl/aQm2G7
Join the official development server                https://discord.gg/uekTNPj
'''


class Translate:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://translation.googleapis.com"
        self.settings = dataIO.load_json("data/google/settings.json")
        self.languages = dataIO.load_json("data/google/flags.json")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def addflag(self, ctx, flag_1, flag_2=None):
        """Sets a custom flag to another flag"""
        new_data = []
        if flag_2 is not None:
            new_data = self.languages[flag_2]
        if flag_1 not in self.languages:
            self.languages[flag_1] = new_data
            dataIO.save_json("data/google/flags.json", self.languages)
        else:
            await self.bot.say("{} is already in the list!".format(flag_1))

    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, message):
        if self.settings["key"] is None:
            await self.bot.say("The bot owner needs to set an api key first!")
            return
        if to_language in self.languages:
            language_code = self.languages[to_language]["code"]
        else:
            try:
                language_code = [self.languages[lang]["code"] for lang in self.languages if (self.languages[lang]["name"].lower() in to_language.lower()) or (self.languages[lang]["country"].lower() in to_language.lower())][0]
            except IndexError:
                await self.bot.say("{} is not an available language!".format(to_language))
                return
        
        from_lang = await self.detect_language(message)
        translated_text = await self.translate_text(from_lang[0][0]["language"], language_code, message)
        author = ctx.message.author
        em = discord.Embed(colour=author.top_role.colour, description=translated_text)
        em.set_author(name=author.display_name, icon_url=author.avatar_url)
        em.set_footer(text="{} to {}".format(from_lang[0][0]["language"].upper(), language_code.upper()))
        await self.bot.send_message(ctx.message.channel, embed=em)

    async def detect_language(self, text):
        async with self.session.get(self.url + "/language/translate/v2/detect", params={"q":text, "key":self.settings["key"]}) as resp:
                data = await resp.json()
        return data["data"]["detections"]


    async def translate_text(self, from_lang, target, text):
        formatting = "text"
        params = {"q":text, "target":target,"key":self.settings["key"], "format":formatting, "source":from_lang}
        try:
            async with self.session.get(self.url + "/language/translate/v2", params=params) as resp:
                data = await resp.json()
        except:
            return None, None
        translated_text = data["data"]["translations"][0]["translatedText"]
        
        return translated_text

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def translatereact(self, ctx):
        """Set the bot to post reaction flags to translate messages on this server"""
        server = ctx.message.server
        if "servers" not in self.settings:
            self.settings["servers"] = []
        if server.id not in self.settings["servers"]:
            self.settings["servers"].append(server.id)
            await self.bot.say("{} has been added to post translated responses!".format(server.name))
        elif server.id in self.settings["servers"]:
            self.settings["servers"].remove(server.id)
            await self.bot.say("{} has been removed from translated responses!".format(server.name))
        dataIO.save_json("data/google/settings.json", self.settings)


    async def on_reaction_add(self, reaction, user):
        """Translates the message based off the flag added"""
        if self.settings["key"] is None:
            return
        if reaction.emoji not in self.languages:
            return
        if reaction.message.channel.server.id not in self.settings["servers"]:
            return
        if reaction.message.embeds != []:
            to_translate = reaction.message.embeds[0]["description"]
        else:
            to_translate = reaction.message.clean_content    
        target = self.languages[reaction.emoji]["code"]
        from_lang = await self.detect_language(to_translate)
        translated_text = await self.translate_text(from_lang[0][0]["language"], target, to_translate)
        author = reaction.message.author
        em = discord.Embed(colour=author.top_role.colour, description=translated_text)
        em.set_author(name=author.display_name, icon_url=author.avatar_url)
        em.set_footer(text="{} to {}".format(from_lang[0][0]["language"].upper(), target.upper()))
        await self.bot.send_message(reaction.message.channel, embed=em)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def translateset(self, ctx, api_key):
        """You must get an API key from google to set this up
        https://console.cloud.google.com/apis/library/translate.googleapis.com/?q=translate&id=c22f20ba-6a29-40ae-9084-8bc264a97fc2&project=dameznet-158219
        """
        self.settings["key"] = api_key
        dataIO.save_json("data/google/settings.json", self.settings)
        await self.bot.say("API key set.")

def check_folder():
    if not os.path.exists("data/google"):
        print("Creating data/google folder")
        os.makedirs("data/google")

def check_file():
    data = {"key": None}
    f = "data/google/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Translate(bot))