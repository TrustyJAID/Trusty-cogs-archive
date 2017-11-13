import discord
from discord.ext import commands
import aiohttp
import os
from PIL import Image
from PIL import ImageColor
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageSequence
from barcode import generate
from barcode.writer import ImageWriter
from redbot.core.data_manager import bundled_data_path
from redbot.core.data_manager import cog_data_path
from pathlib import Path
import glob

class Badges:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        temp_folder = cog_data_path(self) /"temp"
        temp_folder.mkdir(exist_ok=True, parents=True)
        temp_gif = temp_folder/"tempgif"
        temp_gif.mkdir(exist_ok=True, parents=True)
        self.blank_template = {"cia":"cia-template.png", 
                               "cicada":"cicada-template.png", 
                               "ioi":"IOI-template.png",
                               "fbi":"fbi-template.png",
                               "nsa":"nsa-template.png",
                               "gab":"gab-template.png",
                               "dop":"dop-template.png",
                               "shit":"shit-template.png",
                               "bunker":"bunker-template.png",
                               "nk":"nk-template.png",
                               "kek": "kek-template.png",
                               "unsc": "unsc-template.png"}
        

    async def dl_image(self, url, ext="png"):
        """Downloads the users avatar to a temp folder"""
        async with self.session.get(url) as resp:
            test = await resp.read()
            with open(str(cog_data_path(self)) + "\\temp\\temp." + ext, "wb") as f:
                f.write(test)

    async def create_badge(self, user, badge):
        avatar = user.avatar_url if user.avatar_url != "" else user.default_avatar_url
        username = user.display_name
        userid = user.id
        department = "GENERAL SUPPORT" if user.top_role.name == "@everyone" else user.top_role.name.upper()
        status = user.status
        if str(user.status) == "online":
            status = "ACTIVE"
        if str(user.status) == "offline":
            status = "COMPLETING TASK"
        if str(user.status) == "idle":
            status = "AWAITING INSTRUCTIONS"
        if str(user.status) == "dnd":
            status = "MIA"
        ext = "png"
        if "gif" in avatar:
            ext = "gif"
        await self.dl_image(avatar, ext)
        temp_barcode = generate("code39", str(userid), 
                                writer=ImageWriter(), 
                                output=str(cog_data_path(self)) + "\\temp\\bar_code_temp")
        template = Image.open(str(bundled_data_path(self))+ "\\" + self.blank_template[badge])
        template = template.convert("RGBA")
        avatar = Image.open(str(cog_data_path(self)) + "\\temp\\temp." + ext)
        barcode = Image.open(str(cog_data_path(self)) + "\\temp\\bar_code_temp.png")
        barcode = barcode.convert("RGBA")
        barcode = barcode.resize((555,125), Image.ANTIALIAS)
        template.paste(barcode, (400,520), barcode)
        # font for user information
        font1 = ImageFont.truetype(str(bundled_data_path(self)) + "\\ARIALUNI.ttf", 30)
        # font for extra information
        font2 = ImageFont.truetype(str(bundled_data_path(self)) + "\\ARIALUNI.ttf", 24)
        draw = ImageDraw.Draw(template)
        # adds username
        draw.text((225, 330), str(username), fill=(0, 0, 0), font=font1)
        # adds ID Class
        draw.text((225, 400), badge.upper() + "-" + str(user).split("#")[1], fill=(0, 0, 0), font=font1)
        # adds user id
        draw.text((250, 115), str(userid), fill=(0, 0, 0), font=font2)
        # adds user status
        draw.text((250, 175), status, fill=(0, 0, 0), font=font2)
        # adds department from top role
        draw.text((250, 235), department, fill=(0, 0, 0), font=font2)
        # adds user level
        draw.text((420, 475), "LEVEL " + str(len(user.roles)), fill="red", font=font1)
        # adds user level
        draw.text((60, 585), str(user.joined_at), fill=(0, 0, 0), font=font2)
        if ext == "gif":
            for image in glob.glob(str(cog_data_path(self)) + "\\temp\\tempgif\\*"):
                os.remove(image)
            gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
            img_list = []
            num = 0
            for frame in gif_list[:18]:
                watermark = frame.copy()
                watermark = watermark.convert("RGBA")
                watermark = watermark.resize((100,100))
                watermark.putalpha(128)
                id_image = frame.resize((165, 165))
                template.paste(watermark, (845,45, 945,145), watermark)
                template.paste(id_image, (60,95, 225, 260))
                template.save(str(cog_data_path(self)) + "\\temp\\tempgif\\{}.png".format(str(num)))
                num += 1
            img_list = [Image.open(file) for file in glob.glob(str(cog_data_path(self)) + "\\temp\\tempgif\\*")]
            template.save(str(cog_data_path(self)) + "\\temp\\tempbadge.gif", save_all=True, append_images=img_list, duration=1, loop=10)
        else:
            watermark = avatar.convert("RGBA")
            watermark.putalpha(128)
            watermark = watermark.resize((100,100))
            id_image = avatar.resize((165, 165))
            template.paste(watermark, (845,45, 945,145), watermark)
            template.paste(id_image, (60,95, 225, 260))
            template.save(str(cog_data_path(self)) + "\\temp\\tempbadge.png")
    
    @commands.command()
    async def badges(self, ctx, badge, user:discord.Member=None):
        """Creates a badge for [cia, nsa, fbi, dop, ioi]"""
        if badge.lower() not in self.blank_template:
            await ctx.send("That badge doesn't exist yet!")
            return
        if user is None:
            user = ctx.message.author
        avatar = user.avatar_url if user.avatar_url != "" else user.default_avatar_url
        ext = "png"
        if "gif" in avatar:
            ext = "gif"
        await self.create_badge(user, badge.lower())
        image = discord.File(str(cog_data_path(self)) + "\\temp\\tempbadge." + ext)
        await ctx.send(file=image)
