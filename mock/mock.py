import discord
import random
from redbot.core import commands

class Mock(commands.Cog):
    """mock a user as spongebob"""

    def __init__(self, bot):
        self.bot = bot

    def cap_change(self, message):
        result = ""
        for char in message:
            value = random.choice([True, False])
            if value:
                result += char.upper()
            else:
                result += char.lower()
        return result

    @commands.command(pass_context=True)
    async def mock(self, ctx, *, msg=""):
        """Use >mock to randomized capitalization on a message or string.
            Better random comming soon™
            Usage:
            >mock a string
                A sTRiNg
            >mock
                laSt SeNT MeSsaGE
            >mock (message id)
                THaT mEsSAgE
        """
        channel = ctx.message.channel
        result = ""
        user = ctx.message.author
        if msg:
            if msg.isdigit():
                async for message in channel.history(limit=100):
                    if str(message.id) == msg:
                        msg = message
                        break
        else:
            async for message in channel.history(limit=2):
                msg = message
        result = self.cap_change(msg.content) if hasattr(msg, "content") else self.cap_change(msg)
        author = msg.author if hasattr(msg, "author") else ctx.message.author
        time = msg.created_at if hasattr(msg, "created_at") else ctx.message.created_at
        embed = discord.Embed(description=result, timestamp=time)
        embed.colour = author.colour if hasattr(author, "colour") else discord.Colour.default()
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_thumbnail(url="https://i.imgur.com/upItEiG.jpg")
        embed.set_footer(text="{} mocked {}".format(
                         ctx.message.author.display_name, author.display_name), icon_url=ctx.message.author.avatar_url)
        if hasattr(msg, "attachments") and msg.attachments != []:
            embed.set_image(url=msg.attachments[0].url)
        if not channel.permissions_for(channel.guild.me).embed_links:
            if author != user:
                await ctx.send(result + " - " + author.mention)
            else:
                await ctx.send(result)
        else:
            await ctx.send(embed=embed)
            if author != user:
                await ctx.send("- " + author.mention)
