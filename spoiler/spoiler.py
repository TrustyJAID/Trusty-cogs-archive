import discord
from redbot.core import Config, checks, commands


class Spoiler(getattr(commands, "Cog", object)):
    """
        Post spoilers in chat without spoining the text for everyone
    """

    def __init__(self, bot):
        self.bot = bot
        default = {"messages":[]}
        self.config = Config.get_conf(self, 545496534746)
        self.config.register_global(**default)


    @commands.command(name="spoiler", aliases=["spoilers"])
    async def _spoiler(self, ctx, *, spoiler_msg):
        """
            Post spoilers in chat, react to the message to see the spoilers
        """
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        new_msg = await ctx.send("**__SPOILERS__** (React to this message to view)")
        if ctx.channel.permissions_for(ctx.guild.me).add_reactions:
            await new_msg.add_reaction("✅")
        msg_list = await self.config.messages()
        spoiler_obj = {"message_id":new_msg.id, "spoiler_text":spoiler_msg}
        msg_list.append(spoiler_obj)
        await self.config.messages.set(msg_list)

    async def on_raw_reaction_add(self, payload):
        if payload.message_id not in [m["message_id"] for m in await self.config.messages()]:
            return
        if str(payload.emoji) != "✅":
            return
        channel = self.bot.get_channel(id=payload.channel_id)
        try:
            guild = channel.guild
        except:
            return
        user = guild.get_member(payload.user_id)
        if user.bot:
            return
        msg_list = await self.config.messages()
        spoiler_text = " "
        for msg in msg_list:
            if payload.message_id == msg["message_id"]:
                spoiler_text = msg["spoiler_text"]
        try:
            await user.send(spoiler_text)
        except Exception as e:
            print(e)