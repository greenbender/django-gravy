from ctypes.util import find_library
from ctypes import *


__all__ = [
    'liblzo', 'LZO_E_OK', 'LZO_E_ERROR', 'LZO_E_OUT_OF_MEMORY',
    'LZO_E_NOT_COMPRESSIBLE', 'LZO_E_INPUT_OVERRUN', 'LZO_E_OUTPUT_OVERRUN',
    'LZO_E_LOOKBEHIND_OVERRUN', 'LZO_E_EOF_NOT_FOUND',
    'LZO_E_INPUT_NOT_CONSUMED', 'LZO_E_NOT_YET_IMPLEMENTED',
    'LZO_E_INVALID_ARGUMENT', 'LZO_E_INVALID_ALIGNMENT',
    'LZO_E_OUTPUT_NOT_CONSUMED', 'LZO_E_INTERNAL_ERROR', 'lzo_buffer',
    'lzo1x_1_compress', 'lzo1x_decompress'
]


liblzo = CDLL(find_library('lzo2'))


# types
lzo_uint = c_uint
lzo_uintp = POINTER(lzo_uint)
lzo_bytep = POINTER(c_ubyte)
lzo_voidp = c_void_p
lzo_sizeof_dict_t = sizeof(lzo_bytep)


# constants
LZO1_MEM_COMPRESS = 8192 * lzo_sizeof_dict_t
LZO1X_MEM_COMPRESS = LZO1X_1_MEM_COMPRESS = 16384 * lzo_sizeof_dict_t
LZO1_99_MEM_COMPRESS = 65536 * lzo_sizeof_dict_t
LZO1_MEM_DECOMPRESS = 0


# errors
LZO_E_OK = 0
LZO_E_ERROR = -1
LZO_E_OUT_OF_MEMORY = -2
LZO_E_NOT_COMPRESSIBLE = -3
LZO_E_INPUT_OVERRUN = -4
LZO_E_OUTPUT_OVERRUN = -5
LZO_E_LOOKBEHIND_OVERRUN = -6
LZO_E_EOF_NOT_FOUND = -7
LZO_E_INPUT_NOT_CONSUMED = -8
LZO_E_NOT_YET_IMPLEMENTED = -9
LZO_E_INVALID_ARGUMENT = -10
LZO_E_INVALID_ALIGNMENT = -11
LZO_E_OUTPUT_NOT_CONSUMED = -12
LZO_E_INTERNAL_ERROR = -99


# lzo_buffer
def lzo_buffer(size):
    return create_string_buffer(size)


# lzo1x_1_compress
def lzo1x_1_compress(src, dst=None):
    if dst is None:
        dst = lzo_buffer(len(src) + len(src)/16 + 64 + 3)
    dst_len = lzo_uint(sizeof(dst))
    wrkmem = create_string_buffer(LZO1X_1_MEM_COMPRESS)
    result = liblzo.lzo1x_1_compress(src, len(src), dst, byref(dst_len), wrkmem)
    if result != LZO_E_OK:
        raise Exception("LZO Error: %d" % result)
    return dst[:dst_len.value]


# lzo1x_decompress
def lzo1x_decompress(src, dst):
    dst_len = lzo_uint(sizeof(dst))
    result = liblzo.lzo1x_decompress(src, len(src), dst, byref(dst_len), None)
    if result != LZO_E_OK:
        raise Exception("LZO Error: %d" % result)
    return dst[:dst_len.value]


# test
if __name__ == '__main__':
    import sys
    plain = sys.stdin.read()
    compressed = lzo1_compress(plain)
    decompressed = lzo1_decompress(compressed, lzo_buffer(len(plain)))
    sys.stdout.write(decompressed)
