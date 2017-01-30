# -*- coding: utf-8 -*-
'''Various search related functions'''
from __future__ import division
import json
from .filesystem import read
from binascii import hexlify

hashes = {hash: json.loads(read('data/wlhashes/{}.json'.format(hash)))
          for hash in ('md5', 'sha1', 'sha256', 'ripemd160')}

DEFAULT_MAGIC = {"DOC Header": ["d0cf11e0a1b11ae1"],
                 "DOC Footer": ["576f72642e446f63756d656e742e"],
                 "XLS Header": ["d0cf11e0a1b11ae1"],
                 "XLS Footer": ["feffffff000000000000000057006f0072006b0062006f006f006b00"],
                 "PPT Header": ["d0cf11e0a1b11ae1"],
                 "PPT Footer": ["a0461df0"],
                 "ZIP Header": ["504b030414"],
                 "ZIP Footer": ["504b050600"],
                 "ZIPLock Footer": ["504b030414000100630000000000"],
                 "JPG Header": ["ffd8ffe000104a464946000101"],
                 "GIF Header": ["474946383961"],
                 "GIF Footer": ["2100003b00"],
                 "PDF Header": ["25504446"],
                 "PDF-Header": ["2623323035"],
                 "PDF Footer": ["2525454f46"],
                 "Torrent Header": ["616e6e6f756e6365"],
                 "GZ Header": ["1f8b0808"],
                 "TAR Header": ["1f8b0800"],
                 "TAR.GZ Header": ["1f9d9070"],
                 "EPUB Header": ["504b03040a000200"],
                 "PNG Header": ["89504e470d0a1a0a"],
                 "8192 Header": ["6d51514e42"],
                 "4096 Header": ["6d51494e4246672f"],
                 "2048 Header": ["952e3e2e584b7a"],
                 "Secret Header": ["526172211a0700"],
                 "RAR Header": ["6d51454e424667"],
                 "UTF8 header": ["efedface"],
                 "OGG Header": ["4f676753"],
                 "WAV Header": ["42494646", "57415645"],
                 "AVI Header": ["42494646", "41564920"],
                 "MIDI Header": ["4d546864"],
                 "7z Header": ["377abcaf271c"],
                 "7z Footer": ["0000001706"],
                 "DMG Header": ["7801730d626260"],
                 "Wikileaks": ["57696b696c65616b73"],
                 "Julian": ["4a756c69616e"],
                 "Assange": ["417373616e6765"],
                 "Mendax": ["4d656e646178"],
                 "eta numeris": ["392d8a3eea2527d6ad8b1ebbab6ad"],
                 "sin topper": ["d6c4c5cc97f9cb8849d9914e516f9"],
                 "project runway": ["847d8d6ea4edd8583d4a7dc3deeae"],
                 "7FG final request": ["831cf9c1c534ecdae63e2c8783eb9"],
                 "fall of cassandra": ["2b6dae482aede5bac99b7d47abdb3"]}


def check_magic(hexcode, magic=DEFAULT_MAGIC):
    '''Returns a string listing magic bytes found in the given hexcode and compared against the magic dictionary of keys to lists of values.

    This is the hex header search function.  It searches the line of hex for any of these known header hex values.
    '''
    return ' '.join('{} Found'.format(key)
                    for key, values in magic.items()
                    if all(v.lower() in hexcode for v in values))


def check_hash(hexcode, sumcheck):
    '''
    This will return whether or not a wikileaks file hash is inside the blockchain
    '''
    return ' '.join('{}'.format(key)
                    for key, values in hashes[sumcheck].items()
                    if values in hexcode)


def search_hex(hexdata, IO):
    revhex = "".join(reversed([hexdata[i:i+2] for i in range(0, len(hexdata), 2)]))
    hexmagic = check_magic(hexdata)
    revhexmagic = check_magic(revhex)
    if hexmagic != '':
        return hexmagic + " " + IO
    if revhexmagic != '':
        return revhexmagic + " " + IO + " reverse"
    else:
        return ''


def search_words(data):
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



def search_hashes(allhex):
    '''
    This method is obsolete with new hash dictionary

    md5hashsearch = check_hash(allhex, 'md5')           # Searches in hex data
    sha1hashsearch = check_hash(allhex, 'sha1')         # for hashes
    sha256hashsearch = check_hash(allhex, 'sha256')
    if md5hashsearch != '':
        return md5hashsearch + " md5"
    if sha1hashsearch != '':
        return sha1hashsearch + " sha1"
    if sha256hashsearch != '':
        return sha256hashsearch + " sha256"
    else:
        return ''
    '''

def sha256_sum(self, data):
    """
    Builds and checks a list of hashes from data
    downloaded from the blockchain
    useful to find duplicate data
    TODO: figure out how to save as dictionary file and impliment into searching


    hashsum = hashlib.sha256(data)
    hashexists = False
    with open("hashindex.txt", "a+") as hashfile:
        for hashes in hashfile:
            if hashsum.hexdigest() == hashes.strip():
                hashexists = True

        if not hashexists:
            hashfile.writelines(hashsum.hexdigest()+newline())
            hashexists = False
    hashfile.close()
    return hashexists
    """

def crc(self, filename):
    """
    Should be used to determine if filename
    is garbage or is part of the file

    prev = 0
    for eachLine in open(filename, "rb"):
        prev = zlib.crc32(eachLine, prev)
        print (prev)
    return "%X" % (prev & 0xFFFFFFFF)
"""
