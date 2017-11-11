from discord.ext import commands
from redbot.core import checks
from redbot.core import Config
import aiohttp
import discord
import chatterbot
from chatterbot.trainers import ListTrainer


class Chatter():
    """Chatterbot"""

    def __init__(self, bot):
        self.bot = bot
        default_guild = {"toggle": True, "channel": None}
        default_channel = {"message": None, "author": None}
        self.config = Config.get_conf(self, 3568777796)
        self.config.register_guild(**default_guild)
        self.config.register_channel(**default_channel)
        self.chatbot = chatterbot.ChatBot("TrustyBot", 
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
        await ctx.send(response)

    @chatterbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def toggle(self, ctx):
        """Toggles reply on mention"""
        guild = ctx.message.guild
        cur_toggle = await self.config.guild(guild).toggle()
        await self.config.guild(guild).toggle.set(not cur_toggle)
        if cur_toggle:
            await ctx.send("I won't reply on mention anymore.")
        else:
            await ctx.send("I will reply on mention.")
    
    @chatterbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        """Toggles channel for automatic replies"""
        guild = ctx.message.guild
        await self.config.guild(guild).channel.set(channel.id)
        await self.bot.say("I will reply in {}".format(channel.mention))

    async def on_message(self, message):
        guild = message.guild
        channel = message.channel
        author = message.author
        conversation = []
        if "http" in message.content or message.content == "" or author.bot:
            return
        last_author = await self.config.channel(channel).message()
        last_message = await self.config.channel(channel).author()
        if author.id == last_author and last_message != message.content:
            await self.config.channel(channl).message.set(message.content)
        if author.id != last_author and author.id != self.bot.user.id and last_author is not None:
            conversation.append(message.content)
            conversation.append(last_message)
            self.chatbot.train(conversation)
            await self.config.channel(channel).message.set(None)
            await self.config.channel(channel).author.set(None)
        if last_author is None and last_message is None:
            await self.config.channel(channel).message.set(message.content)
            await self.config.channel(channel).author.set(author.id)
        if not await self.config.guild(guild).toggle() or message.guild is None:
            return

        if author.id != self.bot.user.id:
            to_strip = "@" + author.guild.me.display_name + " "
            text = message.clean_content
            if not text.startswith(to_strip) and message.channel.id != await self.config.guild(guild).channel():
                return
            text = text.replace(to_strip, "", 1)
            await channel.trigger_typing()
            response = self.chatbot.get_response(text)
            await message.channel.send(response)
