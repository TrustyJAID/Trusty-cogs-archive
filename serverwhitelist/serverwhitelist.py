import discord
from redbot.core import commands
from redbot.core import Config, checks

class ServerWhitelist:

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 1584348454)
        default = {"whitelist":[]}
        self.config.register_global(**default)

    @commands.group(name="serverwhitelist", aliases=["guildwhitelist"])
    @checks.is_owner()
    async def serverwhitelist(self, ctx):
        """Add or remove servers to the bots approved server list"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @serverwhitelist.command(aliases=["set"])
    @checks.is_owner()
    async def add(self, ctx, server_id:int):
        """Add a server to the bots approved server list."""
        cur_list = await self.config.whitelist()
        if server_id in cur_list:
            await ctx.send("{} is already in the whitelist.".format(server_id))
            return
        cur_list.append(server_id)
        await self.config.whitelist.set(cur_list)
        await ctx.send("{} server has been added to the whitelist.".format(server_id))


    @serverwhitelist.command()
    @checks.is_owner()
    async def remove(self, ctx, server_id:int):
        """Removes a server from the bots approved server list."""
        cur_list = await self.config.whitelist()
        if server_id not in cur_list:
            await ctx.send("{} is not in the whitelist.".format(server_id))
            return
        cur_list.remove(server_id)
        await self.config.whitelist.set(cur_list)
        await ctx.send("{} server has been removed the whitelist.".format(server_id))

    async def on_guild_join(self, guild):
        """Checks if a joined server is in the bots approved server list and leaves if it isn't."""
        whitelist = await self.config.whitelist()
        if guild.id not in whitelist:
            await guild.leave()

