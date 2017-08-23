import discord
import asyncio
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from discord.ext import commands
import os
import re

class Star:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/star/settings.json")
    
    @commands.command(pass_context=True)
    async def addstarboard(self, ctx, channel: discord.Channel=None, emoji="⭐"):
        if channel is None:
            channel = ctx.message.channel
        if "<" in emoji and ">" in emoji:
            emoji = emoji.strip("<>")
        server = ctx.message.server
        self.settings[server.id] = {"emoji": emoji, "channel" :channel.id}
        dataIO.save_json("data/star/settings.json", self.settings)
        await self.bot.say("Starboard set to {}".format(channel.mention))
  
    async def on_reaction_add(self, reaction, user):
        server = reaction.message.server
        msg = reaction.message
        if server.id not in self.settings or user.id == msg.author.id:
            return
        react = self.settings[server.id]["emoji"]
        if react in str(reaction.emoji):
            if reaction.count > 1:
                return
            author = reaction.message.author
            channel = reaction.message.channel
            channel2 = discord.Object(id=self.settings[server.id]["channel"])
            if reaction.message.embeds != []:
                embed = reaction.message.embeds[0]
                em = discord.Embed(timestamp=reaction.message.timestamp)
                if "title" in embed:
                    em.title = embed["title"]
                if "thumbnail" in embed:
                    em.set_thumbnail(url=embed["thumbnail"]["url"])
                if "description" in embed:
                    if embed["description"] is None:
                        em.description = msg.clean_content
                    else:
                        em.description = embed["description"]
                if "url" in embed:
                    em.url = embed["url"]
                if "footer" in embed:
                    em.set_footer(text=embed["footer"]["text"])
                if "author" in embed:
                    postauthor = embed["author"]
                    if "icon_url" in postauthor:
                        em.set_author(name=postauthor["name"], icon_url=postauthor["icon_url"])
                    else:
                        em.set_author(name=postauthor["name"])
                if "color" in embed:
                    em.color = embed["color"]
                if "image" in embed:
                    em.set_image(url=embed["image"]["url"])
                if embed["type"] == "image":
                    em.type = "image"
                    em.set_thumbnail(url=embed["url"])
                    em.set_image(url=embed["url"]+"."+embed["thumbnail"]["url"].rsplit(".")[-1])
                if embed["type"] == "gifv":
                    em.type = "gifv"
                    em.set_thumbnail(url=embed["url"])
                    em.set_image(url=embed["url"]+".gif")
                
            else:
                em = discord.Embed(timestamp=reaction.message.timestamp)
                em.color = author.top_role.color
                if "<:" in msg.content and ">" in msg.content:
                    if msg.content.count("<:") == 1:
                        emoji = re.findall(r'<(.*?)>', msg.content)[0]
                        emoji_id= emoji.split(":")[-1]
                        newmsg = re.sub('<[^>]+>', '', msg.content)
                        em.description = newmsg
                        em.set_image(url="https://cdn.discordapp.com/emojis/{}.png".format(emoji_id))
                else:
                    em.description = msg.clean_content
                em.set_author(name=author.name, icon_url=author.avatar_url)
                em.set_footer(text='{} | {}'.format(channel.server.name, channel.name))
                if reaction.message.attachments != []:
                    em.set_image(url=reaction.message.attachments[0]["url"])
            post_msg = await self.bot.send_message(channel2, embed=em)
            await self.bot.add_reaction(post_msg, emoji=react)
        else:
            return

def check_folder():
    if not os.path.exists('data/star'):
        os.mkdir('data/star')


def check_files():
    f = 'data/star/settings.json'
    if not os.path.exists(f):
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Star(bot))