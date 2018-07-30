import discord
from discord.ext import commands
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
                        "check_roles": [],
                        "time": 604800,
                        "invite": True,
                        "link": "",
                        "rip_count": 0,
                        "enabled":False,
                        "members":[]}
        self.config = Config.get_conf(self, 16484554673)
        self.units = {"minute" : 60, "hour" : 3600, "day" : 86400, "week": 604800, "month": 2592000}
        self.activitycheck = bot.loop.create_task(self.activity_checker())

    def __unload(self):
        self.activitycheck.cancel()

    async def get_role(self, guild, role_id):
        role_return = None
        for role in guild.roles:
            if role.id == role_id:
                role_return = role
        return role_return

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def activity(self, ctx):
        """Setup an activity checker channel"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            guild = ctx.message.guild
            time = await self.config.guild(guild).time()
            channel = guild.get_channel(await self.config.guild(guild).channel())
            if channel is None:
                channel = "None"
            else:
                channel = channel.mention
            link = await self.config.guild(guild).link()
            link_enabled = await self.config.guild(guild).invite()
            enabled = await self.config.guild(guild).enabled()
            roles_list = await self.config.guild(guild).check_roles()
            if roles_list is None:
                roles = "None"
            else:
                for role in roles_list:
                    roles = ", ".join(x.mention for x in guild.roles if x.id == role)
            rip_count = await self.config.guild(guild).rip_count()
            em = discord.Embed()
            if enabled:
                em.description = "The Activity Checker is currently **ON**"
            else:
                em.description = "The Activity Checker is currently **OFF**"
            em.set_author(name="{} Activity Checker".format(guild.name), icon_url=guild.icon_url)
            em.add_field(name="Channel", value="Posting kick messages in {}".format(channel))
            em.add_field(name="Roles being checked", value=roles)
            em.add_field(name="Time", value=time)
            em.add_field(name="RIP", value="{} members had DM's from the bot disabled".format(rip_count))
            em.set_thumbnail(url=guild.icon_url)
            if link_enabled:
                em.add_field(name="Invite Link", value=link)
            await ctx.send(embed=em)

    @activity.command(pass_context=True, name="list")
    async def list_roles(self, ctx):
        """lists the roles checked"""
        guild = ctx.message.guild
        if not await self.config.guild(ctx.guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
        else:
            msg = ""
            for role in await self.config.guild(ctx.guild).check_roles():
                role_name = ", ".join(x.name for x in guild.roles if x.id == role)
                msg += role_name
            await ctx.send("```" + msg + "```")

    async def check_ignored_users(self, guild, member_id):
        member = guild.get_member(member_id)
        roles = await self.config.guild(guild).check_roles()
        if member is None:
            # print("member doesn't exist on the guild I should remove them from the list")
            member_list = await self.config.guild(guild).members()
            member_list.remove(member_id)
            await self.config.guild(guild).members.set(member_list)
            return True
        if member.bot:
            # print("member is a bot account, we don't care about those " + member.name)
            return True
        if  member is guild.owner:
            # print("member is the guild owner, we can't kick them anyways " + member.name)
            return True
        if  member.id == self.bot.owner_id:
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
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
        member_list = await self.config.guild(guild).members()
        for member_id in member_list:
            member = guild.get_member(member_id["id"])
            if await self.check_ignored_users(guild, member_id["id"]):
                continue
            member_time = member_id["time"]
            if member_time <= last_post_time:
                last_post_time = member_time
                member_name = member.mention
        time_left = timedelta(seconds=abs(time.time() - last_post_time - await self.config.guild(guild).time()), microseconds=0)
        time_left = time_left - timedelta(microseconds=time_left.microseconds)
        clean_time = "{} seconds until purging starts with {}!".format(time_left, member_name)
        # clean_time = time.strftime("%j days %H hours %M minutes %S seconds", time.gmtime(time_left))
        await ctx.send(clean_time)

    @activity.command(pass_context=True, name="remove", aliases=["disable"])
    async def rem_guild(self, ctx):
        """Removes a guild from the activity checker"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
        await self.config.guild(guild).enabled.set(False)
        await ctx.send("Done! No more activity checking in {}!".format(guild.name))


    async def get_everyone_role(self, guild):
        for role in guild.roles:
            if role.is_default():
                return role.id

    @activity.command(pass_context=True, name="role")
    async def role_check(self, ctx, role:discord.Role):
        """Add or remove a role to be checked. Remove all roles to check everyone."""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
        guild_roles = await self.config.guild(guild).check_roles()
        channel = ctx.message.channel
        added_role = False
        everyone_role = await self.get_everyone_role(guild)
        if role.id in guild_roles:
            guild_roles.remove(role.id)
            await channel.send("Now ignoring {}!".format(role.name))
            added_role = True
        if role.id not in guild_roles and not added_role:
            guild_roles.append(role.id)
            await channel.send("Now checking {}!".format(role.name))
        if len(guild_roles) < 1:
            guild_roles.append(everyone_role)
            await self.bot.send_message(channel, "Now checking everyone!")
        if len(guild_roles) > 1 and everyone_role in guild_roles:
            guild_roles.remove(everyone_role)
        await self.config.guild(guild).check_roles.set(guild_roles)

    @activity.command(pass_context=True, name="invite")
    async def send_invite(self, ctx):
        """Toggles sending user invite links to re-join the guild"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return

        if await self.config.guild(guild).invite():
            await self.config.guild(guild).invite.set(False)
            await ctx.send("No longer sending invite links!")
            return
        if not await self.config.guild(guild).invite():
            await self.config.guild(guild).invite.set(True)
            await ctx.send("Sending invite links to kicked users!")
            return

    @activity.command(pass_context=True, name="link")
    async def set_invite_link(self, ctx, *, link=None):
        """Sets the invite link for when the bot can't create one."""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
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
        await self.config.guild(guild).link.set(invite_link.url)
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
    async def refresh(self, ctx, channel:discord.TextChannel=None, guild:discord.guild=None):
        """Refreshes the activity checker to start right now"""
        if guild is None:
            guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
        await self.build_list(ctx, guild)
        await ctx.send("The list has been refreshed!")

    async def build_list(self, ctx, guild):
        """Builds a new list of all guild members"""
        cur_time = time.time()
        member_list = {}
        for member in guild.members:
            if await self.check_ignored_users(guild, member.id):
                continue
            member_list[member.id] = cur_time
        await self.config.guild(guild).members.set(member_list)
        return

    @activity.command(pass_context=True, name="time")
    async def set_time(self, ctx, quantity : int, time_unit : str):
        """Set the time to check for removal"""
        time_unit = time_unit.lower()
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
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
        await self.config.guild(guild).time.set(seconds)
        await ctx.send("Okay, setting the guild time check to {}s".format(seconds))

    @activity.command(pass_context=True, name="channel")
    async def set_channel(self, ctx, channel:discord.TextChannel=None):
        """Set the channel to post activity messages"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup to check activity on this guild!")
            return
        await self.config.guild(guild).channel.set(channel.id)
        await ctx.send("Okay, sending warning messages to {}".format(channel.mention))


    @activity.command(pass_context=True, name="set")
    async def add_guild(self, ctx, channel:discord.TextChannel=None, role:discord.Role=None):
        """Set the guild for activity checking"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        if role is not None:
            role = role.id
        if role is None:
            role = await self.get_everyone_role(guild)
        if await self.config.guild(ctx.guild).enabled():
            await ctx.send("This guild is already checking for activity!")
            return
        invite_link = "https://discord.gg/"
        # if invite_link is None:
            # await ctx.send("I could not create an invite link here! Set a link I can use with the link command.")
        # else:
            # invite_link = invite_link.url
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await self.config.guild(ctx.guild).check_roles.set([role])
        await self.config.guild(ctx.guild).time.set(604800)
        await self.config.guild(ctx.guild).invite.set(True)
        await self.config.guild(ctx.guild).link.set(invite_link)
        await self.config.guild(ctx.guild).rip_count.set(0)
        await self.config.guild(ctx.guild).members.set([])
        await self.config.guild(ctx.guild).enabled.set(True)

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
            for guild in self.bot.guilds:

                if not await self.config.guild(guild).enabled():
                    # Ignore guilds not added to the activity checker
                    continue
                roles = await self.config.guild(guild).check_roles()
                cur_time = time.time()
                member_list = await self.config.guild(guild).members()
                for member_id in member_list:
                    member = guild.get_member(member_id["id"])
                    if await self.check_ignored_users(guild, member_id["id"]):
                        continue
                    last_msg_time = cur_time - member_id["time"]
                    guild_time = await self.config.guild(guild).time()
                    if last_msg_time > guild_time:
                        await self.maybe_kick(guild, member)
            await asyncio.sleep(15)

    async def remove_member(self, guild, member_id):
        member_list = await self.config.guild(guild).members()
        for member in member_list:
            if member_id == member["id"]:
                member_list.remove(member)
        await self.config.guild(guild).members.set(member_list)

    async def update_member(self, guild, member_id):
        member_list = await self.config.guild(guild).members()
        for member in member_list:
            if member_id == member["id"]:
                member_list.remove(member)
                member["time"] = time.time()
                member_list.append(member)
        await self.config.guild(guild).members.set(member_list)

    async def check_member(self, guild, member_id):
        member_list = await self.config.guild(guild).members()
        exists = False
        for member in member_list:
            if member_id == member["id"]:
                exists = True
        return exists


    async def maybe_kick(self, guild, member):
        channel = guild.get_channel(await self.config.guild(guild).channel())
        msg = await channel.send("{}, you haven't talked in a while! you have 15 seconds to react to this message to stay!"
                                 .format(member.mention))
        await msg.add_reaction("☑")
        check = lambda react, user:user.id == member.id and react.emoji == "☑" and react.message.id == msg.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=15.0)
        except asyncio.TimeoutError:
            await msg.remove_reaction("☑", guild.me)
            await channel.send("Goodbye {}!".format(member.mention))
            await self.maybe_invite(guild, member)
            try:
                await guild.kick(member)
            except Exception as e:
                print("Could not Kick {}({}): {}".format(member.name, member.id, e))

            await self.remove_member(guild, member.id)
        else:
            await msg.remove_reaction("☑", guild.me)
            await channel.send("Good, you decided to stay!")
            await self.update_member_time(guild, member.id)

    async def maybe_invite(self, guild, member):
        if await self.config.guild(guild).invite():
            invite = await self.config.guild(guild).link()
            if invite is not None:
                invite_msg = "You have been kicked from {0}, here's an invite link to get back! {1}".format(guild.name, invite)
                try:
                    await member.send(invite_msg)
                except(discord.errors.Forbidden, discord.errors.NotFound):
                    rip_count = await self.config.guild(guild).rip_count()
                    rip_count += 1
                    await self.config.guild(guild).rip_count.set(rip_count)
                    channel = guild.get_channel(await self.config.guild(guild).channel())
                    await channel.send("RIP #{0} {1}".format(rip_count, member.name))
                except discord.errors.HTTPException:
                    pass
            else:
                rip_count = await self.config.guild(guild).rip_count()
                rip_count += 1
                await self.config.guild(guild).rip_count.set(rip_count)
                channel = guild.get_channel(id=await self.config.guild(guild).channel())
                await channel.send("RIP #{0} {1}".format(rip_count, member.name))
            



    async def on_message(self, message):
        guild = message.guild
        author = message.author
        if message.guild is None:
            return
        if not await self.config.guild(guild).enabled():
            return
        if await self.check_member(guild, author.id):
            if not await self.check_ignored_users(guild, author.id):
                await self.update_member(guild, author.id)
            else:
                return
        else:
            if not await self.check_ignored_users(guild, author.id):
                member_list = await self.config.guild(guild).members()
                member_data = {"id":author.id, "name":author.name, "time":time.time()}
                member_list.append(member_data)
                await self.config.guild(guild).members.set(member_list)
            else:
                return
