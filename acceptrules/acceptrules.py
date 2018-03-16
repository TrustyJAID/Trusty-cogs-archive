import discord
import asyncio
from sys import argv
from discord.ext import commands
from .utils.dataIO import dataIO
import os


class AcceptRules:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/acceptrules/settings.json")
    
    def getroles(self, ctx, role):
        return {r.name: r for r in ctx}[role]
    
    def savefile(self):
        dataIO.save_json("data/acceptrules/settings.json", self.settings)
    
    @commands.group(pass_context=True)
    async def rules(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @rules.command(pass_context=True, name="set")
    async def _set(self, ctx, channel:discord.Channel=None, role:discord.Role=None):
        """Setup the rules channel and role to be applied"""
        if channel is None:
            channel = ctx.message.channel
        self.settings[ctx.message.server.id] = {"rules": "Welcome! Please react with 🇾 to accept the rules.", "channel": channel.id,
        "role": ""}
        self.savefile()
        await self.bot.say("Rules set to {} in channel {} applying role {}".format(self.settings[ctx.message.server.id]["rules"], channel.mention, role))


    
    @rules.command(pass_context=True)
    async def channel(self, ctx, channel : discord.Channel):
        server = ctx.message.server
        if server.id not in self.settings:
            await self.bot.say("Please use the rules set command to change the rules message")
            return
        self.settings[ctx.message.server.id]["channel"] = channel.id
        await self.bot.say("Channel changed to {}".format(channel.mention))
        self.savefile()
    
    @rules.command(pass_context=True)
    async def change(self, ctx, *, message):
        if ctx.message.server.id not in self.settings:
            await self.bot.say("Please use the rules set command to change the rules message")
            return
        self.settings[ctx.message.server.id]["rules"] = message
        await self.bot.say("Message changed to {}".format(message))
        self.savefile()
        
    @rules.command(pass_context=True)
    async def role(self, ctx, role):
        try:
            serverrole = self.getroles(ctx.message.server.roles, role)
            self.settings[ctx.message.server.id]["role"] = role
            await self.bot.say("Role changed to {}".format(role))
            self.savefile()
        except KeyError:
            await self.bot.say("The {} role does not exist, make sure it's spelled correctly and exists!".format(role))


    async def on_member_join(self, member):
        server = member.server
        if server.id not in self.settings:
            return
        channel = discord.Object(id=self.settings[server.id]["channel"])
        message = await self.bot.send_message(channel, "{} {}".format(member.mention, self.settings[server.id]["rules"]))
        role = self.settings[server.id]["role"]
        await self.bot.add_reaction(message, "🇾")
        await self.bot.add_reaction(message, "🇳")
        answer = await self.bot.wait_for_reaction(emoji=["🇾", "🇳"], user=member, message=message)
        if answer.reaction.emoji == "🇾":
            await self.bot.add_roles(member, self.getroles(server.roles, role))
            await self.bot.delete_message(message)
        if answer.reaction.emoji == "🇳":
            await self.bot.kick(member)
            await self.bot.delete_message(message)
            
def check_folder():
    if not os.path.exists("data/acceptrules"):
        print("Creating data/acceptrules folder")
        os.makedirs("data/acceptrules")


def check_file():
    data = {}
    f = "data/acceptrules/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_file()
    n = AcceptRules(bot)
    bot.add_cog(n)

