import discord
import asyncio
import aiohttp
from discord.ext import commands
from .utils.dataIO import dataIO
from cogs.utils import checks
import datetime
import os


class Backup:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.session.close()

    async def check_folder(self, folder_name):
        if not os.path.exists("data/backup/{}".format(folder_name)) or not os.path.exists("data/backup/{}/files".format(folder_name)):
            try:
                os.makedirs("data/backup/{}".format(folder_name))
                os.makedirs("data/backup/{}/files".format(folder_name))
                return True
            except:
                return False
        else:
            return True

    @commands.command(pass_context=True, aliases=["dlimage"])
    @checks.admin_or_permissions(manage_messages=True)
    async def imagedl(self, ctx, *, server_name=None):
        if server_name is None:
            server = ctx.message.server
        else:
            for servers in self.bot.servers:
                if server_name.lower() in servers.name.lower():
                    server = servers
        channel = ctx.message.channel
        is_folder = await self.check_folder(server.name)
        total_msgs = 0
        if not is_folder:
            print("{} folder doesn't exist!".format(server.name))
            return
        for chn in server.channels:
            # await self.bot.send_message(channel, "backing up {}".format(chn.name))
            files_saved = 0
            try:
                async for message in self.bot.logs_from(chn, limit=10000000):
                    if message.attachments != []:
                        for file in message.attachments:
                            async with self.session.get(file["url"]) as resp:
                                data = await resp.read()
                            file_loc = "data/backup/{}/files/{}".format(server.name, "{}-{}".format(total_msgs,file["filename"]))
                            with open(file_loc, "wb") as file:
                                file.write(data)
                        files_saved += 1
                    total_msgs += 1
                await self.bot.send_message(channel, "{} messages saved from {}".format(files_saved, chn.name))
            except discord.errors.Forbidden:
                await self.bot.send_message(channel, "0 messages saved from {}".format(chn.name))
                pass
        await self.bot.send_message(channel, "{} messages saved from {}".format(total_msgs, server.name))
            


    @commands.command(pass_context=True, aliases=["backup"])
    @checks.admin_or_permissions(manage_messages=True)
    async def logs(self, ctx, *, server_name=None):
        if server_name is None:
            server = ctx.message.server
        else:
            for servers in self.bot.servers:
                if server_name.lower() in servers.name.lower():
                    server = servers
        today = datetime.date.today().strftime("%Y-%m-%d")
        channel = ctx.message.channel
        is_folder = await self.check_folder(server.name)
        total_msgs = 0
        files_saved = 0
        if not is_folder:
            print("{} folder doesn't exist!".format(server.name))
            return
        for chn in server.channels:
            # await self.bot.send_message(channel, "backing up {}".format(chn.name))
            message_list = []
            try:
                async for message in self.bot.logs_from(chn, limit=10000000):
                    data = {"timestamp":message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "tts":message.tts,
                            "author":{"name":message.author.name,
                                      "display_name":message.author.display_name,
                                      "discriminator":message.author.discriminator,
                                      "id":message.author.id,
                                      "bot":message.author.bot},
                            "content":message.content,
                            "nonce":message.nonce,
                            "embeds":message.embeds,
                            "channel":{"name":message.channel.name, "id":message.channel.id},
                            "mention_everyone":message.mention_everyone,
                            "mentions":[{"name":user.name, 
                                         "display_name":user.display_name,
                                         "discriminator":user.discriminator,
                                         "id":user.id,
                                         "bot":user.bot} for user in message.mentions],
                            "channel_mentions":[{"name":channel.name, 
                                                 "id":channel.id} for channel in message.channel_mentions],
                            "role_mentions":[{"name":role.name, 
                                              "id":role.id} for role in message.role_mentions],
                            "id":message.id,
                            "attachments":message.attachments,
                            "pinned":message.pinned}
                    if message.attachments != []:
                        for file in message.attachments:
                            async with self.session.get(file["url"]) as resp:
                                img_data = await resp.read()
                            file_loc = "data/backup/{}/files/{}".format(server.name, "{}-{}".format(files_saved, file["filename"]))
                            with open(file_loc, "wb") as file:
                                file.write(img_data)
                            files_saved += 1
                    message_list.append(data)
                total_msgs += len(message_list)
                if len(message_list) == 0:
                    continue
                dataIO.save_json("data/backup/{}/{}-{}.json".format(server.name, chn.name, today), message_list)
                await self.bot.send_message(channel, "{} messages saved from {}".format(len(message_list), chn.name))
            except discord.errors.Forbidden:
                await self.bot.send_message(channel, "0 messages saved from {}".format(chn.name))
                pass
        await self.bot.send_message(channel, "{} messages saved from {}".format(total_msgs, server.name))


def check_folder():
    if not os.path.exists("data/backup"):
        print("Creating data/backup folder")
        os.makedirs("data/backup")

def setup(bot):
    check_folder()
    bot.add_cog(Backup(bot))
