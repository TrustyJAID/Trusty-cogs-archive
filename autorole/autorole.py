import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
import random
import string
import os

default_settings = {
            "ENABLED": False,
            "ROLE": [],
            "AGREE_CHANNEL": None,
            "AGREE_MSG": None
        }

class Autorole(getattr(commands, "Cog", object)):
    """
        Autorole commands. Rewritten for V3 from 
        https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/autorole/autorole.py
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 45463543548)
        self.config.register_guild(**default_settings)
        self.users = {}
        self.messages = {}

    async def _no_perms(self, guild):
        m = ("It appears that you haven't given this "
             "bot enough permissions to use autorole. "
             "The bot requires the \"Manage Roles\" and "
             "the \"Manage Messages\" permissions in"
             "order to use autorole. You can change the "
             "permissions in the \"Roles\" tab of the "
             "guild settings.")
        await self.bot.send_message(guild, m)

    async def on_message(self, message):
        guild = message.guild
        user = message.author
        if guild is None:
            return
        try:
            if await self.config.guild(guild).AGREE_CHANNEL() is not None:
                pass
            else:
                return
        except:
            return

        try:
            if message.content == self.users[user.id]:
                roles_id = await self.config.guild(guild).ROLE()
                try:
                    roles = guild.roles
                except AttributeError:
                    print("This guild has no roles... what even?\n")
                    return

                roles = [discord.utils.get(guild.roles, id=x) for x in roles_id]
                try:
                    for role in roles:
                        if role is None:
                            continue
                        await user.add_roles(role)
                    if message.channel.permissions_for(guild.me).manage_messages:
                        await message.delete()
                    if user.id in self.messages:
                        self.messages.pop(user.id, None)
                except discord.Forbidden:
                    await self._no_perms(guild)
        except KeyError:
            return

    async def _agree_maker(self, member):
        guild = member.guild
        self.last_guild = guild
        # await self._verify_json(None)
        key = ''.join(random.choice(string.ascii_uppercase +
                                    string.digits) for _ in range(6))
        # <3 Stackoverflow http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630#23728630
        self.users[member.id] = key
        ch = guild.get_channel(await self.config.guild(guild).AGREE_CHANNEL())
        msg = await self.config.guild(guild).AGREE_MSG()
        try:
            msg = msg.format(key=key,
                             member=member,
                             name=member.name,
                             mention=member.mention,
                             guild=guild.name)
        except Exception as e:
            self.bot.logger.error(e)

        try:
            msg = await member.send(msg)
        except discord.Forbidden:
            msg = await ch.send(msg)
        except discord.HTTPException:
            return
        self.messages[member.id] = msg

    async def _auto_give(self, member):
        guild = member.guild
        try:
            roles_id = await self.config.guild(guild).ROLE()
        except KeyError:
            return
        except AttributeError:
            print("This guild has no roles... what even?\n")
            return

        roles = [discord.utils.get(guild.roles, id=x) for x in roles_id]
        try:
            for role in roles:
                if role is None:
                    continue
                await member.add_roles(role)
        except discord.Forbidden:
            await self._no_perms(guild)

    async def on_member_join(self, member):
        guild = member.guild
        self.last_guild = guild  # In case something breaks

        if await self.config.guild(guild).ENABLED():
            try:
                if await self.config.guild(guild).AGREE_CHANNEL() is not None:
                    await self._agree_maker(member)
                else:  # Immediately give the new user the role
                    await self._auto_give(member)
            except KeyError as e:
                self.last_guild = guild

    @commands.group(name="autorole", pass_context=True, no_pm=True)
    async def autorole(self, ctx):
        """Change settings for autorole

        Requires the manage roles permission"""
        guild = ctx.message.guild
        if ctx.invoked_subcommand is None:
            try:
                enabled = await self.config.guild(guild).ENABLED()
                roles = await self.config.guild(guild).ROLE()
                role_name = []
                for guild_role in guild.roles:
                    for auto_role in roles:
                        if guild_role.id == auto_role:
                            role_name.append(guild_role.name)
                role_name_str = ", ".join(role for role in role_name)
                await ctx.send("```Current autorole state: {}\nCurrent Roles:{}```".format(enabled, role_name_str))
            except KeyError:
                pass

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Enables/Disables autorole"""
        guild = ctx.message.guild
        if await self.config.guild(guild).ROLE() is None:
            await ctx.send("You haven't set a role to give to new users! "
                               "Use `{}autorole role \"role\"` to set it!"
                               .format(ctx.prefix))
        else:
            if await self.config.guild(guild).ENABLED():
                await self.config.guild(guild).ENABLED.set(False)
                await ctx.send("Autorole is now disabled.")
            else:
                await self.config.guild(guild).ENABLED.set(True)
                await ctx.send("Autorole is now enabled.")

    @autorole.command(pass_context=True, no_pm=True, name="add", aliases=["role"])
    @checks.admin_or_permissions(manage_roles=True)
    async def role(self, ctx, *, role: discord.Role):
        """Add a role for autorole to assign.
        
        You can use this command multiple times to add multiple roles."""
        guild = ctx.message.guild
        roles = await self.config.guild(guild).ROLE()
        if not guild.me.guild_permissions.manage_roles:
            await ctx.send("I don't have the manage roles permission to use these features!")
            return
        if role.id in roles:
            await ctx.send("{} is already in the autorole list.".format(role.name))
            return
        if guild.me.top_role < role:
            await ctx.send("{} is higher than my highest role in the Discord hierarchy.".format(role.name))
            return
        roles.append(role.id)
        await self.config.guild(guild).ROLE.set(roles)
        await ctx.send(f"Added the role `{role.name}` to the autorole.")
            
    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def remove(self, ctx, *, role: discord.Role):
        """Remove a role from the autorole."""
        guild = ctx.message.guild
        roles = await self.config.guild(guild).ROLE()
        if role.id not in roles:
            await ctx.send("{} is not in the autorole list.".format(role.name))
            return
        roles.remove(role.id)
        await self.config.guild(guild).ROLE.set(roles)
        await ctx.send(f"Removed the role `{role.name}` from the autorole.")

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def agreement(self, ctx, channel: discord.TextChannel=None, *, msg: str=None):
        """Set the channel and message that will be used for accepting the rules.
        This is not needed and is completely optional

        Entering nothing will disable this."""
        guild = ctx.message.guild

        if channel is None:
            await self.config.guild(guild).AGREE_CHANNEL.set(None)
            await ctx.send("Agreement channel cleared")
        else:
            await self.config.guild(guild).AGREE_CHANNEL.set(channel.id)
            if msg is None:
                msg = "{name} please enter this code: {key}"
            await self.config.guild(guild).AGREE_MSG.set(msg)
            await ctx.send("Agreement channel set to {}".format(channel.mention))
