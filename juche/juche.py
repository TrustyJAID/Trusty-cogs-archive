import discord

class Juche(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def check_date(self, message):
        for i in range(1912, 2100):
            if str(i) in message.split(" ") and "http" not in message:
                message = message.replace(str(i), "Juche " + str(i-1912+1))
                message = "I think you mean Juche " + str(i-1912+1) + "."
                return message

        return None

    async def on_message(self, message):
        msg = message.content
        if not hasattr(msg, "guild"):
            return
        guild = message.guild
        channel = message.channel

        if guild.id in [304436539482701825, 321105104931389440]:
            juche = await self.check_date(msg)
            if juche != None:
                await channel.send(juche)
