from random import choice, randint
import discord
import asyncio
from redbot.core import commands
from redbot.core import checks, bank, Config
import datetime
import aiohttp
from io import BytesIO
from redbot.core.i18n import Translator
from redbot.core.utils.chat_formatting import pagify, box
from typing import Union

_ = Translator("ServerStats", __file__)

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class ServerStats(getattr(commands, "Cog", object)):

    def __init__(self, bot):
        self.bot = bot
        default_global = {"join_channel":None}
        self.config = Config.get_conf(self, 54853421465543)
        self.config.register_global(**default_global)
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    async def on_guild_join(self, guild):
        channel_id = await self.config.join_channel()
        if channel_id is None:
            return
        channel = self.bot.get_channel(channel_id)
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(guild.members)
        text_channels = len([x for x in guild.text_channels])
        voice_channels = len([x for x in guild.voice_channels])
        passed = (datetime.datetime.utcnow() - guild.created_at).days
        created_at = _("{} has joined a new server!\n That's {} servers now! \nServer created {}. That's over {} days ago!".format(
                        channel.guild.me.mention,
                        len(self.bot.guilds),
                        guild.created_at.strftime("%d %b %Y %H:%M"),
                        passed))

        colour = guild.roles[-1].colour

        em = discord.Embed(
            description=created_at,
            colour=colour,
            timestamp=guild.created_at)
        em.add_field(name="Region", value=str(guild.region))
        em.add_field(name="Users", value="{}/{}".format(online, total_users))
        em.add_field(name="Text Channels", value=text_channels)
        em.add_field(name="Voice Channels", value=voice_channels)
        em.add_field(name="Roles", value=len(guild.roles))
        em.add_field(name="Owner", value="{} | {}".format(str(guild.owner), guild.owner.mention))
        if guild.features != []:
            em.add_field(name="Guild Features", value=", ".join(feature for feature in guild.features))
        em.set_footer(text="guild ID: {}".format(guild.id))
        em.set_author(name=guild.name, icon_url=guild.icon_url_as(format="png"))
        em.set_thumbnail(url=guild.icon_url_as(format="png"))
        await channel.send(embed=em)

    async def on_guild_remove(self, guild):
        channel_id = await self.config.join_channel()
        if channel_id is None:
            return
        channel = self.bot.get_channel(channel_id)
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(guild.members)
        text_channels = len([x for x in guild.text_channels])
        voice_channels = len([x for x in guild.voice_channels])
        passed = (datetime.datetime.utcnow() - guild.created_at).days
        created_at = _("{} has left a server!\n That's {} servers now! \nServer created {}. That's over {} days ago!".format(
                        channel.guild.me.mention,
                        len(self.bot.guilds),
                        guild.created_at.strftime("%d %b %Y %H:%M"),
                        passed))

        colour = guild.roles[-1].colour

        em = discord.Embed(
            description=created_at,
            colour=colour,
            timestamp=guild.created_at)
        em.add_field(name="Region", value=str(guild.region))
        em.add_field(name="Users", value="{}/{}".format(online, total_users))
        em.add_field(name="Text Channels", value=text_channels)
        em.add_field(name="Voice Channels", value=voice_channels)
        em.add_field(name="Roles", value=len(guild.roles))
        em.add_field(name="Owner", value="{} | {}".format(str(guild.owner), guild.owner.mention))
        if guild.features != []:
            em.add_field(name="Guild Features", value=", ".join(feature for feature in guild.features))
        em.set_footer(text="guild ID: {}".format(guild.id))
        em.set_author(name=guild.name, icon_url=guild.icon_url_as(format="png"))
        em.set_thumbnail(url=guild.icon_url_as(format="png"))

        await channel.send(embed=em)

    @commands.command(pass_context=True)
    async def emoji(self, ctx, emoji):
        """
            Post a large size server emoji in chat
        """
        if emoji is discord.Emoji:
            await ctx.channel.trigger_typing()
            emoji_name = emoji.name
            ext = emoji.url.split(".")[-1]
            async with self.session.get(emoji.url) as resp:
                data = await resp.read()
            file = discord.File(io.BytesIO(data),filename="{}.{}".format(emoji.name, ext))
            await ctx.send(file=file)
            # await self.bot.say(emoji.url)
        else:
            emoji_id = emoji.split(":")[-1].replace(">", "")
            if not emoji_id.isdigit():
                return
            await ctx.channel.trigger_typing()
            # print(emoji_id)
            if emoji.startswith("<a"):
                async with self.session.get("https://cdn.discordapp.com/emojis/{}.gif?v=1".format(emoji_id)) as resp:
                    data = await resp.read()
                file = discord.File(BytesIO(data),filename="{}.gif".format(emoji_id))
            else:
                async with self.session.get("https://cdn.discordapp.com/emojis/{}.png?v=1".format(emoji_id)) as resp:
                    data = await resp.read()
                file = discord.File(BytesIO(data),filename="{}.png".format(emoji_id))
            await ctx.send(file=file)

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member:discord.Member=None):
        """
            Display a users avatar in chat
        """
        if member is None:
            member = ctx.message.author
        guild = ctx.message.guild
        if guild is not None:
            colour = member.top_role.colour
        else:
            colour = discord.Embed.Empty
        await ctx.channel.trigger_typing()
        em = discord.Embed(title="**Avatar**", colour=colour)
        if member.is_avatar_animated():
            url = member.avatar_url_as(format="gif")
        if not member.is_avatar_animated():
            url = member.avatar_url_as(static_format="png")
        em.set_image(url= url)
        em.set_author(name="{}#{}".format(member.name, member.discriminator), icon_url=url, url=url)
        await ctx.send(embed=em)

    @commands.command()
    @checks.is_owner()
    async def setguildjoin(self, ctx, channel:discord.TextChannel=None):
        """Set a channel to see new servers the bot is joining"""
        if channel is None:
            channel = ctx.message.channel
        await self.config.join_channel.set(channel.id)
        await ctx.send("Posting new servers and left servers in {}".format(channel.mention))

    @commands.command()
    @checks.is_owner()
    async def removeguildjoin(self, ctx):
        """Set a channel to see new servers the bot is joining"""
        await self.config.join_channel.set(None)
        await ctx.send("No longer posting joined or left servers.")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def checkcheater(self, ctx, user_id):
        """Checks for possible cheaters abusing the global bank and server powers"""
        is_cheater = False
        for guild in self.bot.guilds:
            print(guild.owner.id)
            if guild.owner.id == user_id:
                is_cheater = True
                await ctx.send("<@{}> is guild owner of {}".format(user_id, guild.name))
        if not is_cheater:
            await ctx.send("Not a cheater")

    @commands.command(hidden=True)
    @checks.is_owner()
    async def whois(self, ctx, member:Union[int, discord.User]):
        """Shows if a user is on any other servers the bot is on"""
        if type(member) == int:
            try:
                member = await self.bot.get_user_info(member)
            except discord.errors.NotFound:
                await ctx.send(f"{member} doesn't seem to be a discord user.")
                return
        guild_list = []
        for guild in self.bot.guilds:
            members = [member.id for member in guild.members]
            if member.id in members:
                guild_list.append(guild)
        if guild_list != []:
            msg = "{} ({}) is on:\n".format(member.name, member.id)
            for guild in guild_list:
                msg += "{} ({})\n".format(guild.name, guild.id)
            for page in pagify(msg, ["\n"]):
                await ctx.send(page)
        else:
            msg = f"{member.name}#{member.discriminator} ({member.id}) is not in any shared servers!"
            await ctx.send(msg)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def topservers(self, ctx):
        """Lists servers by number of users and shows number of users"""
        owner = ctx.author
        guilds = sorted(list(self.bot.guilds),
                        key=lambda s: len(s.members), reverse=True)
        msg = ""
        for i, server in enumerate(guilds):
            msg += "{}: {}\n".format(server.name, len(server.members))

        for page in pagify(msg, ['\n']):
            await ctx.send(page)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def newservers(self, ctx):
        """Lists servers by when the bot was added to the server"""
        owner = ctx.author
        guilds = sorted(list(self.bot.guilds),
                        key=lambda s: s.me.joined_at)
        msg = ""
        for i, server in enumerate(guilds):
            msg += "{}: {} ({})\n".format(i, server.name, server.id)

        for page in pagify(msg, ['\n']):
            await ctx.send(page)

    @commands.command()
    @checks.is_owner()
    async def topmembers(self, ctx, number:int=10, guild_id:int=None):
        """Lists top 10 members on the server by join date"""
        if guild_id is not None:
            guild = self.bot.get_guild(id=guild_id)
        else:
            guild = ctx.message.guild
        member_list = sorted(guild.members, key=lambda m: m.joined_at)
        new_msg = ""
        for member in member_list[:number]:
            new_msg += "{}. {}\n".format((member_list.index(member)+1), member.name)

        for page in pagify(new_msg, ['\n']):
            await ctx.send(page)
    
    @commands.command()
    @checks.is_owner()
    async def listchannels(self, ctx, guild_id:discord.guild=None):
        """Lists channels and their position and ID for a server"""
        if guild_id is None:
            guild = ctx.message.guild
        else:
            guild = guild_id
        channels = {}
        msg = "__**{}({})**__\n".format(guild.name, guild.id)
        for channel in guild.channels:
            msg += "{} ({}): {}\n".format(channel.mention, channel.id, channel.position)
        for page in pagify(msg, ["\n"]):
            await ctx.send(page)

    async def guild_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        guild = post_list[page]
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(guild.members)
        text_channels = len([x for x in guild.text_channels])
        voice_channels = len([x for x in guild.voice_channels])
        passed = (ctx.message.created_at - guild.created_at).days
        created_at = _("Since {}. That's over {} days ago!"
                      "".format(guild.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        invite_link = "https://discord.trustyjaid.com"

        em = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour),
            timestamp=guild.created_at)
        em.add_field(name="Region", value=str(guild.region))
        em.add_field(name="Users", value="{}/{}".format(online, total_users))
        em.add_field(name="Text Channels", value=text_channels)
        em.add_field(name="Voice Channels", value=voice_channels)
        em.add_field(name="Roles", value=len(guild.roles))
        em.add_field(name="Owner", value="{} | {}".format(str(guild.owner), guild.owner.mention))
        if guild.features != []:
            em.add_field(name="Guild Features", value=", ".join(feature for feature in guild.features))
        em.set_footer(text="guild ID: {}".format(guild.id))

        if guild.icon_url:
            em.set_author(name=guild.name, url=invite_link, icon_url=guild.icon_url)
            em.set_thumbnail(url=guild.icon_url)
        else:
            em.set_author(name=guild.name)           
        
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"] and react.message.id == message.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.remove_reaction("⬅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)
            await message.remove_reaction("➡", self.bot.user)
            return None
        else:
            reacts = {v: k for k, v in numbs.items()}
            react = reacts[react.emoji]
            if react == "next":
                next_page = 0
                if page == len(post_list) - 1:
                    next_page = 0  # Loop around to the first item
                else:
                    next_page = page + 1
                try:
                    await message.remove_reaction("➡", ctx.message.author)
                except:
                    pass
                return await self.guild_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            elif react == "back":
                next_page = 0
                if page == 0:
                    next_page = len(post_list) - 1  # Loop around to the last item
                else:
                    next_page = page - 1
                try:
                    await message.remove_reaction("⬅", ctx.message.author)
                except:
                    pass
                return await self.guild_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            else:
                return await message.delete()

    @commands.command()
    @checks.is_owner()
    async def getguild(self, ctx, guild_name:Union[int, str]=None):
        """Menu to view info on all servers the bot is on"""
        guilds = [guild for guild in self.bot.guilds]
        page = 0
        if guild_name is not None:
            if type(guild_name) == int:
                page_guild = [guild for guild in self.bot.guilds if int(guild_name) == guild.id]
            if type(guild_name) == str:
                page_guild = [guild for guild in self.bot.guilds if guild_name.lower() in guild.name.lower()]
        try:
            if guild_name is not None:
                page = guilds.index(page_guild[0])
        except IndexError as e:
            await ctx.send("{} guild was not found.".format(guild_name))
            return

        await self.guild_menu(ctx, guilds, None, page)

    
    @commands.command()
    @checks.is_owner()
    async def nummembers(self, ctx, *, guild_name=None):
        """Checks the number of members on the server"""
        if guild_name is not None:
            for guild in self.bot.guilds:
                if guild.name == guild_name:
                    await ctx.send(len(guild.members))
        else:
            guild = ctx.message.guild
            await ctx.send(len(guild.members))

    @commands.command()
    @checks.is_owner()
    async def getroles(self, ctx):
        """
            Displays all roles and their associated ID in chat
        """
        guild = ctx.message.guild
        msg = ""
        for role in guild.roles:
            msg += ("{} ({})\n".format(role.name, role.id))

        for page in pagify(msg, ["\n"]):
            await ctx.send(page)

    @commands.command()
    async def rolestats(self, ctx):
        """
            Display number of members in each role by role hierarchy 
        """
        guild = ctx.message.guild
        msg = ""
        for role in sorted(guild.roles, reverse=True):
            msg += "{}: {} \n".format(role.mention, len(role.members))
        for page in pagify(msg, ["\n"]):
            em = discord.Embed(description=page)
            await ctx.send(embed=em)

    async def check_highest(self, data):
        highest = 0
        users = 0
        for user, value in data.items():
            if value > highest:
                highest = value
                users = user
        return highest, users

    @commands.command(name="getreactions", aliases=["getreaction"])
    @checks.mod_or_permissions(manage_messages=True)
    async def get_reactions(self, ctx, message_id:int, channel:discord.TextChannel=None):
        """
            Gets a list of all reactions from specified message and displays the user ID,
            Username, and Discriminator and the emoji name.
        """
        if channel is None:
            channel = ctx.message.channel
        msg = await channel.get_message(message_id)
        new_msg = ""
        for reaction in msg.reactions:
            async for user in reaction.users():
                if type(reaction.emoji) is not str:
                    new_msg += "{} {}#{} {}\n".format(user.id, user.name, user.discriminator, reaction.emoji.name)
                else:
                    new_msg += "{} {}#{} {}\n".format(user.id, user.name, user.discriminator, reaction.emoji)
        for page in pagify(new_msg, shorten_by=20):
            await ctx.send("```py\n{}\n```".format(page))


    @commands.command(aliases=["serverstats"])
    @checks.mod_or_permissions(manage_messages=True)
    async def server_stats(self, ctx, *, guild_id:int=None):
        """Gets total messages on the server and per-channel basis as well as most single user posts"""
        if guild_id is None:
            guild = ctx.message.guild
        else:
            for guilds in self.bot.guilds:
                if guild_id == guilds.id:
                    guild = guilds
        channel = ctx.message.channel
        total_msgs = 0
        msg = ""
        total_contribution = {}
        warning_msg = await ctx.send(_("This might take a while!"))
        async with ctx.channel.typing():
            for chn in guild.channels:
                channel_msgs = 0
                channel_contribution = {}
                try:
                    async for message in chn.history(limit=10000000):
                        author = message.author
                        channel_msgs += 1
                        total_msgs += 1
                        if author.id not in channel_contribution:
                            channel_contribution[author.id] = 1
                        else:
                            channel_contribution[author.id] += 1

                        if author.id not in total_contribution:
                            total_contribution[author.id] = 1
                        else:
                            total_contribution[author.id] += 1
                    highest, users = await self.check_highest(channel_contribution)
                    msg += "{}: Total Messages:**{}**   most user posts **{}**\n".format(chn.mention, channel_msgs, highest)
                except discord.errors.Forbidden:
                    pass
                except AttributeError:
                    pass
            highest, users = await self.check_highest(total_contribution)
            new_msg = "__{}__: Total Messages:**{}**  Most user posts **{}**\n{}".format(guild.name, total_msgs, highest, msg)
            await warning_msg.delete()
            for page in pagify(new_msg, ["\n"]):
                await channel.send(page)


    async def emoji_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        emojis = post_list[page]
        guild = ctx.message.guild
        em = discord.Embed(timestamp=ctx.message.created_at)
        em.set_author(name=guild.name + " Emojis", icon_url=guild.icon_url)
        regular = []
        msg = ""
        for emoji in emojis:
            msg += emoji
        em.description = msg
        em.set_footer(text="Page {} of {}".format(page+1, len(post_list)))
        
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"] and react.message.id == message.id
        try:
            react, user = await self.bot.wait_for("reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            await message.remove_reaction("⬅", self.bot.user)
            await message.remove_reaction("❌", self.bot.user)
            await message.remove_reaction("➡", self.bot.user)
            return None
        else:
            reacts = {v: k for k, v in numbs.items()}
            react = reacts[react.emoji]
            if react == "next":
                next_page = 0
                if page == len(post_list) - 1:
                    next_page = 0  # Loop around to the first item
                else:
                    next_page = page + 1
                try:
                    await message.remove_reaction("➡", ctx.message.author)
                except:
                    pass
                return await self.emoji_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            elif react == "back":
                next_page = 0
                if page == 0:
                    next_page = len(post_list) - 1  # Loop around to the last item
                else:
                    next_page = page - 1
                try:
                    await message.remove_reaction("⬅", ctx.message.author)
                except:
                    pass
                return await self.emoji_menu(ctx, post_list, message=message,
                                             page=next_page, timeout=timeout)
            else:
                return await message.delete()

    @commands.command(aliases=["serveremojis"])
    async def guildemojis(self, ctx, *, guildname=None):
        """
            Display all server emojis in a menu that can be scrolled through
        """
        msg = ""
        guild = None
        if guildname is not None:
            for guilds in self.bot.guilds:
                if guilds.name == guildname:
                    guild = guilds
        else:
            guild = ctx.message.guild

        if guild is None:
            ctx.send("I don't see that guild!")
            return
        
        embed = discord.Embed(timestamp=ctx.message.created_at)
        embed.set_author(name=guild.name, icon_url=guild.icon_url)
        regular = []
        for emoji in guild.emojis:
            if emoji.animated:
                regular.append("<a:{emoji.name}:{emoji.id}> = `:{emoji.name}:`\n".format(emoji=emoji))
            else:
                regular.append("<:{emoji.name}:{emoji.id}> = `:{emoji.name}:`\n".format(emoji=emoji))
        if regular != "":
            embed.description = regular
        chunks, chunk_size = len(regular), len(regular)//4
        x = [regular[i:i+chunk_size] for i in range(0, chunks, chunk_size)]
        # if animated != "":
            # embed.add_field(name="Animated Emojis", value=animated[:1023])
        await self.emoji_menu(ctx, x)

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
