from discord.ext import commands
from redbot.core import checks
from redbot.core import Config
import datetime
import discord
import asyncio
import os
from random import choice, randint

inv_settings = {"settings":{"embed": False, "Channel": None, "toggleedit": False, "toggledelete": False, "toggleuser": False,
                "toggleroles": False,
                "togglevoice": False,
                "toggleban": False, "togglejoin": False, "toggleleave": False, "togglechannel": False,
                "toggleguild": False}}


class ModLogs:
    def __init__(self, bot):
        self.bot = bot
        self.direct = "data/modlogset/settings.json"
        self.config = Config.get_conf(self, 154457677895, force_registration=True)
        self.config.register_guild(**inv_settings)

    @checks.admin_or_permissions(administrator=True)
    @commands.group(name='modlogtoggle', pass_context=True, no_pm=True)
    async def modlogtoggles(self, ctx):
        """toggle which guild activity to log"""
        if await self.config.guild(ctx.message.guild).settings() == {}:
            await self.config.guild(ctx.message.guild).set(inv_settings)
        if ctx.invoked_subcommand is None:
            guild = ctx.message.guild
            db = await self.config.guild(guild).settings()
            await ctx.send_help()
            try:
                e = discord.Embed(title="Setting for {}".format(guild.name), colour=discord.Colour.blue())
                e.add_field(name="Delete", value=str(db["toggledelete"]))
                e.add_field(name="Edit", value=str(db["toggleedit"]))
                e.add_field(name="Roles", value=str(db["toggleroles"]))
                e.add_field(name="User", value=str(db["toggleuser"]))
                e.add_field(name="Voice", value=str(db["togglevoice"]))
                e.add_field(name="Ban", value=str(db["toggleban"]))
                e.add_field(name="Join", value=str(db["togglejoin"]))
                e.add_field(name="Leave", value=str(db["toggleleave"]))
                e.add_field(name="Channel", value=str(db["togglechannel"]))
                e.add_field(name="guild", value=str(db["toggleguild"]))
                e.set_thumbnail(url=guild.icon_url)
                await ctx.send(embed=e)
            except KeyError:
                return

    @checks.admin_or_permissions(administrator=True)
    @commands.group(pass_context=True, no_pm=True)
    async def modlogset(self, ctx):
        """Change modlog settings"""
        if await self.config.guild(ctx.message.guild).settings() == {}:
            await self.config.guild(ctx.message.guild).set(inv_settings)
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @modlogset.command(name='channel', pass_context=True, no_pm=True)
    async def _channel(self, ctx):
        """Set the channel to send notifications too"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        print(db)
        if ctx.message.guild.me.permissions_in(ctx.message.channel).send_messages:
            if db["Channel"] is not None:
                db['Channel'] = ctx.message.channel.id
                await self.config.guild(guild).settings.set(db)
                await ctx.send("Channel changed.")
                return
            else:
                db["Channel"] = ctx.message.channel.id
                await self.config.guild(guild).settings.set(db)
                await ctx.send("I will now send toggled modlog notifications here")
        else:
            return

    @modlogset.command(pass_context=True, no_pm=True)
    async def embed(self, ctx):
        """Enables or disables embed modlog."""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["embed"] == False:
            db["embed"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Enabled embed modlog.")
        elif db["embed"] == True:
            db["embed"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Disabled embed modlog.")

    @modlogset.command(pass_context=True, no_pm=True)
    async def disable(self, ctx):
        """disables the modlog"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            await ctx.send("guild not found, use modlogset to set a channnel")
            return
        del db
        await self.config.guild(guild).settings.set(db)
        await ctx.send("I will no longer send modlog notifications here")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def edit(self, ctx):
        """toggle notifications when a member edits theyre message"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleedit"] == False:
            db["toggleedit"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Edit messages enabled")
        elif db["toggleedit"] == True:
            db["toggleedit"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Edit messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """toggles notofications when a member joins the guild."""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["togglejoin"] == False:
            db["togglejoin"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Enabled join logs.")
        elif db['togglejoin'] == True:
            db['togglejoin'] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Disabled join logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def guild(self, ctx):
        """toggles notofications when the guild updates."""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleguild"] == False:
            db["toggleguild"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Enabled guild logs.")
        elif db['toggleguild'] == True:
            db['toggleguild'] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Disabled guild logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def channel(self, ctx):
        """toggles channel update logging for the guild."""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["togglechannel"] == False:
            db["togglechannel"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Enabled channel logs.")
        elif db['togglechannel'] == True:
            db['togglechannel'] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Disabled channel logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        """toggles notofications when a member leaves the guild."""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleleave"] == False:
            db["toggleleave"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Enabled leave logs.")
        elif db['toggleleave'] == True:
            db['toggleleave'] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Disabled leave logs.")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def delete(self, ctx):
        """toggle notifications when a member delete theyre message"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggledelete"] == False:
            db["toggledelete"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Delete messages enabled")
        elif db["toggledelete"] == True:
            db["toggledelete"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Delete messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def user(self, ctx):
        """toggle notifications when a user changes his profile"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleuser"] == False:
            db["toggleuser"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("User messages enabled")
        elif db["toggleuser"] == True:
            db["toggleuser"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("User messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def roles(self, ctx):
        """toggle notifications when roles change"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleroles"] == False:
            db["toggleroles"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Role messages enabled")
        elif db["toggleroles"] == True:
            db["toggleroles"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Role messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def voice(self, ctx):
        """toggle notifications when voice status change"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["togglevoice"] == False:
            db["togglevoice"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Voice messages enabled")
        elif db["togglevoice"] == True:
            db["togglevoice"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Voice messages disabled")

    @modlogtoggles.command(pass_context=True, no_pm=True)
    async def ban(self, ctx):
        """toggle notifications when a user is banned"""
        guild = ctx.message.guild
        db = await self.config.guild(guild).settings()
        if db["toggleban"] == False:
            db["toggleban"] = True
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Ban messages enabled")
        elif db["toggleban"] == True:
            db["toggleban"] = False
            await self.config.guild(guild).settings.set(db)
            await ctx.send("Ban messages disabled")

    async def on_message_delete(self, message):
        guild = message.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['toggledelete'] == False:
            return
        if message.author is message.author.bot:
            pass
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        cleanmsg = message.content
        for i in message.mentions:
            cleanmsg = cleanmsg.replace(i.mention, str(i))
        fmt = '%H:%M:%S'
        if db["embed"] == True:
            name = message.author
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            infomessage = "A message by {}, was deleted in {}".format(message.author.mention, message.channel.mention)
            delmessage = discord.Embed(description=infomessage, colour=discord.Color.purple(), timestamp=time)
            delmessage.add_field(name="Message:", value=cleanmsg)
            delmessage.set_footer(text="User ID: {}".format(message.author.id), icon_url=message.author.avatar_url)
            delmessage.set_author(name=name + " - Deleted Message", url="http://i.imgur.com/fJpAFgN.png", icon_url=message.author.avatar_url)
            delmessage.set_thumbnail(url="http://i.imgur.com/fJpAFgN.png")
            try:
                await guild.get_channel(channel).send( embed=delmessage)
            except:
                pass
        else:
            msg = ":pencil: `{}` **Channel** {} **{}'s** message has been deleted. Content: {}".format(
                time.strftime(fmt), message.channel.mention, message.author, cleanmsg)
            await guild.get_channel(channel).send(
                                        msg)

    async def on_member_join(self, member):
        guild = member.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['togglejoin'] == False:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        users = len([e.name for e in guild.members])
        if db["embed"] == True:
            name = member
            # name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            joinmsg = discord.Embed(description=member.mention, colour=discord.Color.red(), timestamp=member.joined_at)
            # infomessage = "Total Users: {}".format(users)
            joinmsg.add_field(name="Total Users:", value=str(users), inline=True)
            joinmsg.set_footer(text="User ID: {}".format(member.id), icon_url=member.avatar_url)
            joinmsg.set_author(name=name.display_name + " has joined the guild",url=member.avatar_url, icon_url=member.avatar_url)
            joinmsg.set_thumbnail(url=member.avatar_url)
            try:
                await guild.get_channel(channel).send( embed=joinmsg)
            except:
                pass
        if db["embed"] == False:
            msg = ":white_check_mark: `{}` **{}** join the guild. Total users: {}.".format(time.strftime(fmt),
                                                                                            member.name, users)
            await guild.get_channel(channel).send( msg)

    async def on_member_remove(self, member):
        guild = member.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['toggleleave'] == False:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = "%H:%M:%S"
        users = len([e.name for e in guild.members])
        if db["embed"] == True:
            name = member
            # name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            joinmsg = discord.Embed(description=member.mention, colour=discord.Color.red(), timestamp=time)
            # infomessage = "Total Users: {}".format(users)
            joinmsg.add_field(name="Total Users:", value=str(users), inline=True)
            joinmsg.set_footer(text="User ID: {}".format(member.id), icon_url=member.avatar_url)
            joinmsg.set_author(name=name.display_name + " has left the guild",url=member.avatar_url, icon_url=member.avatar_url)
            joinmsg.set_thumbnail(url=member.avatar_url)
            try:
                await guild.get_channel(channel).send( embed=joinmsg)
            except:
                pass
        if db["embed"] == False:
            msg = ":x: `{}` **{}** has left the guild or was kicked. Total members {}.".format(time.strftime(fmt),
                                                                                                member.name, users)
            await guild.get_channel(channel).send( msg)

    async def on_channel_update(self, before, after):
        guild = before.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['togglechannel'] == False:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = "%H:%M:%S"
        msg = ""
        if before.name != after.name:
            if before.type == discord.ChannelType.voice:
                if db["embed"] == True:
                    fmt = "%H:%M:%S"
                    voice1 = discord.Embed(colour=discord.Color.blue(), timestamp=time)
                    infomessage = ":loud_sound: Voice channel name update. Before: **{}** After: **{}**.".format(
                        before.name, after.name)
                    voice1.add_field(name="Info:", value=infomessage, inline=False)
                    voice1.set_author(name=time.strftime(fmt) + " - Voice Channel Update",
                                      icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                    voice1.set_thumbnail(
                        url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                    try:
                        await guild.get_channel(channel).send( embed=voice1)
                    except:
                        pass
                else:
                    fmt = "%H:%M:%S"
                    await guild.get_channel(channel).send(
                                                ":loud_sound: `{}` Voice channel name update. Before: **{}** After: **{}**.".format(
                                                    time.strftime(fmt), before.name, after.name))
            if before.type == discord.ChannelType.text:
                if db["embed"] == True:
                    fmt = "%H:%M:%S"
                    text1 = discord.Embed(colour=discord.Color.blue(), timestamp=time)
                    infomessage = ":loud_sound: Text channel name update. Before: **{}** After: **{}**.".format(
                        before.name, after.name)
                    text1.add_field(name="Info:", value=infomessage, inline=False)
                    text1.set_author(name=time.strftime(fmt) + " - Voice Channel Update",
                                     icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                    text1.set_thumbnail(
                        url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                    await guild.get_channel(channel).send( embed=text1)
                else:
                    fmt = "%H:%M:%S"
                    await guild.get_channel(channel).send(
                                                ":page_facing_up: `{}` Text channel name update. Before: **{}** After: **{}**.".format(
                                                    time.strftime(fmt), before.name, after.name))
        if before.topic != after.topic:
            if db["embed"] == True:
                fmt = "%H:%M:%S"
                topic = discord.Embed(colour=discord.Colour.blue(), timestamp=time)
                infomessage = ":page_facing_up: `{}` Channel topic has been updated.\n**Before:** {}\n**After:** {}".format(
                    time.strftime(fmt), before.topic, after.topic)
                topic.add_field(name="Info:", value=infomessage, inline=False)
                topic.set_author(name=time.strftime(fmt) + " - Channel Topic Update",
                                 icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                topic.set_thumbnail(
                    url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                try:
                    await self.send_message(guild.get_channel(channel), embed=topic)
                except:
                    pass
            else:
                fmt = "%H:%M:%S"
                await guild.get_channel(channel).send(
                                            ":page_facing_up: `{}` Channel topic has been updated.\n**Before:** {}\n**After:** {}".format(
                                                time.strftime(fmt), before.topic, after.topic))
        if before.position != after.position:
            if before.type == discord.ChannelType.voice:
                if db["embed"] == True:
                    fmt = "%H:%M:%S"
                    voice2 = discord.Embed(colour=discord.Colour.blue(), timestamp=time)
                    voice2.set_thumbnail(
                        url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                    voice2.set_author(name=time.strftime(fmt) + " Voice Channel Position Update",
                                      icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                    infomsg = ":loud_sound: Voice channel position update. Channel: **{}** Before: **{}** After: **{}**.".format(
                        before.name, before.position, after.position)
                    voice2.add_field(name="Info:", value=infomsg, inline=False)
                    try:
                        await guild.get_channel(channel).send( embed=voice2)
                    except:
                        pass
                else:
                    fmt = "%H:%M:%S"
                    await guild.get_channel(channel).send(
                                                ":loud_sound: `{}` Voice channel position update. Channel: **{}** Before: **{}** After: **{}**.".format(
                                                    time.strftime(fmt), before.name, before.position, after.position))
            if before.type == discord.ChannelType.text:
                if db["embed"] == True:
                    fmt = "%H:%M:%S"
                    text2 = discord.Embed(colour=discord.Colour.blue(), timestamp=time)
                    text2.set_thumbnail(
                        url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                    text2.set_author(name=time.strftime(fmt) + " Text Channel Position Update",
                                     icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                    infomsg = ":page_facing_up: Text channel position update. Before: **{}** After: **{}**.".format(
                        before.position, after.position)
                    text2.add_field(name="Info:", value=infomsg, inline=False)
                    try:
                        await guild.get_channel(channel).send( embed=text2)
                    except:
                        pass
                else:
                    fmt = "%H:%M:%S"
                    await guild.get_channel(channel).send(
                                                ":page_facing_up: `{}` Text channel position update. Channel: **{}** Before: **{}** After: **{}**.".format(
                                                    time.strftime(fmt), before.name, before.position, after.position))
        if before.bitrate != after.bitrate:
            if db["embed"] == True:
                fmt = "%H:%M:%S"
                bitrate = discord.Embed(colour=discord.Colour.blue(), timestamp=time)
                bitrate.set_author(name=time.strftime(fmt) + " Voice Channel Bitrate Update",
                                   icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                bitrate.set_thumbnail(
                    url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                infomsg = ":loud_sound: Voice Channel bitrate update. Before: **{}** After: **{}**.".format(
                    before.bitrate, after.bitrate)
                bitrate.add_field(name="Info:", value=infomsg, inline=False)
                try:
                    await sef.bot.send_message(guild.get_channel(channel), embed=bitrate)
                except:
                    pass
            else:
                await guild.get_channel(channel).send(
                                            ":loud_sound: `{}` Channel bitrate update. Before: **{}** After: **{}**.".format(
                                                time.strftime(fmt), before.bitrate, after.bitrate))

    async def on_message_edit(self, before, after):
        guild = before.guild
        db = await self.config.guild(guild).settings()
        if before.author.bot:
            return
        if await self.config.guild(guild).settings() == {}:
            return
        if db['toggleedit'] == False:
            return
        if before.content == after.content:
            return
        cleanbefore = before.content
        for i in before.mentions:
            cleanbefore = cleanbefore.replace(i.mention, str(i))
        cleanafter = after.content
        for i in after.mentions:
            cleanafter = cleanafter.replace(i.mention, str(i))
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        if db["embed"] == True:
            name = before.author
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            
            infomessage = "A message by {}, was edited in {}".format(before.author.mention, before.channel.mention)
            delmessage = discord.Embed(description=infomessage, colour=discord.Color.green(), timestamp=after.created_at)
            delmessage.add_field(name="Before Message:", value=cleanbefore, inline=False)
            delmessage.add_field(name="After Message:", value=cleanafter)
            delmessage.set_footer(text="User ID: {}".format(before.author.id), icon_url=before.author.avatar_url)
            delmessage.set_author(name=name + " - Edited Message", url="http://i.imgur.com/Q8SzUdG.png", icon_url=before.author.avatar_url)
            delmessage.set_thumbnail(url="http://i.imgur.com/Q8SzUdG.png")
            try:
                await guild.get_channel(channel).send( embed=delmessage)
            except:
                pass
        else:
            msg = ":pencil: `{}` **Channel**: {} **{}'s** message has been edited.\nBefore: {}\nAfter: {}".format(
                time.strftime(fmt), before.channel.mention, before.author, cleanbefore, cleanafter)
            await guild.get_channel(channel).send(msg)

    async def on_guild_update(self, before, after):
        guild = before
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['toggleguild'] == False:
            return
        if before.bot:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        if before.name != after.name:
            msg = ":globe_with_meridians: `{}` guild name update. Before: **{}** After: **{}**.".format(
                time.strftime(fmt), before.name, after.name)
        if before.region != after.region:
            msg = ":globe_with_meridians: `{}` guild region update. Before: **{}** After: **{}**.".format(
                time.strftime(fmt), before.region, after.region)
        await guild.get_channel(channel).send(msg)

    async def on_voice_state_update(self, before, after):
        guild = before.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['togglevoice'] == False:
            return
        if before.bot:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        if db["embed"] == True:
            name = before
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            updmessage = discord.Embed(description=name, colour=discord.Color.blue(), timestamp=time)
            infomessage = "__{}__'s voice status has changed".format(before.name)
            updmessage.add_field(name="Info:", value=infomessage, inline=False)
            updmessage.add_field(name="Voice Channel Before:", value=before.voice_channel)
            updmessage.add_field(name="Voice Channel After:", value=after.voice_channel)
            updmessage.set_footer(text="User ID: {}".format(before.id))
            updmessage.set_author(name=time.strftime(fmt) + " - Voice Channel Changed",
                                  url="http://i.imgur.com/8gD34rt.png")
            updmessage.set_thumbnail(url="http://i.imgur.com/8gD34rt.png")
            try:
                await guild.get_channel(channel).send( embed=updmessage)
            except:
                pass
        else:
            await guild.get_channel(channel).send(
                                        ":person_with_pouting_face::skin-tone-3: `{}` **{}'s** voice status has updated. **Channel**: {}\n**Local Mute:** {} **Local Deaf:** {} **guild Mute:** {} **guild Deaf:** {}".format(
                                            time.strftime(fmt), after.name, after.voice_channel, after.self_mute,
                                            after.self_deaf, after.mute, after.deaf))


    async def on_member_update(self, before, after):
        guild = before.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        if not before.roles == after.roles and db['toggleroles']:
            if db["embed"] == True:
                name = after
                name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
                role = discord.Embed(colour=discord.Color.red(), timestamp=time)
                role.add_field(name="Roles Before:", value=" ,".join(role.name for role in before.roles), inline=False)
                role.add_field(name="Roles After:", value=" ,".join(role.name for role in after.roles), inline=False)
                role.set_footer(text="User ID: {}".format(after.id), icon_url=after.avatar_url)
                role.set_author(name=name + " - Updated Roles", icon_url=after.avatar_url)
                # role.set_thumbnail(after)
                try:
                    await guild.get_channel(channel).send( embed=role)
                except:
                    pass
            if db["embed"] == False:
                msg = ":person_with_pouting_face::skin-tone-3: `{}` **{}'s** roles have changed. Old: `{}` New: `{}`".format(
                    time.strftime(fmt), before.name, ", ".join([r.name for r in before.roles]),
                    ", ".join([r.name for r in after.roles]))
                await guild.get_channel(channel).send(
                                            msg)
        if not before.nick == after.nick and db['toggleuser']:
            if db["embed"] == True:
                name = before
                name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
                infomessage = "{}'s nickname has changed".format(before.mention)
                updmessage = discord.Embed(description=infomessage, colour=discord.Color.orange(), timestamp=time)
                updmessage.add_field(name="Nickname Before:", value=before.nick)
                updmessage.add_field(name="Nickname After:", value=after.nick)
                updmessage.set_footer(text="User ID: {}".format(before.id), icon_url=after.avatar_url)
                updmessage.set_author(name=name + " - Nickname Changed", icon_url=after.avatar_url)
                # updmessage.set_thumbnail(url="http://i.imgur.com/I5q71rj.png")
                try:
                    await guild.get_channel(channel).send( embed=updmessage)
                except:
                    pass
            else:
                await guild.get_channel(channel).send(
                                            ":person_with_pouting_face::skin-tone-3: `{}` **{}** changed their nickname from **{}** to **{}**".format(
                                                time.strftime(fmt), before.name, before.nick, after.nick))

    async def on_member_ban(self, member):
        guild = member.guild
        db = await self.config.guild(guild).settings()
        if await self.config.guild(guild).settings() == {}:
            return
        if db['toggleban'] == False:
            return
        channel = db["Channel"]
        time = datetime.datetime.utcnow()
        fmt = '%H:%M:%S'
        if db["embed"] == True:
            name = member
            name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
            
            infomessage = "{} has been banned from the guild.".format(member.mention)
            banmessage = discord.Embed(description=infomessage, colour=discord.Color.red(), timestamp=time)
            banmessage.add_field(name="Info:", value=infomessage, inline=False)
            banmessage.set_footer(text="User ID: {}".format(member.id), icon_url=member.avatar_url)
            banmessage.set_author(name=name + " - Banned User", icon_url=member.avatar_url)
            banmessage.set_thumbnail(url=member.avatar_url)
            try:
                await guild.get_channel(channel).send( embed=banmessage)
            except:
                await guild.get_channel(channel).send(
                                            "How is embed modlog going to work when I don't have embed links permissions?")
        else:
            msg = ":hammer: `{}` {}({}) has been banned!".format(time.strftime(fmt), member, member.id)
            await guild.get_channel(channel).send(msg)
