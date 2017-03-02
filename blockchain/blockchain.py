# -*- coding: utf-8 -*-
'''blockchain rpc related functions'''

import discord
from discord.ext import commands
from random import randint
from random import choice
from enum import Enum
from binascii import hexlify
import hashlib
import datetime
import time
import aiohttp
import asyncio
from data.blockchain import blockchainrpc as rpc
from data.blockchain import search
from data.blockchain import filesystem
from data.blockchain import satoshi

# RPCUSER, RPCPASS = filesystem.read('rpclogin.txt', 'rb').split()
RPCUSER, RPCPASS = filesystem.read("data\\blockchain\\rpclogin.txt", "r").split()
SERVER = rpc.make_server(RPCUSER, RPCPASS)
BADTRANSACTION = ["4a0088a249e9099d205fb4760c28275d4b8965ac9fd56f5ddf6771cdb0d94f38",
                  "dde7cd8e8f073a525c16c5ee4e4a254f847b7ad6babef257231813166fbef551"]

class blockchain:

    SERVER = rpc.make_server(RPCUSER, RPCPASS)

    def __init__(self, bot):
        self.bot = bot
        self.poll_sessions = []
        self.list_words = ["ASCII", "Julian", "Assange", "Wikileaks"]

    async def checksum(self, data):
        """
        verify's the checksum for files
        uploaded using the satoshi uploader
        does not work without the full file
        """
        length, checksum, data = satoshi.length_checksum_data_from_rawdata(data)
        return satoshi.verify_checksum_data(checksum, data)

    @commands.command()
    async def tx(self, transaction):
        """checks a transaction for significance.
        ;tx 4b0cd7e191ef0a14a9b6ab1c5900be534118c20a332ff26407648168d2722a2e"""
        for tx in BADTRANSACTION:
            if transaction in tx:
                await self.bot.say("That transaction is black listed for illegal content.")
                return
        hexdata = rpc.get_data_local(transaction, self.SERVER)
        inhex = rpc.get_indata_local(transaction, self.SERVER)
        _, _, data = satoshi.length_checksum_data_from_rawdata(satoshi.unhexutf8(hexdata))
        indata = satoshi.unhexutf8(inhex)
        origdata = satoshi.unhexutf8(hexdata)
        significanttx = ''
        significanttx += search.search_hex(hexdata, " output")
        significanttx += search.search_hex(inhex, " input")
        # significanttx += check_hash(inhex+hexdata, 'ripemd160')
        if await self.checksum(origdata):
            significanttx += " Satoshi Checksum found"
        if search.search_words(origdata):
            significanttx += " ASCII letters found output"
        if search.search_words(indata):
            significanttx += " ASCII letters found input"
        if significanttx != '':
            # print(transaction + " " + significanttx)
            await self.bot.say(significanttx)
        else:
            await self.bot.say("Nothing significant in transaction {}".format(transaction))

    async def split_long_text(self, data):
        return [data[i:i+1994] for i in range(0, len(data), 1994)]

    @commands.command(pass_context=True)
    async def txdl(self, ctx, transaction, IO="original"):
        """Downloads Data from the blockchain default is original data.
        IO is optional:
        input = i
        output = o
        satoshi = s
        Send a transaction id like the one below
        ;txdl 4b0cd7e191ef0a14a9b6ab1c5900be534118c20a332ff26407648168d2722a2e o"""
        for tx in BADTRANSACTION:
            if transaction in tx:
                await self.bot.say("That transaction is black listed for illegal content.")
                return
        # print(IO)
        # print(discord.Channel)
        try:
            hexdata = rpc.get_data_local(transaction, self.SERVER)
            inhex = rpc.get_indata_local(transaction, self.SERVER)
            _, _, data = satoshi.length_checksum_data_from_rawdata(satoshi.unhexutf8(hexdata))
            indata = satoshi.unhexutf8(inhex)
            origdata = satoshi.unhexutf8(hexdata)
        except:
            print("There was likely an incorrect transaction.")
            await self.bot.say("Sorry there is something wrong with that transaction.")
            return
        significanttx = ''
        significanttx += search.search_hex(hexdata, " output")
        significanttx += search.search_hex(inhex, " input")
        # significanttx += check_hash(inhex+hexdata, 'ripemd160')
        dataout = b""
        if (IO == "o") or (IO == "original"):
            dataout = origdata
        if (IO == "i") or (IO == "input"):
            dataout = indata
        if (IO == "s") or (IO == "satoshi"):
            dataout = data
        if IO == transaction:
            dataout = origdata
        if await self.checksum(origdata):
            significanttx += " Satoshi Checksum found"
        if search.search_words(origdata):
            significanttx += " ASCII letters found output"
        if search.search_words(indata):
            significanttx += " ASCII letters found input"
        filesystem.write("data/blockchain/" + IO + "data.txt", dataout, True, "wb")
        if significanttx != '':
            extension = "txt"
            await self.bot.say(significanttx)
            try:
                for words in self.list_words:
                    if words in significanttx and "input" in significanttx:
                            indata = await self.split_long_text(indata)
                            for i in indata:
                                await self.bot.say("```" + i.decode('utf8') + "```")
                    if words in significanttx and "output" in significanttx:
                        if "Satoshi" in significanttx:
                            data = await self.split_long_text(data)
                            for i in data:
                                await self.bot.say("```" + i.decode('utf8') + "```")
                        else:
                            data = await self.split_long_text(data)
                            for i in data:
                                await self.bot.say("```" + i.decode('utf8') + "```")
            except UnicodeDecodeError:
                pass
            if "GIF" in significanttx:
                extension = "gif"
            if "7z" in significanttx:
                extension = "7z"
            if "GZ" in significanttx:
                extension = "gz"
            if "PDF" in significanttx:
                extension = "pdf"
            if "PNG" in significanttx:
                extension = "png"
            if "JPG" in significanttx:
                extension = "jpg"
            await self.bot.send_file(ctx.message.channel, "data/blockchain/" + IO + "data.txt", filename=IO+'data.'+extension)
        if significanttx == '':
            await self.bot.say("Nothing significant in transaction `{}`".format(transaction))
            await self.bot.send_file(ctx.message.channel, "data/blockchain/" + IO + "data.txt", filename=IO+'data.txt')


def setup(bot):
    n = blockchain(bot)
    # bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
