import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from redbot.core import checks
from redbot.core import Config
import asyncio
import os
import urllib.request
import aiohttp
import json
import time
from datetime import timedelta

class ActivityChecker():

    def __init__(self, bot):
        self.bot = bot
        default_guild = {"channel": "",
                        "check_roles": 0,
                        "time": 604800,
                        "invite": True,
                        "link": "",
                        "rip_count": 0,
                        "enabled":False}
        # self.settings_file = "data/activity/settings.json"
        # self.log_file = "data/activity/log.json"
        # self.settings = dataIO.load_json(self.settings_file)
        # self.log = dataIO.load_json(self.log_file)
        self.config = Config.get_conf(self, 16484554673)

        self.units = {"minute" : 60, "hour" : 3600, "day" : 86400, "week": 604800, "month": 2592000}
        # loop = asyncio.get_event_loop()
        self.activitycheck = bot.loop.create_task(self.activity_checker())

    def __unload(self):
        self.activitycheck.cancel()

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def activity(self, ctx):
        """Setup an activity checker channel"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @activity.command(pass_context=True, name="list")
    async def list_roles(self, ctx):
        """lists the roles checked"""
        guild = ctx.message.guild
        if guild.id not in self.log:
            await ctx.send("I am not setup to check activity on this guild!")
        else:
            msg = ""
            for role in self.settings[guild.id]["check_roles"]:
                role_name = "".join(x.name for x in guild.roles if x.id == role)
                msg += role_name + ", "
        await ctx.send("```" + msg[:-2] + "```")

    async def check_ignored_users(self, guild, member_id):
        member = guild.get_member(member_id)
        roles = self.settings[guild.id]["check_roles"]
        if member is None:
            # print("member doesn't exist on the guild I should remove them from the list")
            try:
                del self.log[guild.id][member_id]
                dataIO.save_json(self.log_file, self.log)
            except KeyError:
                pass
            return True
        if member.bot:
            # print("member is a bot account, we don't care about those " + member.name)
            return True
        if  member is guild.owner:
            # print("member is the guild owner, we can't kick them anyways " + member.name)
            return True
        if  member.id == self.bot.settings.owner:
            # print("member is the bot owner, we don't want to kick them do we? " + member.name)
            return True
        for role in member.roles:
            # print(role.id)
            if role.id in roles:
                return False
        return True

    @activity.command(pass_context=True, name="next")
    async def get_time_left(self, ctx):
        """View how much time until the next purge starts!"""
        last_post_time = time.time()
        guild = ctx.message.guild
        member_name = ""
        if guild.id not in self.log:
            await ctx.send("I don't have activity checking set on this guild!")
            return
        for member_id in list(self.log[guild.id]):
            member = guild.get_member(member_id)
            if await self.check_ignored_users(guild, member_id):
                continue
            member_time = self.log[guild.id][member_id]
            if member_time <= last_post_time:
                last_post_time = member_time
                member_name = member.name
        time_left = timedelta(seconds=abs(time.time() - last_post_time - self.settings[guild.id]["time"]), microseconds=0)
        time_left = time_left - timedelta(microseconds=time_left.microseconds)
        clean_time = "{} seconds until purging starts with {}!".format(time_left, member_name)
        # clean_time = time.strftime("%j days %H hours %M minutes %S seconds", time.gmtime(time_left))
        await ctx.send(clean_time)

    @activity.command(pass_context=True, name="remove")
    async def rem_guild(self, ctx, guild:discord.guild=None):
        """Removes a guild from the activity checker"""
        if guild is None:
            guild = ctx.message.guild
        if guild.id in self.settings:
            del self.settings[guild.id]
            dataIO.save_json(self.settings_file, self.settings)
        if guild.id in self.log:
            del self.log[guild.id]
            dataIO.save_json(self.log_file, self.log)
        await ctx.send("Done! No more activity checking in {}!".format(guild.name))

    async def get_everyone_role(self, guild):
        for role in guild.roles:
            if role.is_everyone:
                return role.id

    @activity.command(pass_context=True, name="role")
    async def role_ignore(self, ctx, role:discord.Role):
        """Add or remove a role to be checked. Remove all roles to check everyone."""
        guild = ctx.message.guild
        guild_roles = self.settings[guild.id]["check_roles"]
        channel = ctx.message.channel
        added_role = False
        everyone_role = await self.get_everyone_role(guild)
        if role.id in guild_roles:
            self.settings[guild.id]["check_roles"].remove(role.id)
            await self.bot.send_message(channel, "Now ignoring {}!".format(role.name))
            added_role = True
        if role.id not in guild_roles and not added_role:
            self.settings[guild.id]["check_roles"].append(role.id)
            await self.bot.send_message(channel, "Now checking {}!".format(role.name))
        if len(guild_roles) < 1:
            self.settings[guild.id]["check_roles"].append(everyone_role)
            await self.bot.send_message(channel, "Now checking everyone!")
        if len(guild_roles) > 1 and everyone_role in guild_roles:
            self.settings[guild.id]["check_roles"].remove(everyone_role)
        dataIO.save_json(self.settings_file, self.settings)

    @activity.command(pass_context=True, name="invite")
    async def send_invite(self, ctx):
        """Toggles sending user invite links to re-join the guild"""
        guild = ctx.message.guild
        if guild.id not in self.settings:
            await ctx.send("I am not setup to check activity on this guild!")
            return
        if self.settings[guild.id]["invite"]:
            self.settings[guild.id]["invite"] = False
            await ctx.send("No longer sending invite links!")
            return
        if not self.settings[guild.id]["invite"]:
            self.settings[guild.id]["invite"] = True
            await ctx.send("Sending invite links to kicked users!")
            return

    @activity.command(pass_context=True, name="link")
    async def set_invite_link(self, ctx, *, link=None):
        """Sets the invite link for when the bot can't create one."""
        guild = ctx.message.guild
        if link is None:
            invite_link = await self.get_invite_link(guild)
            if invite_link is None:
                await ctx.send("I cannot create a link here! Please set a link for me to use!")
                return
        else:
            try:
                invite_link = await self.bot.get_invite(link)
            except(discord.errors.NotFound, HTTPException):
                await ctx.send("That is not a valid discord invite link!")
                return
        self.settings[guild.id]["link"] = invite_link.url
        dataIO.save_json(self.settings_file, self.settings)
        await ctx.send("Invite link set to {} for this guild!".format(invite_link))
        

    async def get_invite_link(self, guild):
        try:
            # tries to create a guild link
            link = await self.bot.create_invite(guild, unique=False)
            return link
        except discord.errors.NotFound:
            # tries to create a guild default channel link
            link = await self.bot.create_invite(guild.default_channel, unique=False)
            return link
        except:
            # if a link cannot be created it returns None
            return None        

    @activity.command(pass_context=True)
    async def refresh(self, ctx, channel:discord.channel=None, guild:discord.guild=None):
        """Refreshes the activity checker to start right now"""
        if guild is None:
            guild = ctx.message.guild
        await self.build_list(ctx, guild)
        await ctx.send("The list has been refreshed!")

    async def build_list(self, ctx, guild):
        """Builds a new list of all guild members"""
        cur_time = time.time()
        self.log[guild.id] = {}
        for member in guild.members:
            if await self.check_ignored_users(guild, member.id):
                continue
            self.log[guild.id][member.id] = cur_time
        dataIO.save_json(self.log_file, self.log)
        return

    @activity.command(pass_context=True, name="time")
    async def set_time(self, ctx, quantity : int, time_unit : str):
        """Set the time to check for removal"""
        time_unit = time_unit.lower()
        guild = ctx.message.guild
        s = ""
        if time_unit.endswith("s"):
            time_unit = time_unit[:-1]
            s = "s"
        if not time_unit in self.units:
            await ctx.send("Invalid time unit. Choose minutes/hours/days/weeks/month")
            return
        if quantity < 1:
            await ctx.send("Quantity must not be 0 or negative.")
            return
        seconds = self.units[time_unit] * quantity
        self.settings[guild.id]["time"] = seconds
        dataIO.save_json(self.settings_file, self.settings)
        await ctx.send("Okay, setting the guild time check to {}".format(seconds))

    @activity.command(pass_context=True, name="channel")
    async def set_channel(self, ctx, channel:discord.Channel=None):
        """Set the channel to post activity messages"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        if guild.id not in self.settings:
            await ctx.send("I am not setup to check activity on this guild!")
            return
        self.settings[guild.id]["channel"] = channel.id
        dataIO.save_json(self.settings_file, self.settings)
        await ctx.send("Okay, sending warning messages to {}".format(channel.mention))


    @activity.command(pass_context=True, name="set")
    async def add_guild(self, ctx, channel:discord.Channel=None, role:discord.Role=None):
        """Set the guild for activity checking"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        if role is not None:
            role = role.id
        if role is None:
            role = await self.get_everyone_role(guild)
        if guild.id in self.log:
            await self.bot.say("This guild is already checking for activity!")
            return
        invite_link = await self.get_invite_link(guild)
        if invite_link is None:
            await ctx.send("I could not create an invite link here! Set a link I can use with the link command.")
        else:
            invite_link = invite_link.url
        self.settings[guild.id] = {"channel": channel.id,
                                    "check_roles": [role],
                                    "time": 604800,
                                    "invite": True,
                                    "link": invite_link,
                                    "rip_count": 0}
        dataIO.save_json(self.settings_file, self.settings)
        await self.build_list(ctx, guild)
        await ctx.send("Sending activity check messages to {}".format(channel.mention))

    def check_roles(self, member, roles):
        """Checks if a role name is in a members roles."""
        has_role = False
        for role in member.roles:
            if role.name in roles:
                has_role = True
        return has_role

    async def activity_checker(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("ActivityChecker"):
            for guild_id in (self.log):
                guild = self.bot.get_guild(id=guild_id)
                channel = self.bot.get_channel(id=self.settings[guild.id]["channel"])
                roles = self.settings[guild.id]["check_roles"]
                cur_time = time.time()
                for member_id in list(self.log[guild.id]):
                    member = guild.get_member(member_id)
                    if await self.check_ignored_users(guild, member_id):
                        continue
                    last_msg_time = cur_time - self.log[guild.id][member.id]
                    if last_msg_time > self.settings[guild.id]["time"]:
                        msg = await self.bot.send_message(channel, "{} you haven't talked in a while! you have 15 seconds to react to this message to stay!"
                                                          .format(member.mention, last_msg_time))
                        await self.bot.add_reaction(msg, "☑")
                        answer = await self.bot.wait_for_reaction(emoji="☑", user=member, message=msg, timeout=15.0)
                        if answer is not None:
                            await self.bot.send_message(channel, "Good, you decided to stay!")
                            self.log[guild.id][member.id] = time.time()
                            dataIO.save_json(self.log_file, self.log)
                        if answer is None:
                            await self.bot.send_message(channel, "Goodbye {}!".format(member.mention))
                            if self.settings[guild.id]["invite"]:
                                invite = self.settings[guild.id]["link"]
                                if invite is None:
                                    # tries to create an invite link
                                    invite = self.get_invite_link(guild)
                                    invite = invite.url
                                if invite is not None:
                                    invite_msg = "You have been kicked from {0}, here's an invite link to get back! {1}".format(guild.name, invite)
                                    try:
                                        await self.bot.send_message(member, invite_msg)
                                    except(discord.errors.Forbidden, discord.errors.NotFound):
                                        if "rip_count" not in self.settings[guild.id]:
                                            self.settings[guild.id]["rip_count"] = 0
                                        self.settings[guild.id]["rip_count"] += 1
                                        dataIO.save_json(self.settings_file, self.settings)
                                        await self.bot.send_message(channel, "RIP #{0} {1}".format(self.settings[guild.id]["rip_count"], member.name))
                                    except discord.errors.HTTPException:
                                        pass
                                else:
                                    if "rip_count" not in self.settings[guild.id]:
                                        self.settings[guild.id]["rip_count"] = 0
                                    self.settings[guild.id]["rip_count"] += 1
                                    dataIO.save_json(self.settings_file, self.settings)
                                    await self.bot.send_message(channel, "RIP #{0} {1}".format(self.settings[guild.id]["rip_count"], member.name))
                                    print("I can't create invites for some reason! Set a link for me to use!")
                            await self.bot.kick(member)
                            del self.log[guild.id][member.id]
                            dataIO.save_json(self.log_file, self.log)
            await asyncio.sleep(15)



    async def on_message(self, message):
        guild = message.guild
        author = message.author
        if message.channel.is_private:
            return
        if guild.id not in self.log:
            return
        if author.id not in self.log[guild.id]:
            if not await self.check_ignored_users(guild, author.id):
                self.log[guild.id][author.id] = time.time()
            else:
                return
        self.log[guild.id][author.id] = time.time()
        dataIO.save_json(self.log_file, self.log)
