import discord
import asyncio
from discord.ext import commands
from .utils.dataIO import dataIO
from cogs.utils import checks
import datetime
import os


class Backup:

    def __init__(self, bot):
        self.bot = bot


    async def check_folder(self, folder_name):
        if not os.path.exists("data/backup/{}".format(folder_name)):
            try:
                os.makedirs("data/backup/{}".format(folder_name))
                return True
            except:
                return False
        else:
            return True
            


    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def logs(self, ctx, *, server_name=None):
        if server_name is None:
            server = ctx.message.server
        else:
            for servers in self.bot.servers:
                if server_name.lower() in server.name:
                    server = servers
        today = datetime.date.today().strftime("%Y-%m-%d")
        channel = ctx.message.channel
        is_folder = await self.check_folder(server.name)
        total_msgs = 0
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
                    message_list.append(data)
                total_msgs += len(message_list)
                dataIO.save_json("data/backup/{}/{}-{}.json".format(server.name, chn.name, today), message_list)
                await self.bot.send_message(channel, "{} messages saved from {}".format(len(message_list), chn.name))
            except discord.errors.Forbidden:
                await self.bot.send_message(channel, "0 messages saved from {}".format(len(message_list), chn.name))
                pass
        await self.bot.send_message(channel, "{} messages saved from {}".format(total_msgs, server.name))


def check_folder():
    if not os.path.exists("data/backup"):
        print("Creating data/backup folder")
        os.makedirs("data/backup")

def setup(bot):
    check_folder()
    bot.add_cog(Backup(bot))