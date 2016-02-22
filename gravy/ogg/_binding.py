from ctypes.util import find_library
from ctypes import *


# library
libogg = CDLL(find_library('ogg'))


# types
c_uchar_p = POINTER(c_ubyte)

c_int_p = POINTER(c_int)

ogg_int64_t = c_longlong
ogg_int64_t_p = POINTER(ogg_int64_t)

class ogg_iovec_t(Structure):
    _fields_ = [
        ('iov_base', c_void_p),
        ('iov_len', c_size_t),
    ]
ogg_iovec_t_p = POINTER(ogg_iovec_t)

class oggpack_buffer(Structure):
    _fields_ = [
        ('endbyte', c_long),
        ('endbit', c_int),
        ('buffer', c_uchar_p),
        ('ptr', c_uchar_p),
        ('storage', c_long),
    ]
oggpack_buffer_p = POINTER(oggpack_buffer)

class ogg_packet(Structure):
    _fields_ = [
        ('packet', c_uchar_p),
        ('bytes', c_long),
        ('b_o_s', c_long),
        ('e_o_s', c_long),
        ('granulepos', ogg_int64_t),
        ('packetno', ogg_int64_t),
    ]
ogg_packet_p = POINTER(ogg_packet)

class ogg_page(Structure):
    _fields_ = [
        ('header', c_uchar_p),
        ('header_len', c_long),
        ('body', c_uchar_p),
        ('body_len', c_long),
    ]
ogg_page_p = POINTER(ogg_page)

class ogg_stream_state(Structure):
    _fields_ = [
        ('body_data', c_uchar_p),
        ('body_storage', c_long),
        ('body_fill', c_long),
        ('body_returned', c_long),
        ('lacing_vals', c_int_p),
        ('granule_vals', ogg_int64_t_p),
        ('lacing_storage', c_long),
        ('lacing_fill', c_long),
        ('lacing_packet', c_long),
        ('lacing_returned', c_long),
        ('header', c_ubyte * 282),
        ('header_fill', c_int),
        ('e_o_s', c_int),
        ('b_o_s', c_int),
        ('serialno', c_long),
        ('pageno', c_long),
        ('packetno', ogg_int64_t),
        ('granulepos', ogg_int64_t),
    ]
ogg_stream_state_p = POINTER(ogg_stream_state)

class ogg_sync_state(Structure):
    _fields_ = [
        ('data', c_uchar_p),
        ('storage', c_int),
        ('fill', c_int),
        ('returned', c_int),
        ('unsynced', c_int),
        ('headerbytes', c_int),
        ('bodybytes' , c_int),
    ]
ogg_sync_state_p = POINTER(ogg_sync_state)


# functions
ogg_stream_init = libogg.ogg_stream_init
ogg_stream_init.argtypes = [ogg_stream_state_p, c_int]
ogg_stream_init.restype = c_int

ogg_stream_clear = libogg.ogg_stream_clear
ogg_stream_clear.argtypes = [ogg_stream_state_p]
ogg_stream_clear.restype = c_int

ogg_stream_reset = libogg.ogg_stream_clear
ogg_stream_reset.argtypes = [ogg_stream_state_p]
ogg_stream_reset.restype = c_int

ogg_stream_packetin = libogg.ogg_stream_packetin
ogg_stream_packetin.argtypes = [ogg_stream_state_p, ogg_packet_p]
ogg_stream_packetin.resype = c_int

ogg_stream_pageout = libogg.ogg_stream_pageout
ogg_stream_pageout.argtypes = [ogg_stream_state_p, ogg_page_p]
ogg_stream_pageout.resype = c_int

ogg_stream_flush = libogg.ogg_stream_flush
ogg_stream_flush.argtypes = [ogg_stream_state_p, ogg_page_p]
ogg_stream_flush.resype = c_int

ogg_stream_destroy = libogg.ogg_stream_clear
ogg_stream_destroy.argtypes = [ogg_stream_state_p]
ogg_stream_destroy.restype = c_int
