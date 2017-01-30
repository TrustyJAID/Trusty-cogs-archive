# -*- coding: utf-8 -*-
'''filesystem functions'''

from __future__ import print_function
import os
import sys
import platform


def read(filename, mode='r', buffering=-1, default=None, silent=True):
    '''Read a given filename opened with the given mode and buffering settings, returning that data or the default.
    Mode defaults to read.
    Negative buffering means system default for device.
    Buffering of 0 means unbuffered, 1 is lined buffered, and any other value is an approximate number of bytes.
    Default is None unless otherwise specified.
    If silent is False and there is an error, then stderr will be output to.'''
    data = default
    try:
        with open(filename, mode, buffering) as f:
            data = f.read()
    except IOError as e:
        print('Error: {}'.format(e), file=sys.stderr)
    return data


def readlines(filename, mode='r', buffering=-1, default=[], silent=True):
    '''Read a given filename opened with the given mode and buffering settings, returning that data as split lines or the default.
    Mode defaults to read.
    Negative buffering means system default for device.
    Buffering of 0 means unbuffered, 1 is lined buffered, and any other value is an approximate number of bytes.
    Default is an empty list unless otherwise specified.
    If silent is False and there is an error, then stderr will be output to.'''
    data = default
    try:
        with open(filename, mode, buffering) as f:
            data = f.readlines()
    except IOError as e:
        print('Error: {}'.format(str(e)), file=sys.stderr)
    return data


def write(filename, data, binary=True, mode='w', buffering=-1, silent=True, encoding="utf8"):
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


def newline():
    return '\r\n' if platform.system() == "Windows" else '\n'
