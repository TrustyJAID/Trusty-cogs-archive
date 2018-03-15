from random import choice, randint
import random
import aiohttp
import discord
import asyncio
from discord.ext import commands
from redbot.core import checks, bank
from redbot.core.utils.chat_formatting import pagify, box
from redbot.core.data_manager import bundled_data_path
from redbot.core.data_manager import cog_data_path
from .data import links, messages
import datetime
import os
import string
import time
import io
from redbot.core.i18n import CogI18n

_ = CogI18n("TrustyBot", __file__)

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class TrustyBot:
    def __init__(self, bot):
        self.bot = bot
        # self.donotdo = dataIO.load_json("data/dnd/donotdo.json")
        self.text = messages
        self.links = links
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def trustyrules(self, ctx):
        rules = """1. Don't be a jerk - We're here to have fun and enjoy music, new bot features, and games!\n
2. No sharing of personal or confidential information - This is a [discord Terms of Service](https://discordapp.com/terms) violation and can result in immediate ban.\n
3. Keep NSFW content in <#412884243195232257> anything outside there deemed NSFW by a mod can and will be deleted as per discords [Community Guidelines](https://discordapp.com/guidelines).\n
4. Do not harass, threaten, or otherwise make another user feel poorly about themselves - This is another [discord TOS](https://discordapp.com/terms) violation.\n
5. Moderator action is at the discretion of a moderator and changes may be made without warning to your privliges.\n
***Any violation of the [discord TOS](https://discordapp.com/terms) or [Community Guidelines](https://discordapp.com/guidelines) will result in immediate banning and possible report to discord.***\n
"""
        em = discord.Embed(colour=discord.Colour.gold())
        em.add_field(name="__RULES__", value=rules)
        em.set_image(url="https://i.imgur.com/6FPYjoU.gif")
        # em.set_thumbnail(url="https://i.imgur.com/EfOnDQy.gif")
        em.set_author(name=ctx.guild.name, icon_url="https://i.imgur.com/EfOnDQy.gif")
        await ctx.message.delete()
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    @checks.is_owner()
    async def checkcheater(self, ctx, user_id):
        is_cheater = False
        for guild in self.bot.guilds:
            print(guild.owner.id)
            if guild.owner.id == user_id:
                is_cheater = True
                await ctx.send("<@{}> is guild owner of {}".format(user_id, guild.name))
        if not is_cheater:
            await ctx.send("Not a cheater")



    async def on_message(self, message):
        if len(message.content) < 2:
            return

        msg = message.content
        channel = message.channel
        guild = message.guild
        if "fuck" in msg.lower():
            if guild is not None:
                if guild.id in [321105104931389440, 402161292644712468]:
                    async with channel.typing():
                        file = discord.File(str(bundled_data_path(self)) + "/christian.jpg")
                        await channel.send(file=file)

        try:
            prefix = await self.get_prefix(message)
        except ValueError:
            return
        alias = await self.first_word(msg[len(prefix):])
        if alias == "beemovie":
            return
        if alias in self.text:
            await channel.trigger_typing()
            await channel.send(self.text[alias])
        if alias in self.links:
            await channel.trigger_typing()
            await channel.send(self.links[alias])
        return

    async def first_word(self, msg):
        return msg.split(" ")[0].lower()

    async def get_prefix(self, message: discord.Message) -> str:
        """
        From Redbot Alias Cog
        Tries to determine what prefix is used in a message object.
            Looks to identify from longest prefix to smallest.
            Will raise ValueError if no prefix is found.
        :param message: Message object
        :return:
        """
        content = message.content
        prefix_list = await self.bot.command_prefix(self.bot, message)
        prefixes = sorted(prefix_list,
                          key=lambda pfx: len(pfx),
                          reverse=True)
        for p in prefixes:
            if content.startswith(p):
                return p
        raise ValueError(_("No prefix found."))

    @commands.command(hidden=True)
    async def say(self, ctx, *, msg):
        print(ctx.message.content)
        await ctx.send(msg)

    @commands.command(aliases=["sl"])
    async def serverleaderboard(self, ctx: commands.Context, top: int = 10):
        """Prints out the leaderboard
        Defaults to top 10"""
        # Originally coded by Airenkun - edited by irdumb, rewritten by Palm__ for v3
        guild = ctx.guild
        if top < 1:
            top = 10
        if await bank.is_global():
            bank_list = [x for x in await bank.get_global_accounts() if guild.get_member_named(x.name) is not None]
            bank_sorted = sorted(bank_list,
                                 key=lambda x: x.balance, reverse=True)
        else:
            bank_sorted = sorted(await bank.get_guild_accounts(guild),
                                 key=lambda x: x.balance, reverse=True)
        if len(bank_sorted) < top:
            top = len(bank_sorted)
        topten = bank_sorted[:top]
        highscore = ""
        place = 1
        for acc in topten:
            dname = str(acc.name)
            if len(dname) >= 23 - len(str(acc.balance)):
                dname = dname[:(23 - len(str(acc.balance))) - 3]
                dname += "... "
            highscore += str(place).ljust(len(str(top)) + 1)
            highscore += dname.ljust(23 - len(str(acc.balance)))
            highscore += str(acc.balance) + "\n"
            place += 1
        if highscore != "":
            for page in pagify(highscore, shorten_by=12):
                await ctx.send(box(page, lang="py"))
        else:
            await ctx.send(_("There are no accounts in the bank."))

    @commands.command()
    async def oof(self, ctx):
        emojis = ["🅾", "🇴", "🇫"]
        channel = ctx.message.channel
        guild = ctx.message.guild
        if not channel.permissions_for(guild.me).manage_messages:
            async for message in channel.history(limit=2):
                msg = message
            for emoji in emojis:
                await message.add_reaction(emoji)
        else:
            await ctx.message.delete()
            async for message in channel.history(limit=1):
                msg = message
            for emoji in emojis:
                await message.add_reaction(emoji)


    @commands.command()
    async def pingtime(self, ctx):
        t1 = time.perf_counter()
        await ctx.channel.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send("pong: {}ms".format(round((t2-t1)*1000)))

    @commands.command(pass_context=True)
    async def emoji(self, ctx, emoji):
        async with ctx.channel.typing():
        # print(emoji)
            if emoji is discord.Emoji:
                emoji_name = emoji.name
                ext = emoji.url.split(".")[-1]
                async with self.session.get(emoji.url) as resp:
                    data = await resp.read()
                file = discord.File(io.BytesIO(data),filename="{}.{}".format(emoji.name, ext))
                await ctx.send(file=file)
                # await self.bot.say(emoji.url)
            else:
                emoji_id = emoji.split(":")[-1].replace(">", "")
                # print(emoji_id)
                if emoji.startswith("<a"):
                    async with self.session.get("https://cdn.discordapp.com/emojis/{}.gif?v=1".format(emoji_id)) as resp:
                        data = await resp.read()
                    file = discord.File(io.BytesIO(data),filename="{}.gif".format(emoji_id))
                else:
                    async with self.session.get("https://cdn.discordapp.com/emojis/{}.png?v=1".format(emoji_id)) as resp:
                        data = await resp.read()
                    file = discord.File(io.BytesIO(data),filename="{}.png".format(emoji_id))
                await ctx.send(file=file)


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def testcu(self, ctx, *, category):
        guild = ctx.message.guild
        for cat in guild.categories:
            if category.lower() == cat.name.lower():
                category = cat
                break
        channel = await guild.create_text_channel("test", category=category)
        print(channel.id)


    @commands.command(pass_context=True)
    async def avatar(self, ctx, member:discord.Member=None):
        async with ctx.channel.typing():
            if member is None:
                member = ctx.message.author
            if member.is_avatar_animated():
                async with self.session.get(member.avatar_url_as(format="gif")) as resp:
                    data = await resp.read()
                file = discord.File(io.BytesIO(data),filename="{}.gif".format(member.name))
            if not member.is_avatar_animated():
                async with self.session.get(member.avatar_url_as(static_format="png")) as resp:
                    data = await resp.read()
                file = discord.File(io.BytesIO(data),filename="{}.png".format(member.name))
            await ctx.send(file=file)


    @commands.command(pass_context=True, aliases=["guildhelp", "serverhelp", "helpserver"])
    async def helpguild(self, ctx):
        await ctx.send("https://discord.gg/wVVrqej")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def members(self, ctx, guild_id:int=None):
        if guild_id is not None:
            guild = self.bot.get_guild(id=guild_id)
        else:
            guild = ctx.message.guild
        member_list = sorted(guild.members, key=lambda m: m.joined_at)
        new_msg = ""
        for member in member_list[:10]:
            new_msg += "{}. {}\n".format((member_list.index(member)+1), member.name)
        await ctx.send(new_msg)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def createchannel(self, ctx, name:str, position:int):
        chn = await self.bot.create_channel(ctx.message.guild, name)
        await self.bot.move_channel(chn, position)
        await ctx.send(chn.position)

    
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def listchannels(self, ctx, guild_id:discord.guild=None):
        if guild_id is None:
            guild = ctx.message.guild
        else:
            guild = guild_id
        channels = {}
        for channel in guild.channels:
            for channel in guild.channels:
                channels[channel.name] = {"id":channel.id, "pos":channel.position}
        await ctx.send("{} ({}): {}".format(guild.name, guild.id, channels))

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
        created_at = ("Since {}. That's over {} days ago!"
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
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"]
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

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def getguild(self, ctx):
        guilds = [guild for guild in self.bot.guilds]
        await self.guild_menu(ctx, guilds)

    
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def nummembers(self, ctx, *, guildname):
        channels = {}
        for guild in self.bot.guilds:
            if guild.name == guildname:
                await ctx.send(len(guild.members))

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def makeinvite(self, ctx, guild_id):
        guild = self.bot.get_guild(id=guild_id)
        invites = []
        for channel in guild.channels:
            try:
                invite = await self.bot.create_invite(channel)
                invites.append(invite.url)
            except:
                pass
        await ctx.send(invites)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def massinvite(self, ctx, guild_id=None):

        invites = []
        for guild in self.bot.guilds:
            made_invite = False
            members = [member.id for member in guild.members]
            if "218773382617890828" not in members:
                print(guild.name)
                for channel in guild.channels:
                    if made_invite:
                        continue
                    if channel.type == discord.ChannelType.text:
                        try:
                            invite = await self.bot.create_invite(channel, unique=False)
                            invites.append(invite.url)
                            made_invite = True
                        except:
                            made_invite = False
                            pass

        await ctx.send(invites)
    
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def getguildid(self, ctx):
        msg = ""
        num = 1
        for guild in self.bot.guilds:
            msg += "{}. {}: {}\n".format(num, guild.name, guild.id)
            num += 1
        await ctx.send(msg)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def getroles(self, ctx):
        guild = ctx.message.guild
        msg = ""
        for role in guild.roles:
            msg += (role.name + ",")
        await ctx.send(msg)

    async def emoji_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        emojis = post_list[page]
        guild = ctx.message.guild
        em = discord.Embed(timestamp=ctx.message.created_at)
        em.set_author(name=guild.name, icon_url=guild.icon_url)
        regular = []
        msg = ""
        for emoji in emojis:
            msg += emoji
        em.add_field(name="Emojis", value=msg)
        em.set_footer(text="Page {} of {}".format(page+1, len(post_list)))
        
        if not message:
            message = await ctx.send(embed=em)
            await message.add_reaction("⬅")
            await message.add_reaction("❌")
            await message.add_reaction("➡")
        else:
            # message edits don't return the message object anymore lol
            await message.edit(embed=em)
        check = lambda react, user:user == ctx.message.author and react.emoji in ["➡", "⬅", "❌"]
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

    @commands.command(pass_context=True, aliases=["serveremojis"])
    async def guildemojis(self, ctx, *, guildname=None):
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

    @commands.command()
    async def beemovie(self, ctx):
        msg = "<a:beemovie1_1:394355466022551552><a:beemovie1_2:394355486625103872><a:beemovie1_3:394355526496026624><a:beemovie1_4:394355551859113985><a:beemovie1_5:394355549581606912><a:beemovie1_6:394355542849617943><a:beemovie1_7:394355537925373952><a:beemovie1_8:394355511912300554>\n<a:beemovie2_1:394355541616361475><a:beemovie2_2:394355559719239690><a:beemovie2_3:394355587409772545><a:beemovie2_4:394355593567272960><a:beemovie2_5:394355578337624064><a:beemovie2_6:394355586067726336><a:beemovie2_7:394355558104432661><a:beemovie2_8:394355539716472832>\n<a:beemovie3_1:394355552626409473><a:beemovie3_2:394355572381843459><a:beemovie3_3:394355594955456532><a:beemovie3_4:394355578253737984><a:beemovie3_5:394355579096793098><a:beemovie3_6:394355586411528192><a:beemovie3_7:394355565788397568><a:beemovie3_8:394355551556861993>\n<a:beemovie4_1:394355538181488640><a:beemovie4_2:394355548944072705><a:beemovie4_3:394355568669884426><a:beemovie4_4:394355564504809485><a:beemovie4_5:394355567843606528><a:beemovie4_6:394355577758679040><a:beemovie4_7:394355552655900672><a:beemovie4_8:394355527867564032>"
        em = discord.Embed(title="The Entire Bee Movie", description=msg)
        await ctx.send(embed=em)

    
    @commands.command()
    async def listtext(self):
        """List phrases added to bot"""
        msg = ""
        for text in self.text.keys():
            msg += text + ", "
        await ctx.send("```" + msg[:len(msg)-2] + "```")
    
    @commands.command()
    async def listlinks(self):
        """List links added to bot"""
        msg = ""
        for link in self.links.keys():
            msg += link + ", "
        await ctx.send("```" + msg[:len(msg)-2] + "```")
    
    @commands.command(pass_context=True)
    async def neat(self, ctx, number:int=None):
        """Neat"""
        files = str(cog_data_path(self)) + "/bundled_data/neat{}.gif"
        if number is None:
            image = discord.File(files.format(str(choice(range(1, 6)))))
            await ctx.send(file=image)
        elif(int(number) > 0 or int(number) < 8):
            image = discord.File(files.format(number))
            await ctx.send(file=image)

    @commands.command(pass_context=True)
    async def reviewbrah(self, ctx):
        """Reviewbrah"""
        files = ["/bundled_data/revi.png", "/bundled_data/ew.png", "/bundled_data/brah.png"]
        print(cog_data_path(self))
        for file in files:
            data = discord.File(str(cog_data_path(self))+file)
            await ctx.send(file=data)


    @commands.command(pass_context=True,)
    async def donate(self, ctx):
        """Donate to the development of TrustyBot!"""
        await ctx.send("Help support me  and development of TrustyBot by buying my album or donating bitcoin on my website :smile: https://trustyjaid.com/")

    
    @commands.command(pass_context=True)
    async def dnd(self, ctx, number=None):
        if number is None:
            await ctx.send(choice(self.donotdo))
        elif number.isdigit():
            await ctx.send(self.donotdo[int(number)-1])
        else:
            await ctx.send(choice(self.donotdo))

    @commands.command(hidden=False)
    async def halp(self,ctx, user=None):
        """How to ask for help!"""
        msg = "{} please type `;help` to be PM'd all my commands! :smile: or type `;guildhelp` to get an invite and I can help you personally."
        if user is None:
            await ctx.send(msg.format(""))
        else:
            await ctx.send(msg.format(user))

    @commands.command(hidden=False)
    async def dreams(self):
        """don't let your dreams be dreams"""
        await ctx.send(self.text["dreams"].format("dreams"))

    @commands.command(hidden=False)
    async def memes(self):
        """don't let your memes be dreams"""
        await ctx.send(self.text["dreams"].format("memes"))

    @commands.command(pass_context=True)
    async def flipm(self, ctx, *, message):
        """Flips a message"""
        msg = ""
        name = ""
        for user in message:
            char = "abcdefghijklmnopqrstuvwxyz - ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz - ∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name += user.translate(table) + " "
        await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
    