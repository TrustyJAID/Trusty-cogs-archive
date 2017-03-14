from discord.ext import commands
from cogs.utils import checks
import datetime
from cogs.utils.dataIO import fileIO
import discord
import asyncio
import os
from random import choice, randint

inv_settings = {"Channel": None, "toggleedit": False, "toggledelete": False, "toggleuser": False, "toggleroles": False,
                "togglevoice": False,
                "toggleban": False}


class invitemirror:
    def __init__(self, bot):
        self.bot = bot
        self.direct = "data/modlogset/settings.json"
        self.nolog = ["239498350817312768", "251222374714834944", "284609869082918912", "284354007076569088", "283022328323899392"]

    @checks.admin_or_permissions(administrator=True)
    @commands.group(name='modlogtoggle', pass_context=True, no_pm=True)
    async def modlogtoggles(self, ctx):
        """toggle which server activity to log"""
        if ctx.invoked_subcommand is None:
            db = fileIO(self.direct, "load")
            await self.bot.send_cmd_help(ctx)
            try:
                await self.bot.say("```Current settings:\a\n\a\n" + "Edit: " + str(
                    db[ctx.message.server.id]['toggleedit']) + "\nDelete: " + str(
                    db[ctx.message.server.id]['toggledelete']) + "\nUser: " + str(
                    db[ctx.message.server.id]['toggleuser']) + "\nRoles: " + str(
                    db[ctx.message.server.id]['toggleroles']) + "\nVoice: " + str(
                    db[ctx.message.server.id]['togglevoice']) + "\nBan: " + str(
                    db[ctx.message.server.id]['toggleban']) + "```")
            except KeyError:
                return

    @checks.admin_or_permissions(administrator=True)
    @commands.group(pass_context=True, name='modlogset', no_pm=True)
    async def modlogset(self, ctx):
        """Change modlog settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @modlogset.command(pass_context=True, name='channel', no_pm=True)
    async def channel(self, ctx):
        """Set the channel to send notifications too"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if ctx.message.server.me.permissions_in(ctx.message.channel).send_messages:
            if server.id in db:
                db[server.id]['Channel'] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("Channel changed.")
                return
            if not server.id in db:
                db[server.id] = inv_settings
                db[server.id]["Channel"] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("I will now send toggled modlog notifications here")
        else:
            return

    @modlogset.command(name='disable', pass_context=True, no_pm=True)
    async def disable(self, ctx):
        """disables the modlog"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say("Server not found, use modlogset to set a channnel")
            return
        del db[server.id]
        fileIO(self.direct, "save", db)
        await self.bot.say("I will no longer send modlog notifications here")

    @modlogtoggles.command(name='edit', pass_context=True, no_pm=True)
    async def edit(self, ctx):
        """toggle notifications when a member edits theyre message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleedit"] == False:
            db[server.id]["toggleedit"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages enabled")
        elif db[server.id]["toggleedit"] == True:
            db[server.id]["toggleedit"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Edit messages disabled")

    @modlogtoggles.command(name='delete', pass_context=True, no_pm=True)
    async def delete(self, ctx):
        """toggle notifications when a member delete theyre message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggledelete"] == False:
            db[server.id]["toggledelete"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages enabled")
        elif db[server.id]["toggledelete"] == True:
            db[server.id]["toggledelete"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Delete messages disabled")

    @modlogtoggles.command(name='user', pass_context=True, no_pm=True)
    async def user(self, ctx):
        """toggle notifications when a user changes his profile"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleuser"] == False:
            db[server.id]["toggleuser"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages enabled")
        elif db[server.id]["toggleuser"] == True:
            db[server.id]["toggleuser"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("User messages disabled")

    @modlogtoggles.command(name='roles', pass_context=True, no_pm=True)
    async def roles(self, ctx):
        """toggle notifications when roles change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleroles"] == False:
            db[server.id]["toggleroles"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages enabled")
        elif db[server.id]["toggleroles"] == True:
            db[server.id]["toggleroles"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Role messages disabled")

    @modlogtoggles.command(name='voice', pass_context=True, no_pm=True)
    async def voice(self, ctx):
        """toggle notifications when voice status change"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["togglevoice"] == False:
            db[server.id]["togglevoice"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages enabled")
        elif db[server.id]["togglevoice"] == True:
            db[server.id]["togglevoice"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Voice messages disabled")

    @modlogtoggles.command(name='ban', pass_context=True, no_pm=True)
    async def ban(self, ctx):
        """toggle notifications when a user is banned"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["toggleban"] == False:
            db[server.id]["toggleban"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages enabled")
        elif db[server.id]["toggleban"] == True:
            db[server.id]["toggleban"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("Ban messages disabled")

    async def on_message_delete(self, message):
        server = message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggledelete'] == False:
            return
        if message.channel.id in self.nolog:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%d/%m/%y %H:%M:%S'
        username = message.author
        userid = message.author.id
        channelname = message.channel
        body = message.content
        embed = discord.Embed(description="Message deleted in {}".format(channelname), colour=discord.Colour.gold())
        embed.add_field(name="Content", value=body)
        embed.add_field(name="ID", value=userid)
        embed.set_footer(text=time.strftime(fmt))
        await self.bot.send_message(server.get_channel(channel), embed=embed)

    async def on_message_edit(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleedit'] == False:
            return
        if before.content == after.content:
            return
        if before.channel.id in self.nolog:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%d/%m/%y %H:%M:%S'
        username = before.author
        userid = before.author.id
        channelname = before.channel
        body = before.content
        body2 = after.content
        embed = discord.Embed(description="Message changed in {}".format(channelname), colour=discord.Colour.gold())
        embed.add_field(name="Old Message", value=body)
        embed.add_field(name="New Message", value=body2)
        embed.add_field(name="ID", value=userid)
        embed.set_footer(text=time.strftime(fmt))
        await self.bot.send_message(server.get_channel(channel), embed=embed)

    async def on_voice_state_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['togglevoice'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%d/%m/%y %H:%M:%S'
        await self.bot.send_message(server.get_channel(channel),
                                    "``{}`` {} ({}) Voice status changed:\a\n\a\n__**Before:**__ ``{}``\a\n\a\n__**After:**__ ``{}``".format(
                                        time.strftime(fmt), before, before.id,
                                        before.voice_channel, after.voice_channel))

    async def on_member_update(self, before, after):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] and db[server.id]['toggleroles'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%d/%m/%y %H:%M:%S'
        if not before.nick == after.nick:
            embed = discord.Embed(description="User Name Changed", colour=discord.Colour.gold())
            embed.add_field(name=before + "|" + before.id, value=before.nick + " to " + after.nick)
            embed.add_field(name="Time", value=time.strftime(fmt))
            await self.bot.send_message(server.get_channel(channel), embed=embed)
        if not before.roles == after.roles:
            embed = discord.Embed(description="User Role Changed for " + str(before) + " | " + str(before.id), colour=discord.Colour.gold())
            embed.add_field(name="Roles before", value=" | ".join([r.name for r in before.roles if r.name != "@everyone"]))
            embed.add_field(name="Roles After", value=" | ".join([r.name for r in after.roles if r.name != "@everyone"]))
            embed.set_footer(text=time.strftime(fmt))
            await self.bot.send_message(server.get_channel(channel), embed=embed)

    async def on_member_ban(self, member):
        server = before.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['toggleuser'] == False:
            return
        channel = db[server.id]["Channel"]
        time = datetime.datetime.now()
        fmt = '%d/%m/%y %H:%M:%S'
        embed = discord.Embed(description="User Banned", colour=discord.Colour.gold())
        embed.add_field(name="Username", value=member)
        embed.add_field(name="User ID", value=member.id)
        embed.set_footer(text=time.strftime(fmt))
        await self.bot.send_message(server.get_channel(channel), embed=embed)


def check_folder():
    if not os.path.exists('data/modlogset'):
        print('Creating data/modlogset folder...')
        os.makedirs('data/modlogset')


def check_file():
    f = 'data/modlogset/settings.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(invitemirror(bot))
