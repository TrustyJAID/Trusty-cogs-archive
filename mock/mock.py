import discord
import random
from discord.ext import commands

class Mock:

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
                async for message in self.bot.logs_from(channel, limit=100):
                    if str(message.id) == msg:
                        msg = message
                        break
        else:
            async for message in self.bot.logs_from(channel, limit=2):
                msg = message
        result = self.cap_change(msg.content) if hasattr(msg, "content") else self.cap_change(msg)
        author = msg.author if hasattr(msg, "author") else ctx.message.author
        time = msg.timestamp if hasattr(msg, "created_at") else ctx.message.timestamp
        # file = discord.File("data/mock/spongebob.jpg")
        embed = discord.Embed(description=result,
                              timestamp=time)
        embed.colour = author.colour if hasattr(author, "colour") else discord.Colour.default()
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_thumbnail(url="https://i.imgur.com/upItEiG.jpg")
        if hasattr(msg, "attachments") and msg.attachments != []:
            embed.set_image(url=msg.attachments[0].url)
        await self.bot.send_message(channel, embed=embed)
        if author != user:
            await self.bot.send_message(channel, "- " + author.mention)


def setup(bot):
    bot.add_cog(Mock(bot))
