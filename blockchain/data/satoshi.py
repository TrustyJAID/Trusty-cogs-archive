# -*- coding: utf-8 -*-
'''satoshi downloader and uploader functions'''

from binascii import crc32, hexlify, unhexlify
from decimal import Decimal

import io
import os
import random
import struct
import sys

COIN = 100000000

OP_CHECKSIG = b'\xac'
OP_CHECKMULTISIG = b'\xae'
OP_PUSHDATA1 = b'\x4c'
OP_DUP = b'\x76'
OP_HASH160 = b'\xa9'
OP_EQUALVERIFY = b'\x88'


def unhexutf8(s):
    '''Return unhexlified string data encoded as utf8 bytes'''
    return unhexlify(s.encode('utf8'))


def rawdata_from_jsonrpc_rawtx(tx):
    '''Returns raw data as utf8 encoded bytes from a `jsonrpc.getrawtransaction(txid, 1)`'''
    data = b''
    for txout in tx['vout'][0:-2]:
        for op in txout['scriptPubKey']['asm'].split(' '):
            if not op.startswith('OP_') and len(op) >= 40:
                data = unhexutf8(op)
    return data


def length_checksum_data_from_rawdata(rawdata):
    '''Returns the length, checksum, and data bytes from the given rawdata'''
    try:
        length = struct.unpack('<L', rawdata[0:4])[0]
        return length, struct.unpack('<L', rawdata[4:8])[0], rawdata[8:8+length]
    except struct.error as e:
        print(e)
        return None, None, rawdata


def length_byte(data):
    '''Returns the length of the data as a 32 bit value.'''
    return struct.pack('<L', len(data))


def checksum_byte(data):
    '''Returns the crc32 checksum value for the given data'''
    return struct.pack('<L', crc32(data) & 0xffffffff)


def make_rawdata(data):
    return b''.join((length_byte(data),
                     checksum_byte(data),
                     data))


def verify_checksum_data(checksum, data):
    '''Returns true if the checksum matches the crc32 checksum of the data'''
    return crc32(data) & 0xffffffff == checksum


def verify_rawdata(rawdata):
    '''Returns true if the checksum in the rawdata matches the checksum of the data'''
    _, checksum, data = length_checksum_data_from_rawdata(rawdata)
    return crc32(data) & 0xffffffff == checksum


###
### TODO: Change these original functions from satoshi uploader to be more pure
### TODO: If they have a "proxy", that is a global jsonrpc client that needs to be factored out
###


def select_txins(value, SERVER=None):
    unspent = list(SERVER.listunspent())
    random.shuffle(unspent)

    r = []
    total = 0
    for tx in unspent:
        total += tx['amount']
        r.append(tx)

        if total >= value:
            break

    if total < value:
        return None
    else:
        return (r, total)


def varint(n):
    if n < 0xfd:
        return bytes([n])
    elif n < 0xffff:
        return b'\xfd' + struct.pack('<H',n)
    else:
        assert False


def packtxin(prevout, scriptSig, seq=0xffffffff):
    return prevout[0][::-1] + struct.pack('<L',prevout[1]) + varint(len(scriptSig)) + scriptSig + struct.pack('<L', seq)


def packtxout(value, scriptPubKey):
    return struct.pack('<Q',int(value*COIN)) + varint(len(scriptPubKey)) + scriptPubKey


def packtx(txins, txouts, locktime=0):
    r = b'\x01\x00\x00\x00' # version
    r += varint(len(txins))

    for txin in txins:
        r += packtxin((unhexutf8(txin['txid']),txin['vout']), b'')

    r += varint(len(txouts))

    for (value, scriptPubKey) in txouts:
        r += packtxout(value, scriptPubKey)

    r += struct.pack('<L', locktime)
    return r


def pushdata(data):
    assert len(data) < OP_PUSHDATA1[0]
    return bytes([len(data)]) + data


def pushint(n):
    assert 0 < n <= 16
    return bytes([0x51 + n-1])


def addr2bytes(s):
    digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = 0
    for c in s:
        n *= 58
        if c not in digits58:
            raise ValueError
        n += digits58.index(c)

    h = '%x' % n
    if len(h) % 2:
        h = '0' + h

    for c in s:
        if c == digits58[0]:
            h = '00' + h
        else:
            break
    return unhexutf8(h)[1:-4] # skip version and checksum


def checkmultisig_scriptPubKey_dump(fd):
    data = fd.read(65*3)
    if not data:
        return None

    r = pushint(1)

    n = 0
    while data:
        chunk = data[0:65]
        data = data[65:]

        if len(chunk) < 33:
            chunk += b'\x00'*(33-len(chunk))
        elif len(chunk) < 65:
            chunk += b'\x00'*(65-len(chunk))

        r += pushdata(chunk)
        n += 1

    r += pushint(n) + OP_CHECKMULTISIG
    return r
