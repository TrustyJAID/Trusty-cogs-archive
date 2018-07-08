import discord
from discord.ext import commands
from .utils.chat_formatting import box
from .utils.dataIO import dataIO
from .utils import checks
import os

class ServerWhitelist:

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/serverwhitelist/settings.json"
        self.settings = dataIO.load_json(self.settings_file)

    @commands.group(pass_context=True, name="serverwhitelist", aliases=["serverwhitelist"])
    async def serverwhitelist(self, ctx):
        """Add or remove servers to the bots approved server list"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @serverwhitelist.command(pass_context=True, aliases=["set"])
    async def add(self, ctx, server_id:int):
        """Add a server to the bots approved server list."""
        if server_id in self.settings["whitelist"]:
            await self.bot.send_message(ctx.message.channel, "{} is already in the whitelist.".format(server_id))
            return
        self.settings["whitelist"].append(str(server_id))
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "{} server has been added to the whitelist.".format(server_id))


    @serverwhitelist.command(pass_context=True)
    async def remove(self, ctx, server_id:int):
        """Removes a server from the bots approved server list."""
        if server_id not in self.settings["whitelist"]:
            await self.bot.send_message(ctx.message.channel, "{} is not in the whitelist.".format(server_id))
            return
        self.settings["whitelist"].remove(str(server_id))
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "{} server has been removed the whitelist.".format(server_id))

    async def on_server_join(self, server):
        """Checks if a joined server is in the bots approved server list and leaves if it isn't."""
        if server.id not in self.settings["whitelist"]:
            await self.bot.leave_server(server)

def check_folder():
    if not os.path.exists("data/serverwhitelist"):
        print("Creating data/serverwhitelist folder")
        os.makedirs("data/serverwhitelist")


def check_file():
    data = {"whitelist":[]}
    f = "data/serverwhitelist/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    n = ServerWhitelist(bot)
    bot.add_cog(n)


