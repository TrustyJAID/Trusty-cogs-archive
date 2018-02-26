import discord
from redbot.core import Config
from redbot.core import checks
from discord.ext import commands
from .message_entry import StarboardMessage
import re

class Starboard:

    def __init__(self, bot):
        self.bot = bot
        default_guild = {"enabled": False, "channel": None, "emoji": None, 
                         "role":[], "messages":[], "ignore":[], "threshold": 0}
        self.config = Config.get_conf(self, 356488795)
        self.config.register_guild(**default_guild)

    @commands.group(pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def starboard(self, ctx):
        """Commands for managing the starboard"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @starboard.group(pass_context=True, name="role", aliases=["roles"])
    async def _roles(self, ctx):
        """Add or remove roles allowed to add to the starboard"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    async def get_everyone_role(self, guild):
        for role in guild.roles:
            if role.is_default():
                return role

    async def check_guild_emojis(self, guild, emoji):
        guild_emoji = None
        for emojis in guild.emojis:
            if str(emojis.id) in emoji:
                guild_emoji = emojis
        return guild_emoji
    
    @starboard.command(pass_context=True, name="setup", aliases=["set"])
    async def setup_starboard(self, ctx, channel: discord.TextChannel=None, emoji="⭐", role:discord.Role=None):
        """Sets the starboard channel, emoji and role"""
        guild = ctx.message.guild
        if channel is None:
            channel = ctx.message.channel
        if "<" in emoji and ">" in emoji:
            emoji = await self.check_guild_emojis(guild, emoji)
            if emoji is None:
                await ctx.send("That emoji is not on this guild!")
                return
            else:
                emoji = "<:" + emoji.name + ":" + str(emoji.id) + ">"
        
        if role is None:
            role = await self.get_everyone_role(guild)
        await self.config.guild(ctx.guild).emoji.set(emoji)
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await self.config.guild(ctx.guild).role.set([role.id])
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.send("Starboard set to {}".format(channel.mention))

    @starboard.command(name="disable")
    async def disable_starboard(self, ctx):
        """Disables the starboard for this guild."""
        await self.config.guild(ctx.guild).enabled.set(False)
        await ctx.send("Starboard disabled here!")

    @starboard.command(name="enable")
    async def enable_starboard(self, ctx):
        """Enables the starboard for this guild."""
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.send("Starboard disabled here!")

    @starboard.command(name="ignore")
    async def toggle_channel_ignore(self, ctx, channel:discord.TextChannel=None):
        """Adds channel to ignored list of channels"""
        if channel is None:
            channel = ctx.message.channel
        ignore_list = await self.config.guild(ctx.guild).ignore()
        if channel.id in ignore_list:
            ignore_list.remove(channel.id)
            await ctx.send("{} removed from the ignored channel list!".format(channel.mention))
        else:
            ignore_list.append(channel.id)
            await ctx.send("{} added to the ignored channel list!".format(channel.mention))
        await self.config.guild(ctx.guild).ignore.set(ignore_list)

    @starboard.command(pass_context=True, name="emoji")
    async def set_emoji(self, ctx, emoji="⭐"):
        """Set the emoji for the starboard defaults to ⭐"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await ctx.send("I am not setup for the starboard on this guild!\
                            \nuse `[p]starboard set` to set it up.")
            return
        is_guild_emoji = False
        if "<" in emoji and ">" in emoji:
            emoji = await self.check_guild_emojis(guild, emoji)
            if emoji is None:
                await self.bot.send_message(ctx.message.channel, "That emoji is not on this guild!")
                return
            else:
                is_guild_emoji = True
                emoji = "<:" + emoji.name + ":" + str(emoji.id) + ">"
        await self.config.guild(guild).emoji.set(emoji)
        if is_guild_emoji:
            await ctx.send("Starboard emoji set to {}.".format(emoji))
        else:
            await ctx.send("Starboard emoji set to {}.".format(emoji))

    @starboard.command(pass_context=True, name="channel")
    async def set_channel(self, ctx, channel:discord.TextChannel=None):
        """Set the channel for the starboard"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await self.bot.send_message(ctx.message.channel, 
                                        "I am not setup for the starboard on this guild!\
                                         \nuse `[p]starboard set` to set it up.")
            return
        if channel is None:
            channel = ctx.message.channel
        await self.config.guild(guild).channel.set(channel.id)
        await ctx.send("Starboard channel set to {}.".format(channel.mention))

    @starboard.command(pass_context=True, name="threshold")
    async def set_threshold(self, ctx, threshold:int=0):
        """Set the threshold before posting to the starboard"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await self.bot.send_message(ctx.message.channel, 
                                        "I am not setup for the starboard on this guild!\
                                         \nuse `[p]starboard set` to set it up.")
            return
        await self.config.guild(guild).threshold.set(threshold)
        await ctx.send("Starboard threshold set to {}.".format(threshold))

    @_roles.command(pass_context=True, name="add")
    async def add_role(self, ctx, role:discord.Role=None):
        """Add a role allowed to add messages to the starboard defaults to @everyone"""
        guild = ctx.message.guild
        if not await self.config.guild(guild).enabled():
            await self.bot.send_message(ctx.message.channel, 
                                        "I am not setup for the starboard on this guild!\
                                         \nuse starboard set to set it up.")
            return
        everyone_role = await self.get_everyone_role(guild)
        guild_roles = await self.config.guild(guild).role()
        if role is None:
            role = everyone_role
        if role.id in guild_roles:
            await ctx.send("{} can already add to the starboard!".format(role.name))
            return
        if everyone_role.id in guild_roles and role != everyone_role:
            guild_roles.remove(everyone_role.id)
        guild_roles.append(role.id)
        await self.config.guild(guild).role.set(guild_roles)
        await ctx.send("Starboard role set to {}.".format(role.name))

    @_roles.command(pass_context=True, name="remove", aliases=["del", "rem"])
    async def remove_role(self, ctx, role:discord.Role):
        """Remove a role allowed to add messages to the starboard"""
        if not await self.config.guild(guild).enabled():
            await self.bot.send_message(ctx.message.channel, 
                                        "I am not setup for the starboard on this guild!\
                                         \nuse starboard set to set it up.")
            return
        guild = ctx.message.guild
        everyone_role = await self.get_everyone_role(guild)
        guild_roles = await self.config.guild(guild).role()
        if role.id in guild_roles:
            guild_roles.remove(role.id)
        if guild_roles == []:
            guild_roles.append(everyone_role.id)
        await self.config.guild(guild).role.set(guild_roles)
        await ctx.send("{} removed from starboard.".format(role.name))

    async def check_roles(self, user, author, guild):
        """Checks if the user is allowed to add to the starboard
           Allows bot owner to always add messages for testing
           disallows users from adding their own messages"""
        has_role = False
        for role in user.roles:
            if role.id in await self.config.guild(guild).role():
                has_role = True
        if user is author:
            has_role = False
        if user.id == self.bot.owner_id:
            # Owner should always be allowed to add messages
            has_role = True
        return has_role

    async def check_is_posted(self, guild, message):
        is_posted = False
        for past_message in await self.config.guild(guild).messages():
            if message.id == past_message["original_message"]:
                is_posted = True
        return is_posted

    async def get_posted_message(self, guild, message):
        msg_list = await self.config.guild(guild).messages()
        for past_message in msg_list:
            if message.id == past_message["original_message"]:
                msg = past_message
        msg_list.remove(msg)
        msg["count"] += 1
        msg_list.append(msg)
        await self.config.guild(guild).messages.set(msg_list)
        return msg["new_message"], msg["count"]
  
    async def on_raw_reaction_add(self, emoji, message_id, channel_id, user_id):
        channel = self.bot.get_channel(id=channel_id)
        try:
            guild = channel.guild
        except:
            return
        msg = await channel.get_message(id=message_id)
        user = guild.get_member(user_id)
        if msg.channel.id in await self.config.guild(guild).ignore():
            return
        if msg.channel.id == await self.config.guild(guild).channel():
            return
        if not await self.config.guild(guild).enabled():
            return
        if not await self.check_roles(user, msg.author, guild):
            return
        if user.bot:
            return
        react = await self.config.guild(guild).emoji()
        if str(react) == str(emoji):
            threshold = await self.config.guild(guild).threshold()
            try:
                count = [reaction.count for reaction in msg.reactions if str(reaction.emoji) == str(emoji)][0]
            except KeyError:
                count = 0
            if await self.check_is_posted(guild, msg):
                channel = self.bot.get_channel(await self.config.guild(guild).channel())
                msg_id, count2 = await self.get_posted_message(guild, msg)
                if msg_id is not None:
                    msg_edit = await channel.get_message(msg_id)
                    await msg_edit.edit(content="{} **#{}**".format(emoji, count))
                    return

            if count < threshold:
                    past_message_list = await self.config.guild(guild).messages()
                    past_message_list.append(StarboardMessage(msg.id, None, count).to_json())
                    await self.config.guild(guild).messages.set(past_message_list)
                    return
            author = msg.author
            channel2 = self.bot.get_channel(id=await self.config.guild(guild).channel())
            if msg.embeds != []:
                embed = msg.embeds[0].to_dict()
                em = discord.Embed(timestamp=msg.created_at)
                if "title" in embed:
                    em.title = embed["title"]
                if "thumbnail" in embed:
                    em.set_thumbnail(url=embed["thumbnail"]["url"])
                if "description" in embed:
                    em.description = msg.clean_content + embed["description"]
                if "description" not in embed:
                    em.description = msg.clean_content
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
                if "author" not in embed:
                    em.set_author(name=author.name, icon_url=author.avatar_url)
                if "color" in embed:
                    em.color = embed["color"]
                if "color" not in embed:
                    em.color = author.top_role.color
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
                em = discord.Embed(timestamp=msg.created_at)
                em.color = author.top_role.color
                em.description = msg.content
                em.set_author(name=author.display_name, icon_url=author.avatar_url)
                if msg.attachments != []:
                    em.set_image(url=msg.attachments[0].url)
            em.set_footer(text='{} | {}'.format(channel.guild.name, channel.name))
            post_msg = await channel2.send("{} **#{}**".format(emoji, count), embed=em)
            past_message_list = await self.config.guild(guild).messages()
            past_message_list.append(StarboardMessage(msg.id, post_msg.id, count).to_json())
            await self.config.guild(guild).messages.set(past_message_list)

        else:
            return
