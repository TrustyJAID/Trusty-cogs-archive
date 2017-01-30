# -*- coding: utf-8 -*-
'''blockchain.info related functions'''
import json
import os
import time

try:
    # Python 3
    Python3 = True
    import urllib.request
    import urllib.parse
    import urllib.error
    import collections
except:
    # Python 2
    Python3 = False
    import urllib
    import urllib2

BLOCKCHAIN_URI = 'https://blockchain.info'


def make_blockchain_url(path, uri=BLOCKCHAIN_URI, **kwargs):
    '''
    Return a blockchain.info URL with the given path
    appended to the uri and urlencoded keyword arguments appended.
    '''
    if Python3:
        return '{}/{}?{}'.format(uri, path, urllib.parse.urlencode(kwargs))
    else:
        return '{}/{}?{}'.format(uri, path, urllib.urlencode(kwargs))


def get_blockchain_request(path, uri=BLOCKCHAIN_URI, **kwargs):
    '''
    Return a response from urllib2.urlopen with the URL built
    by concatenating the uri, path, and urlencoded keyword arguments.
    '''
    if Python3:
        return urllib.request.urlopen(make_blockchain_url(path, uri=uri, **kwargs))
    else:
        return urllib2.urlopen(make_blockchain_url(path, uri=uri, **kwargs))


def get_blockchain_transaction(transaction, format, uri=BLOCKCHAIN_URI):
    '''Return data for a transaction by tx_index or tx_hash in the given format.
    format can be "html", "json", or "hex".'''
    return get_blockchain_request('tx/{}'.format(transaction), format=format, uri=uri)


def get_blockchain_transaction_json(transaction, uri=BLOCKCHAIN_URI):
    '''Return JSON data for a transaction by tx_index or tx_hash.'''
    return get_blockchain_transaction(transaction, format='json', uri=uri)


def get_blockchain_transaction_hex(transaction, uri=BLOCKCHAIN_URI):
    '''Return raw hex data for a transaction by tx_index or tx_hash.'''
    return get_blockchain_transaction(transaction, format='hex', uri=uri)


def get_blockchain_block_height_json(height, uri=BLOCKCHAIN_URI):
    '''Return JSON data with array of blocks at specified height.'''
    return get_blockchain_request('block-height/{}'.format(height), format='json', uri=uri)


def get_blockchain_block_height(height, uri=BLOCKCHAIN_URI):
    '''Return array of blocks at specified height or empty list.'''
    return json.loads(get_blockchain_block_height_json(height)).get('blocks', [], uri=uri)


def get_blockchain_rawblock_json(block, uri=BLOCKCHAIN_URI):
    '''Return JSON data for a given block_index or block_hash'''
    return get_blockchain_request('rawblock/{}'.format(block), format='json', uri=uri)


def get_blockchain_rawaddr_json(address, limit=50, offset=0, uri=BLOCKCHAIN_URI):
    '''Return JSON data for a given address, limit, and offset.'''
    return get_blockchain_request('rawaddr/{}'.format(address), format='json', limit=limit, offset=offset, uri=uri)

def get_latest_block_height_json(uri=BLOCKCHAIN_URI):
    '''Returns JSON data for last block height'''
    return get_blockchain_request('latestblock', format='json', uri=uri)

def get_latest_block_height(uri=BLOCKCHAIN_URI):
    '''Return value for latest block height'''
    return json.loads(get_latest_block_height_json())["height"]


def get_blockchain_rawaddr(address, limit=50, offset=0, silent=True, uri=BLOCKCHAIN_URI):
    error = True
    if Python3:
        while error:
            try:
                dat = get_blockchain_rawaddr_json(address, limit=limit, offset=offset, uri=uri)
                error = False
            except urllib.error.URLError as e:
                if not silent:
                    print(('Error: Trying to open address {} from blockchain.info: '.format(address, e.reason)))
        return json.loads(dat.read().decode())
    else:
        while error:
            try:
                dat = get_blockchain_rawaddr_json(address, limit=limit, offset=offset, uri=uri)
                error = False
            except urllib2.URLError as e:
                if not silent:
                    print('Error: Trying to open address {} from blockchain.info: '.format(address, e.reason))
        return json.loads(dat.read().decode())


def get_txs_from_blockchain_json(data):
    return [tx.get('hash').encode('ascii') for tx in data.get('txs', [])]


def get_tx_from_online(address, limit=50, sleep=1, callback=None):
    address = address.rstrip('\r\n')
    offset = 0
    data = get_blockchain_rawaddr(address, limit=limit, offset=offset, silent=False)
    n_tx = data['n_tx']
    txlist = get_txs_from_blockchain_json(data)

    if Python3:
        while len(txlist) < n_tx:
            if callback and isinstance(callback, collections.Callable):
                callback(txlist, n_tx)
            offset += 50
            txlist.extend(get_txs_from_blockchain_json(get_blockchain_rawaddr(address, limit=limit, offset=offset, silent=True)))
            # Lets be nice to blockchain.info
            if sleep:
                time.sleep(sleep)
    else:
        while len(txlist) < n_tx:
            if callback and callable(callback):
                callback(txlist, n_tx)
            offset += 50
            txlist.extend(get_txs_from_blockchain_json(get_blockchain_rawaddr(address, limit=limit, offset=offset, silent=True)))
            # Lets be nice to blockchain.info
            if sleep:
                time.sleep(sleep)

    return txlist


def get_data_online(transaction, Page):
    """
    Downloads the data from blockchain.info
    TODO: Change the data collection to json
    """
    hexdata = b''
    atoutput = False
    for line in Page:
        if b'Output Scripts' in line:
            atoutput = True

        if b'</table>' in line:
            atoutput = False

        if atoutput:
            if len(line) > 100:
                chunks = line.split(b' ')
                for c in chunks:
                    if b'O' not in c and b'\n' not in c and b'>' not in c and b'<' not in c:
                        hexdata += c
    return hexdata.decode('utf8')


def get_indata_online(transaction, Page):
    """
    Downloads the input scrip data from blockchain.info
    TODO: Change the data collection to json
    """
    inhex = b''
    inoutput = False
    for line in Page:

        if b'Input Scripts' in line:
            inoutput = False

        if b'</table>' in line:
            inoutput = False

        if inoutput:
            if len(line) > 100:
                chunks = line.split(b' ')
                for c in chunks:
                    print(c)
                    if b'O' not in c and b'\n' not in c and b'>' not in c and b'<' not in c:
                        inhex += c

    return inhex.decode('utf8')
