#!/usr/bin/python

from struct import pack, unpack, calcsize
from fifo import Fifo
from _binding import *


__all__ = [
    'LZO_MAGIC', 'MAX_BLOCK', 'Compress', 'compress', 'Decompress', 'decompress'
]
import _binding
__all__.extend(_binding.__all__)


LZO_MAGIC = 'LZO\x00'
MAX_BLOCK = 0x7fff

_BLOCK_HEADER_FORMAT = 'H'
_BLOCK_HEADER_LENGTH = calcsize(_BLOCK_HEADER_FORMAT)


class Compress(object):

    def __init__(self):
        self.__fifo = Fifo()
        self.__output = []
        self.__output.append(LZO_MAGIC)

    def __yield_output(self):
        output = ''.join(self.__output)
        self.__output = []
        return output

    def compress(self, data):
        self.__fifo.write(data)

        while True:
            block = self.__fifo.read(MAX_BLOCK)
            if not block:
                break
            data = lzo1x_1_compress(block)
            if len(data) >= len(block):
                self.__output.append(pack(_BLOCK_HEADER_FORMAT, len(block)))
                self.__output.append(block)
            else:
                self.__output.append(pack(_BLOCK_HEADER_FORMAT, len(data) | 0x8000))
                self.__output.append(data)
        return self.__yield_output()
        

def compress(plain):
    return Compress().compress(plain)


class Decompress(object):

    STATE_MAGIC = 0
    STATE_BLOCK_HEADER = 1
    STATE_BLOCK = 2

    def __init__(self):
        self.__buff = lzo_buffer(MAX_BLOCK)
        self.__fifo = Fifo()
        self.__output = []
        self.state = self.STATE_MAGIC

    def __yield_output(self):
        output = ''.join(self.__output)
        self.__output = []
        return output

    def decompress(self, data):
        self.__fifo.write(data)

        while True:

            # magic
            if self.state == self.STATE_MAGIC:
                magic = self.__fifo.readblock(len(LZO_MAGIC))
                if not magic:
                    break
                if magic != LZO_MAGIC:
                    raise Exception('Bad magic: %s' % magic)
                self.state = self.STATE_BLOCK_HEADER

            # block header
            if self.state == self.STATE_BLOCK_HEADER:
                header = self.__fifo.readblock(_BLOCK_HEADER_LENGTH)
                if not header:
                    break
                self.__block_length = unpack(_BLOCK_HEADER_FORMAT, header)[0]
                self.__block_compressed = self.__block_length & 0x8000
                self.__block_length ^= self.__block_compressed
                if self.__block_length:
                    self.state = self.STATE_BLOCK

            # block
            if self.state == self.STATE_BLOCK:
                block = self.__fifo.readblock(self.__block_length)
                if not block:
                    break
                if self.__block_compressed:
                    decomp = lzo1x_decompress(block, self.__buff)
                    self.__output.append(decomp)
                else:
                    self.__output.append(block)
                self.state = self.STATE_BLOCK_HEADER

        return self.__yield_output()


def decompress(data):
    return Decompress().decompress(data)


if __name__ == '__main__':
    import os
    import sys
    name = os.path.basename(sys.argv[0])
    if name == 'compress':
        l = Compress()
        while True:
            data = sys.stdin.read(4096)
            if not data:
                break
            sys.stdout.write(l.compress(data))
    elif name == 'decompress':
        l = Decompress()
        while True:
            data = sys.stdin.read(1024)
            if not data:
                break
            sys.stdout.write(l.decompress(data))
