import discord
from discord.ext import commands
from redbot.core import checks
from redbot.core import Config
import random
import string
import os

default_settings = {
            "ENABLED": False,
            "ROLE": None,
            "AGREE_CHANNEL": None,
            "AGREE_MSG": None
        }

class Autorole:
    """Autorole commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 45463543548)
        self.config.register_guild(**default_settings)
        # self.file_path = "data/autorole/settings.json"
        # self.settings = dataIO.load_json(self.file_path)
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
                roleid = await self.config.guild(guild).ROLE()
                try:
                    roles = guild.roles
                except AttributeError:
                    print("This guild has no roles... what even?\n")
                    return

                role = discord.utils.get(roles, id=roleid)
                try:
                    await user.add_roles(user)
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
        ch = discord.utils.get(
            self.bot.get_all_channels(),
            id=await self.config.guild(guild).AGREE_CHANNEL())
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
            roleid = await self.config.guild(guild).ROLE()
            roles = guild.roles
        except KeyError:
            return
        except AttributeError:
            print("This guild has no roles... what even?\n")
            return
        role = discord.utils.get(roles, id=roleid)
        try:
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
            await ctx.send_help()
            try:
                await ctx.send("```Current autorole state: {}```".format(
                    await self.config.guild(guild).ENABLED()))
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

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def role(self, ctx, role: discord.Role):
        """Set role for autorole to assign.

        Use quotation marks around the role if it contains spaces."""
        guild = ctx.message.guild
        await self.config.guild(guild).ROLE.set(role.id)
        await ctx.send("Autorole set to " + role.name)

    @autorole.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def agreement(self, ctx, channel: str,
                        *, msg: str=None):
        """Set the channel and message that will be used for accepting the rules.
        This is not needed and is completely optional

        Entering only \"clear\" will disable this."""
        guild = ctx.message.guild

        if not channel:
            await ctx.send_help()
            return

        if channel.startswith("<#"):
            channel = channel[2:-1]

        if channel == "clear":
            await self.config.guild(guild).AGREE_CHANNEL.set(None)
            await ctx.send("Agreement channel cleared")
        else:
            ch = discord.utils.get(guild.channels, name=channel)
            if ch is None:
                ch = discord.utils.get(guild.channels, id=channel)
            if ch is None:
                await ctx.send("Channel not found!")
                return
            try:
                await self.config.guild(guild).AGREE_CHANNEL.set(ch.id)
            except AttributeError as e:
                await ctx.send("Something went wrong...")
            if msg is None:
                msg = "{name} please enter this code: {key}"
            await self.config.guild(guild).AGREE_MSG.set(msg)
            await ctx.send("Agreement channel "
                               "set to {}".format(ch.name))
