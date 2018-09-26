import sys
import cv2
import json
import os
import discord
import functools
import asyncio
import numpy as np
from io import BytesIO
from redbot.core import commands
from PIL import Image, ImageDraw, ImageFont
from redbot.core.data_manager import bundled_data_path

class Trump:
    """Code is from http://isnowillegal.com/ and made to work on redbot"""

    def __init__(self, bot):
        self.bot = bot
        self.textFont = None

    @commands.command()
    async def trump(self, ctx, *, message):
        task = functools.partial(self.make_gif, text=message)        
        task = self.bot.loop.run_in_executor(None, task)
        try:
            temp = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return
        image = discord.File(temp)
        await ctx.send(file=image)

    def make_gif(self, text):
        folder = str(bundled_data_path(self))+"/template"
        jsonPath = os.path.join(folder, 'frames.json')

        # Load frames
        frames = json.load(open(jsonPath))

        # Used to compute motion blur
        lastCorners = None
        textImage = self.generateText(text)

        # Will store all gif frames
        frameImages = []

        # Iterate trough frames
        for frame in frames:
            # Load image
            name = frame['file']
            filePath = os.path.join(folder, name)
            finalFrame = None

            # If it has transformations,
            # process with opencv and convert back to pillow
            if frame['show'] == True:
                image = cv2.imread(filePath)

                # Do rotoscope
                image = self.rotoscope(image, textImage, frame)

                # Show final result
                # cv2.imshow(name, image)
                finalFrame = self.cvImageToPillow(image)
            else:
                finalFrame = Image.open(filePath)

            frameImages.append(finalFrame)
        temp = BytesIO()
            # Saving...
        frameImages[0].save(temp, format="GIF", save_all=True, append_images=frameImages, duration=0, loop=0)
        temp.name = "Trump.gif"
        temp.seek(0)
        return temp


    def rotoscope(self, dst, warp, properties):
        if properties['show'] == False:
            return dst

        corners = properties['corners']

        wRows, wCols, wCh = warp.shape
        rows, cols, ch = dst.shape

        # Apply blur on warp
        kernel = np.ones((5, 5), np.float32) / 25
        warp = cv2.filter2D(warp, -1, kernel)

        # Prepare points to be matched on Affine Transformation
        pts1 = np.float32([[0, 0],[wCols, 0],[0, wRows]])
        pts2 = np.float32(corners) * 2

        # Enlarge image to multisample
        dst = cv2.resize(dst, (cols * 2, rows * 2))

        # Transform image with the Matrix
        M = cv2.getAffineTransform(pts1, pts2)
        cv2.warpAffine(warp, M, (cols * 2, rows * 2), dst, flags=cv2.INTER_AREA, borderMode=cv2.BORDER_TRANSPARENT)

        # Sample back image size
        dst = cv2.resize(dst, (cols, rows))

        return dst


    def computeAndLoadTextFontForSize(self, drawer, text, maxWidth):
        # global textFont

        # Measure text and find out position
        maxSize = 50
        minSize = 6
        curSize = maxSize
        while curSize >= minSize:
            self.textFont = ImageFont.truetype(str(bundled_data_path(self))+'/impact.ttf', size=curSize)
            w, h = drawer.textsize(text, font=self.textFont)
            
            if w > maxWidth:
                curSize -= 4
            else:
                return self.textFont
        return self.textFont

    def generateText(self, text):
        # global impact, textFont

        txtColor = (20, 20, 20)
        bgColor = (224, 233, 237)
        # bgColor = (100, 0, 0)
        imgSize = (160, 200)
        
        # Create image
        image = Image.new("RGB", imgSize, bgColor)

        # Draw text on top
        draw = ImageDraw.Draw(image)

        # Load font for text
        if self.textFont == None:
            self.textFont = self.computeAndLoadTextFontForSize(draw, text, imgSize[0])
            
        w, h = draw.textsize(text, font=self.textFont)
        xCenter = (imgSize[0] - w) / 2
        yCenter = (50 - h) / 2
        draw.text((xCenter, 10 + yCenter), text, font=self.textFont, fill=txtColor)
        impact = ImageFont.truetype(str(bundled_data_path(self))+'/impact.ttf', 46)
        draw.text((12, 70), "IS NOW", font=impact, fill=txtColor)
        draw.text((10, 130), "ILLEGAL", font=impact, fill=txtColor)
        
        # Convert to CV2
        cvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # cv2.imshow('text', cvImage)
        
        return cvImage

    def cvImageToPillow(self, cvImage):
        cvImage = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cvImage)
