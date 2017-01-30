# -*- coding: utf-8 -*-
'''dlfn class and methods'''

from __future__ import print_function
from . import satoshi
from . import blockchaininfo as online
from . import blockchainrpc as rpc
from .filesystem import read, readlines, write, newline
from .search import search_hex, check_hash, search_words

from timeit import default_timer as timer

import struct

RPCUSER, RPCPASS = read('rpclogin.txt', 'r').split()
SERVER = rpc.make_server(RPCUSER, RPCPASS)


class dlfn():
    FILENAME = ''
    RPCUSER, RPCPASS = read('blockchain/rpclogin.txt', 'r').split()
    SERVER = rpc.make_server(RPCUSER, RPCPASS)

    def __init__(self, SERVER, FILENAME='file'):
        self.FILENAME = FILENAME

    def save_data(self, transaction, LOCAL=False, INDIVIDUALFILE=False):
        if INDIVIDUALFILE:
            self.FILENAME = transaction
        if LOCAL:
            hexdata = rpc.get_data_local(transaction, self.SERVER)
            inhex = rpc.get_indata_local(transaction, self.SERVER)
        else:
            Page = online.get_blockchain_request('tx/{}'.format(transaction), show_adv='true')
            hexdata = online.get_data_online(transaction, Page)
            inhex = online.get_indata_online(transaction, Page)
        _, _, data = satoshi.length_checksum_data_from_rawdata(satoshi.unhexutf8(hexdata))
        indata = satoshi.unhexutf8(inhex)
        origdata = satoshi.unhexutf8(hexdata)

        significanttx = ''
        significanttx += search_hex(hexdata, " output")
        significanttx += search_hex(inhex, " input")
        # significanttx += check_hash(inhex+hexdata, 'ripemd160')
        if self.checksum(origdata):
            significanttx += " Satoshi Checksum found"
        if search_words(origdata):
            significanttx += " ASCII letters found output"
            print(origdata)
        if search_words(indata):
            significanttx += " ASCII letters found input"
        if significanttx != '':
            print(transaction + " " + significanttx)
            self.save_file(transaction + " " + significanttx + newline(), "significant.txt", False)
        if "Satoshi" in significanttx:
            self.save_file(data, self.FILENAME+"data.txt")
        self.save_file(indata, self.FILENAME+"indata.txt")     # saves the input script
        # self.save_file(data, self.FILENAME+"data.txt")         # saves binary data
        self.save_file(origdata, self.FILENAME+"origdata.txt", True)         # saves all binary data

    def get_tx_list(self, tx_list, LOCAL):
        """This function checks the blockchain for all transactions in the FILENAME document """
        for line in readlines(tx_list):
            blockhash = line.rstrip('\r\n')
            if blockhash:
                self.save_data(blockhash, LOCAL)

    def get_block_tx(self, start, end, LOCAL):
        """This function checks the blockchain for all transactions in the FILENAME document """
        if not end.isdigit():
            end = rpc.get_block_height(self.SERVER)
        for i in range(int(start), int(end)):
            start = timer()
            hashlist = rpc.get_block_transactions(i, self.SERVER)
            for tx in hashlist:
                self.save_data(tx, LOCAL)
            endtime = timer() - start
            print("Block number: {0} | Time to complete:{1:.2f}s | Number of transactions: {2}"
                  .format(i, endtime, len(hashlist)))

    def save_file(self, filename, dataout, binary=True):
        """
        This saves the data to the chosen
        filename in binary by appending the file
        """
        write(dataout, filename, binary, 'ab')

    def checksum(self, data):
        """
        verify's the checksum for files
        uploaded using the satoshi uploader
        does not work without the full file
        """
        length, checksum, data = satoshi.length_checksum_data_from_rawdata(data)
        return satoshi.verify_checksum_data(checksum, data)
