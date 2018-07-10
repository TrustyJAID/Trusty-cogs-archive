from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO
import os
import aiohttp
import discord

try:
    import chatterbot
    from chatterbot.trainers import ListTrainer
    chatt = True
except:
    chatt = False

class Chatterbot():
    """Chatterbot"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/chatterbot/settings.json")
        self.log = dataIO.load_json("data/chatterbot/log.json")
        self.chatbot = chatterbot.ChatBot("redbot", 
                                          storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
                                          # database="data/chatterbot/db",
                                          logic_adapters=[
                                          "chatterbot.logic.BestMatch",
                                          "chatterbot.logic.TimeLogicAdapter",
                                          "chatterbot.logic.MathematicalEvaluation"]
                                          )
        self.chatbot.set_trainer(ListTrainer)

    @commands.group(no_pm=True, invoke_without_command=True, pass_context=True)
    async def chatterbot(self, ctx, *, message):
        """Talk with cleverbot"""
        author = ctx.message.author
        channel = ctx.message.channel
        response = self.chatbot.get_response(message)
        await self.bot.send_message(channel, response)

    @chatterbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def toggle(self, ctx):
        """Toggles reply on mention"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" : True, "channel":""}
        self.settings[server.id]["TOGGLE"] = not self.settings["TOGGLE"]
        if self.settings[server.id]["TOGGLE"]:
            await self.bot.say("I will reply on mention.")
        else:
            await self.bot.say("I won't reply on mention anymore.")
        dataIO.save_json("data/chatterbot/settings.json", self.settings)
    
    @chatterbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.Channel):
        """Toggles channel for automatic replies"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" :False, "channel":""}
        self.settings[server.id]["channel"] = channel.id
        await self.bot.say("I will reply in {}".format(channel))
        dataIO.save_json("data/chatterbot/settings.json", self.settings)

    async def on_message(self, message):
        server = message.server
        channel = message.channel
        author = message.author
        conversation = []
        if "http" in message.content or message.content == "" or author.bot:
            return
        if server.id not in self.log:
            self.log[server.id] = {}
            self.log[server.id][channel.id] = {"author":author.id,"message":message.content}
            dataIO.save_json("data/chatterbot/log.json", self.log)
        if channel.id not in self.log[server.id]:
            self.log[server.id][channel.id] = {"author":author.id,"message":message.content}
            dataIO.save_json("data/chatterbot/log.json", self.log)
        last_author = self.log[server.id][channel.id]["author"]
        last_message = self.log[server.id][channel.id]["message"]
        if author.id == last_author and last_message != message.content:
            self.log[server.id][channel.id]["message"] = message.content
            dataIO.save_json("data/chatterbot/log.json", self.log)
        if author.id != last_author and author.id != self.bot.user.id:
            self.log[server.id][channel.id]["message"] = message.content
            self.log[server.id][channel.id]["author"] = author.id
            dataIO.save_json("data/chatterbot/log.json", self.log)
            conversation.append(message.content)
            conversation.append(last_message)
            self.chatbot.train(conversation)
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" :True, "channel":""}
            dataIO.save_json("data/chatterbot/settings.json", self.settings)
        if not self.settings[server.id]["TOGGLE"] or message.server is None:
            return
        if not self.bot.user_allowed(message):
            return

        if author.id != self.bot.user.id:
            to_strip = "@" + author.server.me.display_name + " "
            text = message.clean_content
            if not text.startswith(to_strip) and message.channel.id != self.settings[server.id]["channel"]:
                return
            text = text.replace(to_strip, "", 1)
            await self.bot.send_typing(channel)
            response = self.chatbot.get_response(text)
            await self.bot.send_message(message.channel, response)



def check_folders():
    if not os.path.exists("data/chatterbot"):
        print("Creating data/chatterbot folder...")
        os.makedirs("data/chatterbot")
    if not os.path.exists("data/chatterbot/db"):
        os.makedirs("data/chatterbot/db")


def check_files():
    f = "data/chatterbot/settings.json"
    data = {}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)
    log = "data/chatterbot/log.json"
    data = {}
    if not dataIO.is_valid_json(log):
        dataIO.save_json(log, data)

def setup(bot):
    check_folders()
    check_files()
    if not chatt:
        bot.pip_install("chatterbot")
        import chatterbot
        from chatterbot.trainers import ListTrainer
    bot.add_cog(Chatterbot(bot))