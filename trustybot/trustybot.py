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
from .data import links, messages, donotdo
import datetime
import os
import string
import time
import io
from redbot.core.i18n import Translator
from redbot.core.utils.chat_formatting import pagify, box

_ = Translator("TrustyBot", __file__)

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}


class TrustyBot:
    def __init__(self, bot):
        self.bot = bot
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
    async def oilersrules(self, ctx):
        rules = """1. Don't be a *complete* jerk - We're here to have fun and discuss the <@&381573564408791040> and their Triumphs and Defeats!\n
2. No sharing of personal or confidential information of others - This is a [discord Terms of Service](https://discordapp.com/terms) violation and can result in immediate ban.\n
3. Anything deemed NSFW by a <@&381578067304251404> can and will be deleted as per discords [Community Guidelines](https://discordapp.com/guidelines).\n
4. Do not harass or threaten other memebers, this extends to other discord servers - This is another [discord TOS](https://discordapp.com/terms) violation.\n
5. <@&381578067304251404> action is at the discretion of a <@&381578067304251404> and changes may be made without warning to your privliges. Don't get any penalty's.\n
***Any violation of the [discord TOS](https://discordapp.com/terms) or [Community Guidelines](https://discordapp.com/guidelines) will result in immediate banning and possible report to discord.***\n
"""
        roles = """Type `;hockey role <teamname, division, or conference>` in <#381582160710205441> to get the specified team role and colour and access to live goal update channels\n
Type `;hockey goals <teamname>` in <#381582160710205441> to get notifications on team goals
"""
        em = discord.Embed(colour=int("FF4C00", 16))
        em.add_field(name="__RULES__", value=rules)
        em.add_field(name="__Teams/Roles__", value=roles)
        # em.set_image(url="https://nhl.bamcontent.com/images/photos/281721030/256x256/cut.png")
        em.set_thumbnail(url="https://nhl.bamcontent.com/images/photos/281721030/256x256/cut.png")
        em.set_author(name=ctx.guild.name, icon_url="https://nhl.bamcontent.com/images/photos/281721030/256x256/cut.png")
        await ctx.message.delete()
        await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def warfarerules(self, ctx):
        rules = """1. **Meme Warfare** is your "*File Cabinet*" for members to *deposit* and *withdraw* memes. If you would like to post memes, ask an <@&402164942192640001> for the *Poster* role.\n
2. The meme channels are ***ONLY*** for Memes. We would like to keep the channels free from conversations as we need to grab the memes and "go fast".\n
3. Wanna be extra-comfy? Click on the subject/category headers to collapse them. Right Click -> Mark as Read -> Collapse Channels is another way to accomplish this.\n
4. Right Click -> Mute channels that don't interest you so that you won't keep receiving notifications.\n
5. <#407705381922537483>/<#424742925474332683> chat is available for striking up conversations about current events and various non-Q-related topics.\n
6. No sharing of personal or confidential information of others - This is a [discord Terms of Service](https://discordapp.com/terms) violation and can result in immediate ban.\n
7. Do not harass or threaten other members, this extends to other discord servers - This is another [discord TOS](https://discordapp.com/terms) violation.\n
8. <@&402164942192640001> action is at the discretion of an <@&402164942192640001> and changes may be made without warning to your privileges.\n
***Any violation of the [discord TOS](https://discordapp.com/terms) or [Community Guidelines](https://discordapp.com/guidelines) will result in immediate banning and possible report to Discord.***\n
"""
        roles = """**Q-RESEARCH**: Q-related research goes in this channel. Remember to always provide "links/sauce" for your research. Images drops must include an article reference.\n
**TRAINING-HOW-TO-MEME**: Teach people how to create memes and instruct others on the purpose of a meme.\n
"""
        rules_3 = """**HIGHEST PRIORITY**: Hottest memes in rotation.\n
**MEMEWORTHY**: Memes that are very relevant. These could move to *HIGHEST PRIORITY* or *DUSTY MEMES*\n
**HOLLYWOOD**: Memes about the corruption in the entertainment industry.\n
**OPERATION MOCKINGBIRD**: Memes about *Fake News* and the *Shadow Government* pushing the narrative.\n
**POLITICS**: Memes about politicians by name.\n
**DUSTY MEMES**: Memes that have lost relevance with current events. These could still return to *HIGHEST PRIORITY* or *MEMEWORTHY*.\n
**OPERATION REDPILL**: How to redpill individuals in real life.\n
        """
        em = discord.Embed(colour=int("1975e1", 16))
        em.title = "__**BASIC OPERATIONS**__"
        em.description = rules
        # em.add_field(name="__**BASIC OPERATIONS**__", value=rules)
        em.add_field(name="__**TOP CATEGORIES**__", value=roles)
        em.add_field(name="__**MEME CATEGORIES**__", value=rules_3)
        # em.set_image(url="https://nhl.bamcontent.com/images/photos/281721030/256x256/cut.png")
        em.set_thumbnail(url=ctx.message.guild.icon_url)
        em.set_author(name=ctx.guild.name, icon_url=ctx.message.guild.icon_url)
        await ctx.message.delete()
        if ctx.message.guild.id == 402161292644712468:
            await ctx.send(embed=em)


    @commands.command(hidden=True)
    @checks.is_owner()
    async def msg(self, ctx, *, msg):
        print(msg)

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
        if alias in messages:
            await channel.trigger_typing()
            await channel.send(messages[alias])
        if alias in links:
            await channel.trigger_typing()
            await channel.send(links[alias])
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
        # print(emoji)
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
    async def createchannel(self, ctx, name:str, position:int):
        chn = await self.bot.create_channel(ctx.message.guild, name)
        await self.bot.move_channel(chn, position)
        await ctx.send(chn.position)

    
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def makeinvite(self, ctx, guild_id:int):
        guild = self.bot.get_guild(id=guild_id)
        invites = None
        for channel in guild.text_channels:
            if invites is not None:
                break
            try:
                invite = await self.bot.create_invite(channel)
                invites = invite.url
            except:
                pass
        if invites is not None:
            await ctx.send(invites)
        else:
            await ctx.send("Can't make any invites")

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

    @commands.command()
    async def beemovie(self, ctx):
        msg = "<a:bm1_1:394355466022551552><a:bm1_2:394355486625103872><a:bm1_3:394355526496026624><a:bm1_4:394355551859113985><a:bm1_5:394355549581606912><a:bm1_6:394355542849617943><a:bm1_7:394355537925373952><a:bm1_8:394355511912300554>\n<a:bm2_1:394355541616361475><a:bm2_2:394355559719239690><a:bm2_3:394355587409772545><a:bm2_4:394355593567272960><a:bm2_5:394355578337624064><a:bm2_6:394355586067726336><a:bm2_7:394355558104432661><a:bm2_8:394355539716472832>\n<a:bm3_1:394355552626409473><a:bm3_2:394355572381843459><a:bm3_3:394355594955456532><a:bm3_4:394355578253737984><a:bm3_5:394355579096793098><a:bm3_6:394355586411528192><a:bm3_7:394355565788397568><a:bm3_8:394355551556861993>\n<a:bm4_1:394355538181488640><a:bm4_2:394355548944072705><a:bm4_3:394355568669884426><a:bm4_4:394355564504809485><a:bm4_5:394355567843606528><a:bm4_6:394355577758679040><a:bm4_7:394355552655900672><a:bm4_8:394355527867564032>"
        em = discord.Embed(title="The Entire Bee Movie", description=msg)
        await ctx.send(embed=em)

    
    @commands.command()
    async def listtext(self):
        """List phrases added to bot"""
        msg = ""
        for text in messages.keys():
            msg += text + ", "
        await ctx.send("```" + msg[:len(msg)-2] + "```")
    
    @commands.command()
    async def listlinks(self):
        """List links added to bot"""
        msg = ""
        for link in links.keys():
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

    
    @commands.command(pass_context=True, aliases=["dnd"])
    async def donotdo(self, ctx, number=None):
        if number is None:
            await ctx.send(choice(donotdo))
        elif number.isdigit():
            await ctx.send(donotdo[int(number)-1])
        else:
            await ctx.send(choice(donotdo))

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
        await ctx.send(messages["dreams"].format("dreams"))

    @commands.command(hidden=False)
    async def memes(self):
        """don't let your memes be dreams"""
        await ctx.send(messages["dreams"].format("memes"))

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
    