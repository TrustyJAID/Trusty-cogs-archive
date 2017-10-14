import discord
import asyncio
from .utils.dataIO import dataIO
from discord.ext import commands
from cogs.utils import checks
import os
import re

class Star:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/star/settings.json")

    @commands.group(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def starboard(self, ctx):
        """Commands for managing the starboard"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @starboard.group(pass_context=True, name="role", aliases=["roles"])
    async def _roles(self, ctx):
        """Add or remove roles allowed to add to the starboard"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    async def get_everyone_role(self, server):
        for role in server.roles:
            if role.is_everyone:
                return role

    async def check_server_emojis(self, server, emoji):
        server_emoji = None
        for emojis in server.emojis:
            if emojis.id in emoji:
                server_emoji = emojis
        return server_emoji
    
    @starboard.command(pass_context=True, name="set")
    async def setup_starboard(self, ctx, channel: discord.Channel=None, emoji="⭐", role:discord.Role=None):
        """Sets the starboard channel, emoji and role"""
        server = ctx.message.server
        if channel is None:
            channel = ctx.message.channel
        if "<" in emoji and ">" in emoji:
            emoji = await self.check_server_emojis(server, emoji)
            if emoji is None:
                await self.bot.send_message(ctx.message.channel, "That emoji is not on this server!")
                return
            else:
                emoji = ":" + emoji.name + ":" + emoji.id
        
        if role is None:
            role = await self.get_everyone_role(server)
        self.settings[server.id] = {"emoji": emoji, 
                                    "channel": channel.id, 
                                    "role": [role.id]}
        dataIO.save_json("data/star/settings.json", self.settings)
        await self.bot.say("Starboard set to {}".format(channel.mention))

    @starboard.command(pass_context=True, name="emoji")
    async def set_emoji(self, ctx, emoji="⭐"):
        """Set the emoji for the starboard defaults to ⭐"""
        server = ctx.message.server
        is_server_emoji = False
        if "<" in emoji and ">" in emoji:
            emoji = await self.check_server_emojis(server, emoji)
            if emoji is None:
                await self.bot.send_message(ctx.message.channel, "That emoji is not on this server!")
                return
            else:
                is_server_emoji = True
                emoji = ":" + emoji.name + ":" + emoji.id
        self.settings[server.id]["emoji"] = emoji
        dataIO.save_json("data/star/settings.json", self.settings)
        if is_server_emoji:
            await self.bot.send_message(ctx.message.channel, "Starboard emoji set to <{}>.".format(emoji))
        else:
            await self.bot.send_message(ctx.message.channel, "Starboard emoji set to {}.".format(emoji))

    @starboard.command(pass_context=True, name="channel")
    async def set_channel(self, ctx, channel:discord.Channel=None):
        """Set the channel for the starboard"""
        server = ctx.message.server
        if channel is None:
            channel = ctx.message.channel
        self.settings[server.id]["channel"] = channel.id
        dataIO.save_json("data/star/settings.json", self.settings)
        await self.bot.send_message(ctx.message.channel, "Starboard channel set to {}.".format(channel.mention))

    @_roles.command(pass_context=True, name="add")
    async def add_role(self, ctx, role:discord.Role=None):
        """Add a role allowed to add messages to the starboard defaults to @everyone"""
        server = ctx.message.server
        everyone_role = await self.get_everyone_role(server)
        if role is None:
            role = everyone_role
        if role.id in self.settings[server.id]["role"]:
            await self.bot.send_message(ctx.message.channel, "{} can already add to the starboard!".format(role.name))
            return
        if everyone_role.id in self.settings[server.id]["role"] and role != everyone_role:
            self.settings[server.id]["role"].remove(everyone_role.id)
        self.settings[server.id]["role"].append(role.id)
        dataIO.save_json("data/star/settings.json", self.settings)
        await self.bot.send_message(ctx.message.channel, "Starboard role set to {}.".format(role.name))

    @_roles.command(pass_context=True, name="remove", aliases=["del", "rem"])
    async def remove_role(self, ctx, role:discord.Role):
        """Remove a role allowed to add messages to the starboard"""
        server = ctx.message.server
        everyone_role = await self.get_everyone_role(server)
        if role.id in self.settings[server.id]["role"]:
            self.settings[server.id]["role"].remove(role.id)
        if self.settings[server.id]["role"] == []:
            self.settings[server.id]["role"].append(everyone_role.id)
        dataIO.save_json("data/star/settings.json", self.settings)
        await self.bot.send_message(ctx.message.channel, "{} removed from starboard.".format(role.name))

    async def check_roles(self, user, author, server):
        """Checks if the user is allowed to add to the starboard
           Allows bot owner to always add messages for testing
           disallows users from adding their own messages"""
        has_role = False
        for role in user.roles:
            if role.id in self.settings[server.id]["role"]:
                has_role = True
        if user is author:
            has_role = False
        if user.id == self.bot.settings.owner:
            has_role = True
        return has_role
  
    async def on_reaction_add(self, reaction, user):
        server = reaction.message.server
        msg = reaction.message
        if server.id not in self.settings:
            return
        if not await self.check_roles(user, msg.author, server):
            return
        react = self.settings[server.id]["emoji"]
        if react in str(reaction.emoji):
            if reaction.count > 1:
                return
            author = reaction.message.author
            channel = reaction.message.channel
            channel2 = self.bot.get_channel(id=self.settings[server.id]["channel"])
            if reaction.message.embeds != []:
                embed = reaction.message.embeds[0]
                # print(embed)
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
                    if ".png" in embed["url"] or ".jpg" in embed["url"]:
                        em.set_thumbnail(url="")
                        em.set_image(url=embed["url"])
                    else:
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
    data = {}
    f = 'data/star/settings.json'
    if not os.path.exists(f):
        dataIO.save_json(f, data)


def setup(bot):
    check_folder()
    check_files()
    bot.add_cog(Star(bot))