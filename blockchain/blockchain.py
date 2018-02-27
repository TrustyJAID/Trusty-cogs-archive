# -*- coding: utf-8 -*-
'''blockchain rpc related functions'''

import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from random import randint
from random import choice
from enum import Enum
import binascii
import hashlib
import datetime
import time
import aiohttp
import asyncio
import json
import struct# test commit


BADTRANSACTION = ["4a0088a249e9099d205fb4760c28275d4b8965ac9fd56f5ddf6771cdb0d94f38",
                  "dde7cd8e8f073a525c16c5ee4e4a254f847b7ad6babef257231813166fbef551"]

class blockchain:

    def __init__(self, bot):
        self.bot = bot
        self.poll_sessions = []
        self.list_words = ["ASCII", "Julian", "Assange", "Wikileaks", "All"]
        self.login_data = dataIO.load_json("data/blockchain/rpclogin.json")
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.request_id = 1
        self.url = "http://{username}:{password}@{ip}:{port}".format(
                    username=self.login_data["username"],
                    password=self.login_data["password"],
                    ip=self.login_data["ip"],
                    port=self.login_data["port"])

    def __unload(self):
        self.session.close()

    async def get_block_height(self):
        params = json.dumps({"jsonrpc":"1.1","method":"getblockcount","id":self.request_id})
        async with self.session.post(self.url, data=params) as resp:
            data = await resp.json()
        return data["result"]


    async def get_data_local(self, transaction):
        tx = await self.get_transaction_data(transaction)
        return ''.join(op
                       for txout in tx.get('vout')
                       for op in txout.get('scriptPubKey', {'asm': ''}).get('asm', '').split()
                       if not op.startswith('OP_') and len(op) >= 40)


    async def get_indata_local(self, transaction):
        tx = await self.get_transaction_data(transaction)
        return ''.join(inop
                       for txin in tx.get('vin')
                       for inop in txin.get('scriptSig', {'hex': ''}).get('hex', '').split())

    async def get_raw_transaction(self, transaction):
        params = json.dumps({"jsonrpc":"1.1","method":"getrawtransaction","params":[transaction],"id":self.request_id})
        async with self.session.post(self.url, data=params) as resp:
            data = await resp.json()
        return data["result"]

    async def decode_raw_transaction(self, raw_transaction):
        params = json.dumps({"jsonrpc":"1.1","method":"decoderawtransaction","params":[raw_transaction],"id":self.request_id})
        async with self.session.post(self.url, data=params) as resp:
            data = await resp.json()
        return data["result"]

    async def get_transaction_data(self, transaction):
        raw_data = await self.get_raw_transaction(transaction)
        return await self.decode_raw_transaction(raw_data)

    async def checksum(self, data):
        """
        verify's the checksum for files
        uploaded using the satoshi uploader
        does not work without the full file
        """
        length, checksum, data = self.length_checksum_data_from_rawdata(data)
        return self.verify_checksum_data(checksum, data)

    def verify_checksum_data(self, checksum, data):
        '''Returns true if the checksum matches the crc32 checksum of the data'''
        return binascii.crc32(data) & 0xffffffff == checksum

    @commands.group(pass_context=True, name="blockchain", aliases=["bc"])
    async def blockchain(self, ctx):
        """Blockchain commands for accessing the bitcoin blockchain"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @blockchain.command(name="transaction",aliases=["tx"])
    async def _transaction(self, transaction):
        """checks a transaction for significance.
        try: 4b0cd7e191ef0a14a9b6ab1c5900be534118c20a332ff26407648168d2722a2e"""
        if transaction in BADTRANSACTION:
            await self.bot.say("That transaction is black listed for illegal content.")
            return
        hexdata = await self.get_data_local(transaction)
        inhex = await self.get_indata_local(transaction)
        _, _, data = self.length_checksum_data_from_rawdata(self.unhexutf8(hexdata))
        indata = self.unhexutf8(inhex)
        origdata = self.unhexutf8(hexdata)
        significanttx = ''
        significanttx += self.search_hex(hexdata, " output")
        significanttx += self.search_hex(inhex, " input")
        # significanttx += check_hash(inhex+hexdata, 'ripemd160')
        if await self.checksum(origdata):
            significanttx += " Satoshi Checksum found"
        if self.search_words(origdata):
            significanttx += " ASCII letters found output"
        if self.search_words(indata):
            significanttx += " ASCII letters found input"
        if significanttx != '':
            # print(transaction + " " + significanttx)
            await self.bot.say(significanttx)
        else:
            await self.bot.say("Nothing significant in transaction {}".format(transaction))

    def length_checksum_data_from_rawdata(self, rawdata):
        '''Returns the length, checksum, and data bytes from the given rawdata'''
        try:
            length = struct.unpack('<L', rawdata[0:4])[0]
            return length, struct.unpack('<L', rawdata[4:8])[0], rawdata[8:8+length]
        except struct.error as e:
            print(e)
            return None, None, rawdata

    def unhexutf8(self, s):
        '''Return unhexlified string data encoded as utf8 bytes'''
        return binascii.unhexlify(s.encode('utf8'))

    def check_magic(self, hexcode, magic=dataIO.load_json("data/blockchain/magic.json")):
        '''Returns a string listing magic bytes found in the given hexcode and compared against the magic dictionary of keys to lists of values.

        This is the hex header search function.  It searches the line of hex for any of these known header hex values.
        '''
        return ' '.join('{} Found'.format(key)
                        for key, values in magic.items()
                        if all(v.lower() in hexcode for v in values))

    def check_hash(self, hexcode, sumcheck):
        '''
        This will return whether or not a wikileaks file hash is inside the blockchain
        '''
        return ' '.join('{}'.format(key)
                        for key, values in hashes[sumcheck].items()
                        if values in hexcode)

    def search_hex(self, hexdata, IO):
        revhex = "".join(reversed([hexdata[i:i+2] for i in range(0, len(hexdata), 2)]))
        hexmagic = self.check_magic(hexdata)
        revhexmagic = self.check_magic(revhex)
        if hexmagic != '':
            return hexmagic + " " + IO
        if revhexmagic != '':
            return revhexmagic + " " + IO + " reverse"
        else:
            return ''

    def search_words(self, data):
        count = 0
        try:
            for char in data:
                if ord(char) in range(20, 127):
                    count += 1
        except TypeError:
            for char in data:
                if char in range(20, 127):
                    count += 1
        try:
            if(count/len(data)) >= 0.75:
                return True
        except ZeroDivisionError:
            return False
        return False
            

    def split_long_text(self, data):
        return [data[i:i+1990] for i in range(0, len(data), 1990)]

    def remove_non_ascii(self, data):
        msg = b""
        for char in data:
            if char in range(0, 127):
                msg += bytes(chr(char).encode("utf8"))
        return msg

    @blockchain.command(pass_context=True, name="download", aliases=["dl"])
    async def transaction_download(self, ctx, transaction, IO="original"):
        """Downloads Data from the blockchain default is original data.
        IO is optional:
        input = i
        output = o
        satoshi = s
        Send a transaction id like the one below
        try: 4b0cd7e191ef0a14a9b6ab1c5900be534118c20a332ff26407648168d2722a2e o"""
        chn = ctx.message.channel
        await self.bot.send_typing(chn)
        if transaction in BADTRANSACTION:
            await self.bot.say("That transaction is black listed.")
            return
        try:
            hexdata = await self.get_data_local(transaction)
            inhex = await self.get_indata_local(transaction)
            _, _, data = self.length_checksum_data_from_rawdata(self.unhexutf8(hexdata))
            indata = self.unhexutf8(inhex)
            origdata = self.unhexutf8(hexdata)
        except:
            print("There was likely an incorrect transaction.")
            await self.bot.say("Sorry there is something wrong with that transaction.")
            return
        significanttx = ''
        significanttx += self.search_hex(hexdata, " output")
        significanttx += self.search_hex(inhex, " input")
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
        if self.search_words(origdata):
            significanttx += " ASCII letters found output"
        if self.search_words(indata):
            significanttx += " ASCII letters found input"
        # self.write("data/blockchain/" + IO + "data.txt", dataout, True, "wb")
        if significanttx != '':
            extension = "txt"
            await self.bot.say(significanttx)
            for words in self.list_words:
                if words in significanttx and "input" in significanttx:
                        indata = self.split_long_text(self.remove_non_ascii(indata))
                        for i in indata:
                            await self.bot.say("```" + i.decode('utf8') + "```")
                if words in significanttx and "output" in significanttx:
                    if "Satoshi" in significanttx:
                        data = self.split_long_text(self.remove_non_ascii(data))
                        for i in data:
                            await self.bot.say("```" + i.decode('utf8') + "```")
                    else:
                        data = self.split_long_text(self.remove_non_ascii(data))
                        for i in data:
                            await self.bot.say("```" + i.decode('utf8') + "```")
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
        filename = "data/blockchain/" + IO + "data.{}".format(extension)
        self.write(filename, dataout, True, "wb")
        await self.bot.send_file(chn, filename)
        if significanttx == '':
            await self.bot.say("Nothing significant in transaction `{}`".format(transaction))
            await self.bot.send_file(chn, filename)

    def write(self, filename, data, binary=True, mode='w', buffering=-1, silent=True, encoding="utf8"):
        '''Read a given filename opened with the given mode and buffering settings, returning that data or None if failure.
        Mode defaults to write.
        Negative buffering means system default for device.
        Buffering of 0 means unbuffered, 1 is lined buffered, and any other value is an approximate number of bytes.
        If silent is False and there is an error, then stderr will be output to.'''
        if binary:
            try:
                with open(filename, mode, buffering) as f:
                    f.write(data)
            except IOError as e:
                data = None
                print('Error: {}'.format(e), file=sys.stderr)
            return data
        else:
            try:
                with open(filename, mode, buffering) as f:
                    f.write(data.encode('utf8'))
            except IOError as e:
                data = None
                print('Error: {}'.format(e), file=sys.stderr)
            return data


def setup(bot):
    n = blockchain(bot)
    bot.add_cog(n)