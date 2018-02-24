import discord
import os
from discord.ext import commands
from collections import defaultdict
from redbot.core import Config
from redbot.core import checks

default = {
    "sticky_roles": [],
    "to_reapply"  : {}
}


class StickyRoles:
    """Reapplies specific roles on join"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 1358454876)
        self.config.register_guild(**default)
        # db = dataIO.load_json("data/stickyroles/stickyroles.json")
        # self.db = defaultdict(lambda: default.copy(), db)

    @commands.group(pass_context=True, aliases=["stickyrole"])
    @checks.admin()
    async def stickyroles(self, ctx):
        """Adds / removes roles to be reapplied on join"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @stickyroles.command(pass_context=True)
    async def add(self, ctx, *, role: discord.Role):
        """Adds role to be reapplied on join"""
        guild = ctx.message.guild
        sticky_roles = await self.config.guild(guild).sticky_roles()
        if not guild.me.top_role.position > role.position:
            await ctx.send("I don't have enough permissions to add that "
                               "role. Remember to take role hierarchy in "
                               "consideration.")
            return
        sticky_roles.append(role.id)
        await self.config.guild(guild).sticky_roles.set(sticky_roles)
        await ctx.send("That role will now be reapplied on join.")

    @stickyroles.command(pass_context=True)
    async def remove(self, ctx, *, role: discord.Role):
        """Removes role to be reapplied on join"""
        guild = ctx.message.guild
        sticky_roles = await self.config.guild(guild).sticky_roles()
        try:
            sticky_roles.remove(role.id)
        except ValueError:
            await ctx.send("That role was never added in the first place.")
        else:
            await self.config.guild(guild).sticky_roles.set(sticky_roles)
            await ctx.send("That role won't be reapplied on join.")

    @stickyroles.command(pass_context=True)
    async def clear(self, ctx):
        """Removes all sticky roles"""
        guild = ctx.message.guild
        await self.config.guild(guild).sticky_roles.set([])
        await self.config.guild(guild).to_reapply.set({})
        await ctx.send("All sticky roles have been removed.")

    @stickyroles.command(name="list", pass_context=True)
    async def _list(self, ctx):
        """Lists sticky roles"""
        guild = ctx.message.guild
        roles = self.db[guild.id].get("sticky_roles", [])
        roles = [discord.utils.get(guild.roles, id=r) for r in await self.config.guild(guild).sticky_roles()]
        roles = [r.name for r in roles if r is not None]
        if roles:
            await ctx.send("Sticky roles:\n\n" + ", ".join(roles))
        else:
            await ctx.send("No sticky roles. Add some with `{}stickyroles "
                               "add`".format(ctx.prefix))

    async def on_member_remove(self, member):
        guild = member.guild
        sticky_roles = await self.config.guild(guild).sticky_roles()
        to_reapply = await self.config.guild(guild).to_reapply()
        print(guild)
        if to_reapply is None:
            return

        save = False

        for role in member.roles:
            if role.id in sticky_roles:
                if str(member.id) not in to_reapply:
                    to_reapply[str(member.id)] = []
                to_reapply[str(member.id)].append(role.id)
                save = True

        if save:
            await self.config.guild(guild).to_reapply.set(to_reapply)

    async def on_member_join(self, member):
        guild = member.guild
        sticky_roles = await self.config.guild(guild).sticky_roles()
        to_reapply = await self.config.guild(guild).to_reapply()
        if to_reapply is None:
            return

        if str(member.id) not in to_reapply:
            return

        to_add = []

        for role_id in to_reapply[str(member.id)]:
            if role_id not in sticky_roles:
                continue
            role = discord.utils.get(guild.roles, id=role_id)
            if role:
                to_add.append(role)

        del to_reapply[str(member.id)]

        if to_add:
            try:
                await member.add_roles(*to_add)
            except discord.Forbidden:
                print("Failed to add roles to {} ({})\n{}\n"
                      "I lack permissions to do that."
                      "".format(member, member.id, to_add))
            except discord.HTTPException as e:
                print("Failed to add roles to {} ({})\n{}\n"
                      "{}"
                      "".format(member, member.id, to_add, e))

        await self.config.guild(guild).to_reapply.set(to_reapply)
