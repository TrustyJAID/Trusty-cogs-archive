import discord
import time
from discord.ext import commands
from random import choice, randint
from redbot.core import Config
from redbot.core import checks
import asyncio
import os
import time

class Rainbow:
    """Rainbows the selected role"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 356478965)
        default_guild = {"role":[], "enabled":False}
        default_global = {"delay":300.0}
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.loop = bot.loop.create_task(self.change_colours())

    def __unload(self):
        self.loop.cancel()

    @commands.group(name="rainbow")
    @checks.admin_or_permissions(manage_roles=True)
    async def _rainbow(self, ctx):
        """Command for setting required access information for the API"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @_rainbow.command( name="interval")
    async def _interval(self, ctx, interval:float):
        """Changes the interval between colour changes (GLOBAL ONLY)"""
        if interval < 120.0 and interval > 500.0:
            await ctx.send("Please choose an interval between 120 and 500 seconds.")
            return
        await self.config.delay.set(interval)
        await ctx.send("Rainbow interval set to {}".format(interval))

    @_rainbow.command(pass_context = True, name="add")
    async def add_rainbow(self, ctx, *, role: discord.Role):
        """Adds a role to change colour at the set interval"""
        guild = ctx.message.guild
        if role.id in await self.config.guild(guild).role():
            await ctx.send("{} is already set to rainbow!".format(role.name))
            return
        role_list = await self.config.guild(guild).role()
        role_list.append(role.id)
        await self.config.guild(guild).role.set(role_list)
        await self.config.guild(guild).enabled.set(True)
        await ctx.send("{} has been set to rainbow!".format(role.name))

    @_rainbow.command(name="remove", aliases=["del", "rem"])
    async def remove_rainbow(self, ctx, *, role: discord.Role):
        """Removes a role from being changed at the set interval"""
        guild = ctx.message.guild
        if role.id not in await self.config.guild(guild).role():
            await ctx.send("{} is not set to rainbow!".format(role.name))
            return
        role_list = await self.config.guild(guild).role()
        role_list.remove(role.id)
        await self.config.guild(guild).role.set(role_list)
        await ctx.send("{} has been set to rainbow!".format(role.name))

    @_rainbow.command(pass_context = True, name="stop")
    async def stop_rainbow(self, ctx):
        """Stops the rainbow from working on this server"""
        guild = ctx.message.guild
        await self.config.guild(guild).enabled.set(False)
        await ctx.send("Rainbow disabled")

    @_rainbow.command(pass_context = True, name="start")
    async def start_rainbow(self, ctx):
        """Starts the rainbow for chosen roles on this server"""
        guild = ctx.message.guild
        await self.config.guild(guild).enabled.set(True)
        await ctx.send("Rainbow enabled")
    
    async def get_role_obj(self, id_list, guild):
        role = []
        for role_id in id_list:
            try:
                for roles in guild.roles:
                    if roles.id == role_id:
                        role.append(roles)
            except AttributeError:
                print("There was a role colour change error!")
        return role
    
    async def change_colours(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Rainbow"):
            guild_list = [guild for guild in await self.config.all_guilds() if await self.config.guild(self.bot.get_guild(guild)).enabled()]
            for guild_id in guild_list:
                guild = self.bot.get_guild(id=guild_id)
                roles = await self.get_role_obj(await self.config.guild(guild).role(), guild)
                for role in roles:
                    colour = int(''.join([choice('0123456789ABCDEF') for x in range(6)]), 16)
                    await role.edit(colour=discord.Colour(value=colour))
            print("Roles updated!")
            await asyncio.sleep(await self.config.delay())
