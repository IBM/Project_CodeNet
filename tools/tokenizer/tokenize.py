#!/usr/bin/env python

# Copyright IBM Corporation 2021, 2022
# Written by Geert Janssen <geert@us.ibm.com>

# Simple ctypes-based Python wrapper of libtoken.so
# See ctypes documentation: https://docs.python.org/3/library/ctypes.html
# This Python script works with versions 2.6, 2.7, and 3.5

import sys
from ctypes import *

# Load the shared object (expects it in current directory):
libtoken = CDLL('./libtoken.so')

# Define the exported function signatures:
libtoken.C_tokenize.argtypes = (POINTER(c_char_p),
                                POINTER(c_char_p),
                                POINTER(c_uint),
                                POINTER(c_uint),
                                POINTER(c_uint))
libtoken.open_as_stdin.argtypes = (c_char_p,)

# 'Declare' the C function argument types:
_token  = c_char_p()
_kind   = c_char_p()
_linenr = c_uint()
_column = c_uint()
_pos    = c_uint()

# Token generator:
def token():
    global _token, _kind, _linenr, _column, _pos

    # C_tokenize returns 0 upon end-of-file.
    while int(libtoken.C_tokenize(byref(_token), byref(_kind), byref(_linenr),
                                  byref(_column), byref(_pos))):
        # Turn ctypes into real Python values:
        lin = _linenr.value
        col = _column.value
        pos = _pos.value # not used for now
        clas = _kind.value.decode()
        text = _token.value.decode()
        yield (lin,col,clas,text)

if len(sys.argv) == 1:
    for tok in token():
        print('[%u:%u] %s, %s' % tok)
else:
    for file in sys.argv[1:]:
        # Set C filename global and reopen as stdin:
        b_str = file.encode('utf-8') # need handle b_str to retain as C pointer
        libtoken.open_as_stdin(b_str)

        # Access C globals:
        filename = c_char_p.in_dll(libtoken, 'filename')
        print('[0:0] filename, %s' % filename.value.decode())

        for tok in token():
            print('[%u:%u] %s, %s' % tok)

        # Reset globals:
        c_uint.in_dll(libtoken, 'linenr').value = 1
        c_uint.in_dll(libtoken, 'column').value = 0
        c_uint.in_dll(libtoken, 'char_count').value = 0
        c_uint.in_dll(libtoken, 'utf8_count').value = 0
