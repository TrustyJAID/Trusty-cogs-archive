import discord
import time
from discord.ext import commands
from random import choice, randint
import asyncio
from .utils import checks
from .utils import dataIO
from .utils.dataIO import fileIO
from .utils.dataIO import dataIO
import os
import time

class Rainbow:
    """Rainbows the selected role"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/rainbow/settings.json"
        self.settings = dataIO.load_json(self.settings_file)

    @commands.group(pass_context=True, name='rainbow')
    @checks.admin_or_permissions(manage_roles=True)
    async def _rainbow(self, ctx):
        """Command for setting required access information for the API"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_rainbow.command(pass_context = True, name="interval")
    async def _interval(self, ctx, interval:float):
        if interval < 120.0 and interval > 500.0:
            await self.bot.say("Please choose an interval between 120 and 500 seconds.")
            return
        self.settings["delay"] = interval
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say("Rainbow interval set to {}".format(interval))


    @_rainbow.command(pass_context = True, name="add")
    async def _addrainbow(self, ctx, *, role: discord.Role):
        server_id = ctx.message.server.id
        if server_id in self.settings["servers"]:
            if role.id in self.settings["servers"][server_id]:
                await self.bot.say("That role is already rainbow!")
                return
            self.settings["servers"][server_id].append(role.id)
        else:
            self.settings["servers"][server_id] = [role.id]
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say("{} role set to rainbow!".format(role.mention))

    @_rainbow.command(pass_context = True, name="stop")
    async def _stoprainbow(self, ctx):
        server_id = ctx.message.server.id
        if server_id in self.settings["servers"]:
            del self.settings["servers"][server_id]
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say("Rainbow roles removed")
    
    async def get_role_obj(self, id_list, server):
        role = []
        for role_id in id_list:
            try:
                for roles in server.roles:
                    if roles.id == role_id:
                        role.append(roles)
            except AttributeError:
                print("There was a role colour change error!")
        return role
    
    async def change_colours(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Rainbow"):
            for server_id in self.settings["servers"]:
                server = self.bot.get_server(id=server_id)
                roles = await self.get_role_obj(self.settings["servers"][server_id], server)
                for role in roles:
                    colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
                    colour = int(colour, 16)
                    await self.bot.edit_role(server, role, colour=discord.Colour(value=colour))
            # print("Roles updated!")
            await asyncio.sleep(self.settings["delay"])
    

def check_folders():
    if not os.path.exists("data/rainbow"):
        print("Creating data/rainbow folder...")
        os.makedirs("data/rainbow")

def check_files():
    settings = {"delay" : 300, "servers": {}}
    f = "data/rainbow/settings.json"
    if not fileIO(f, "check"):
        print("Creating empty settings.json...")
        dataIO.save_json(f, settings)


def setup(bot):
    check_folders()
    check_files()
    n = Rainbow(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.change_colours())
    bot.add_cog(n)
