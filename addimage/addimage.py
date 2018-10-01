from random import choice, randint
import random
import aiohttp
import discord
import asyncio
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config
from redbot.core.data_manager import cog_data_path
from pathlib import Path
import os
import string
from .imageentry import ImageEntry
from redbot.core.i18n import Translator

_ = Translator("Alias", __file__)

class AddImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.images = dataIO.load_json("data/addimage/settings.json")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        temp_folder = cog_data_path(self) /"global"
        temp_folder.mkdir(exist_ok=True, parents=True)
        default_global = {"images":[]}
        default_guild = {"images":[]}
        self.config = Config.get_conf(self, 16446735546)
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

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

    async def part_of_existing_command(self, alias):
        '''Command or alias'''
        command = self.bot.get_command(alias)
        return command is not None


    async def make_guild_folder(self, directory):
        if not directory.is_dir():
            print("Creating guild folder")
            directory.mkdir(exist_ok=True, parents=True)

    async def get_image(self, alias, guild, is_global:bool)-> ImageEntry:
        if is_global:
            list_images = await self.config.images()
            for image in await self.config.images():
                if image["command_name"].lower() == alias.lower():
                    list_images.remove(image)
                    image["count"] += 1
                    list_images.append(image)
                    await self.config.images.set(list_images)
                    return ImageEntry.from_json(image)
        else:
            list_images = await self.config.guild(guild).images()
            for image in await self.config.guild(guild).images():
                # print(image)
                if image["command_name"].lower() == alias.lower():
                    list_images.remove(image)
                    image["count"] += 1
                    list_images.append(image)
                    await self.config.images.set(list_images)
                    return ImageEntry.from_json(image)


    async def on_message(self, message):
        if len(message.content) < 2 or message.guild is None:
            return

        msg = message.content
        guild = message.guild
        channel = message.channel
        try:
            prefix = await self.get_prefix(message)
        except ValueError:
            return
        alias = await self.first_word(msg[len(prefix):])

        if alias in [x["command_name"] for x in await self.config.images()]:
            
            await channel.trigger_typing()
            image = await self.get_image(alias, guild, True)
            file = discord.File(image.file_loc)
            await channel.send(file=file)

        elif alias in [x["command_name"] for x in await self.config.guild(guild).images()]:
            await channel.trigger_typing()
            image = await self.get_image(alias, guild, False)
            file = discord.File(image.file_loc)
            await channel.send(file=file)

    async def check_command_exists(self, command, guild):
        if command in [x["command_name"] for x in await self.config.guild(guild).images()]:
            return True
        elif await self.part_of_existing_command(command):
            return True
        elif command in [x["command_name"] for x in await self.config.images()]:
            return True
        else:
            return False

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def listimages(self, ctx):
        """List images for the guild or globally"""
        # print(ctx.invoked_subcommand)
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.listimages_guild)

    @listimages.command(pass_context=True, name="guild")
    async def listimages_guild(self, ctx):
        """List images added to bot"""
        msg = ""
        guild = ctx.message.guild
        channel = ctx.message.channel
        # print(await self.config.guild(guild).images())
        if await self.config.guild(guild).images() == []:
            await ctx.send("{} does not have any images saved!".format(guild.name))
            return
        em = discord.Embed(timestamp=ctx.message.created_at)
        for image in await self.config.guild(guild).images():
            em.add_field(name=image["command_name"], value="__Author__: <@{}>\n__Count__: **{}**".format(image["author"], image["count"]))
        em.set_author(name=guild.name, icon_url=guild.icon_url)
        await channel.send(embed=em)

    @listimages.command(pass_context=True, name="global", aliases=["all"])
    async def listimages_global(self, ctx):
        """List images added to bot"""
        msg = ""
        guild = ctx.message.guild
        channel = ctx.message.channel
        # print(await self.config.images())
        if await self.config.images() == []:
            await ctx.send("{} does not have any images saved!".format(self.bot.user.display_name))
            return
        em = discord.Embed(timestamp=ctx.message.created_at)
        for image in await self.config.images():
            em.add_field(name=image["command_name"], value="__Author__: <@{}>\n__Count__: **{}**".format(image["author"], image["count"]))
        em.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        await channel.send(embed=em)

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    async def remimage(self, ctx, cmd):
        """Add images for the bot to upload per guild"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.rem_image_guild, cmd=cmd)

    @remimage.command(pass_context=True, name="guild")
    async def rem_image_guild(self, ctx, cmd):
        """Remove a selected images"""
        author = ctx.message.author
        guild = ctx.message.guild
        channel = ctx.message.channel
        cmd = cmd.lower()
        if cmd not in [x["command_name"] for x in await self.config.guild(guild).images()]:
            await ctx.send("{} is not an image for this guild!".format(cmd))
            return

        await channel.trigger_typing()
        all_imgs = await self.config.guild(guild).images()
        image = await self.get_image(cmd, guild, False)
        all_imgs.remove(image.to_json())
        try:
            os.remove(image.file_loc)
        except:
            pass
        await self.config.guild(guild).images.set(all_imgs)
        await ctx.send("{} has been deleted from this guild!".format(cmd))

    @checks.is_owner()
    @remimage.command(hidden=True, pass_context=True, name="global")
    async def rem_image_global(self, ctx, cmd):
        """Remove a selected images"""
        author = ctx.message.author
        guild = ctx.message.guild
        channel = ctx.message.channel
        cmd = cmd.lower()
        if cmd not in [x["command_name"] for x in await self.config.images()]:
            await ctx.send("{} is not a global image!".format(cmd))
            return

        await channel.trigger_typing()
        all_imgs = await self.config.images()
        image = await self.get_image(cmd, guild, True)
        all_imgs.remove(image.to_json())
        try:
            os.remove(image.file_loc)
        except:
            pass
        await self.config.images.set(all_imgs)
        await ctx.send("{} has been deleted globally!".format(cmd))

    @commands.command(pass_context=True, name="addimage")
    async def add_image_guild(self, ctx, cmd):
        """Add an image to direct upload."""
        author = ctx.message.author
        guild = ctx.message.guild
        channel = ctx.message.channel
        msg = ctx.message
        if cmd.lower() == "global":
            await ctx.send("global is not a valid command name! Try something else.")
            return
        if await self.check_command_exists(cmd, guild):
            await ctx.send("{} is already in the list, try another!".format(cmd))
            return
        else:
            await ctx.send("{} added as the command!".format(cmd))
        await ctx.send("Upload an image for me to use! Type `exit` to cancel.")
        while msg is not None:
            check = lambda m: m.author == author and m.attachments != []
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("Image adding timed out.")
                break

            else:
                seed = ''.join(random.sample(string.ascii_uppercase + string.digits, k=5))
                filename = "{}-{}".format(seed, msg.attachments[0].filename[-5:])
                
                directory = cog_data_path(self) /str(guild.id)
                await self.make_guild_folder(directory)
                cmd = cmd.lower()
                guild_imgs = await self.config.guild(guild).images()
                file_path = "{}/{}".format(str(directory), filename)

                new_entry = ImageEntry(cmd, 0, file_path, author.id)

                guild_imgs.append(new_entry.to_json())
                async with self.session.get(msg.attachments[0].url) as resp:
                    test = await resp.read()
                    with open(file_path, "wb") as f:
                        f.write(test)
                await self.config.guild(guild).images.set(guild_imgs)
                await ctx.send("{} has been added to my files!"
                                            .format(cmd))
                break
            if msg.content.lower().strip() == "exit":
                await ctx.send("Image adding cancelled.")
                break

    @checks.is_owner()
    @commands.command(hidden=True, pass_context=True, name="addglobal")
    async def add_image_global(self, ctx, cmd):
        """Add an image to direct upload."""
        author = ctx.message.author
        guild = ctx.message.guild
        channel = ctx.message.channel
        msg = ctx.message
        if cmd.lower() == "global":
            await ctx.send("global is not a valid command name! Try something else.")
            return
        if await self.check_command_exists(cmd, guild):
            await ctx.send("{} is already in the list, try another!".format(cmd))
            return
        else:
            await ctx.send("{} added as the command!".format(cmd))
        await ctx.send("Upload an image for me to use! Type `exit` to cancel.")
        while msg is not None:
            check = lambda m: m.author == author and m.attachments != []
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("Image adding timed out.")
                break

            else:
                seed = ''.join(random.sample(string.ascii_uppercase + string.digits, k=5))
                filename = "{}-{}".format(seed, msg.attachments[0].filename[-5:])
                
                directory = cog_data_path(self) /"global"
                await self.make_guild_folder(directory)
                cmd = cmd.lower()
                global_imgs = await self.config.images()
                file_path = "{}/{}".format(str(directory), filename)

                new_entry = ImageEntry(cmd, 0, file_path, author.id)

                global_imgs.append(new_entry.to_json())
                async with self.session.get(msg.attachments[0].url) as resp:
                    test = await resp.read()
                    with open(file_path, "wb") as f:
                        f.write(test)
                await self.config.images.set(global_imgs)
                await ctx.send("{} has been added to my files!"
                                            .format(cmd))
                break
            if msg.content.lower().strip() == "exit":
                await ctx.send("Image adding cancelled.")
                break

    def __unload(self):
        self.bot.loop.create_task(self.session.close())

    __del__ = __unload
