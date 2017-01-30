# -*- coding: utf-8 -*-
'''blockchain rpc related functions'''

import jsonrpclib

DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 8332
DEFAULT_SCHEMA = 'http'


def make_server_from_url(url):
    '''Return a `jsonrpclib.Server` instance initialized with the given url'''
    return jsonrpclib.Server(url)


def make_server_url(username, password, hostname=DEFAULT_PORT, port=DEFAULT_PORT, schema=DEFAULT_SCHEMA):
    return '{schema}://{username}:{password}@{hostname}:{port}'.format(schema=schema,
                                                                       username=username,
                                                                       password=password,
                                                                       hostname=hostname,
                                                                       port=port)


def make_server(username, password, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT, schema=DEFAULT_SCHEMA):
    return make_server_from_url(make_server_url(username=username,
                                                password=password,
                                                hostname=hostname,
                                                port=port,
                                                schema=schema))


def get_block_height(SERVER):
    return SERVER.getblockcount()


def get_block_transactions(blockindex, SERVER):
    """
    Gets transaction data from block ranges
    """
    txlist = []
    blockhash = SERVER.getblockhash(blockindex)  # Gets the block hash from the block index number
    for tx in SERVER.getblock(blockhash)['tx']:  # Gets all transactions from block hash
        txlist += [tx]
    return txlist


def get_data_local(transaction, SERVER):
    """
    Downloads data from Bitcoin Core RPC and returns hex
    """
    rawTx = SERVER.getrawtransaction(transaction)
    tx = SERVER.decoderawtransaction(rawTx)
    return ''.join(op
                   for txout in tx.get('vout')
                   for op in txout.get('scriptPubKey', {'asm': ''}).get('asm', '').split()
                   if not op.startswith('OP_') and len(op) >= 40)


def get_indata_local(transaction, SERVER):
    rawTx = SERVER.getrawtransaction(transaction)
    tx = SERVER.decoderawtransaction(rawTx)
    return ''.join(inop
                   for txin in tx.get('vin')
                   for inop in txin.get('scriptSig', {'hex': ''}).get('hex', '').split())

