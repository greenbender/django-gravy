from ctypes.util import find_library
from ctypes import *
from os import SEEK_SET, SEEK_CUR, SEEK_END


# library
libsndfile = CDLL(find_library('sndfile'))


# constants
SF_FORMAT_WAV = 0x010000
SF_FORMAT_AIFF = 0x020000
SF_FORMAT_AU = 0x030000
SF_FORMAT_RAW = 0x040000
SF_FORMAT_PAF = 0x050000
SF_FORMAT_SVX = 0x060000
SF_FORMAT_NIST = 0x070000
SF_FORMAT_VOC = 0x080000
SF_FORMAT_IRCAM = 0x0A0000
SF_FORMAT_W64 = 0x0B0000
SF_FORMAT_MAT4 = 0x0C0000
SF_FORMAT_MAT5 = 0x0D0000
SF_FORMAT_PVF = 0x0E0000
SF_FORMAT_XI = 0x0F0000
SF_FORMAT_HTK = 0x100000
SF_FORMAT_SDS = 0x110000
SF_FORMAT_AVR = 0x120000
SF_FORMAT_WAVEX = 0x130000
SF_FORMAT_SD2 = 0x160000
SF_FORMAT_FLAC = 0x170000
SF_FORMAT_CAF = 0x180000
SF_FORMAT_WVE = 0x190000
SF_FORMAT_OGG = 0x200000
SF_FORMAT_MPC2K = 0x210000
SF_FORMAT_RF64 = 0x220000
SF_FORMAT_PCM_S8 = 0x0001
SF_FORMAT_PCM_16 = 0x0002
SF_FORMAT_PCM_24 = 0x0003
SF_FORMAT_PCM_32 = 0x0004
SF_FORMAT_PCM_U8 = 0x0005
SF_FORMAT_FLOAT = 0x0006
SF_FORMAT_DOUBLE = 0x0007
SF_FORMAT_ULAW = 0x0010
SF_FORMAT_ALAW = 0x0011
SF_FORMAT_IMA_ADPCM = 0x0012
SF_FORMAT_MS_ADPCM = 0x0013
SF_FORMAT_GSM610 = 0x0020
SF_FORMAT_VOX_ADPCM = 0x0021
SF_FORMAT_G721_32 = 0x0030
SF_FORMAT_G723_24 = 0x0031
SF_FORMAT_G723_40 = 0x0032
SF_FORMAT_DWVW_12 = 0x0040
SF_FORMAT_DWVW_16 = 0x0041
SF_FORMAT_DWVW_24 = 0x0042
SF_FORMAT_DWVW_N = 0x0043
SF_FORMAT_DPCM_8 = 0x0050
SF_FORMAT_DPCM_16 = 0x0051
SF_FORMAT_VORBIS = 0x0060
SF_ENDIAN_FILE = 0x00000000
SF_ENDIAN_LITTLE = 0x10000000
SF_ENDIAN_BIG = 0x20000000
SF_ENDIAN_CPU = 0x30000000
SF_FORMAT_SUBMASK = 0x0000FFFF
SF_FORMAT_TYPEMASK = 0x0FFF0000
SF_FORMAT_ENDMASK = 0x30000000
SFC_GET_LIB_VERSION = 0x1000
SFC_GET_LOG_INFO = 0x1001
SFC_GET_CURRENT_SF_INFO = 0x1002
SFC_GET_NORM_DOUBLE = 0x1010
SFC_GET_NORM_FLOAT = 0x1011
SFC_SET_NORM_DOUBLE = 0x1012
SFC_SET_NORM_FLOAT = 0x1013
SFC_SET_SCALE_FLOAT_INT_READ = 0x1014
SFC_SET_SCALE_INT_FLOAT_WRITE = 0x1015
SFC_GET_SIMPLE_FORMAT_COUNT = 0x1020
SFC_GET_SIMPLE_FORMAT = 0x1021
SFC_GET_FORMAT_INFO = 0x1028
SFC_GET_FORMAT_MAJOR_COUNT = 0x1030
SFC_GET_FORMAT_MAJOR = 0x1031
SFC_GET_FORMAT_SUBTYPE_COUNT = 0x1032
SFC_GET_FORMAT_SUBTYPE = 0x1033
SFC_CALC_SIGNAL_MAX = 0x1040
SFC_CALC_NORM_SIGNAL_MAX = 0x1041
SFC_CALC_MAX_ALL_CHANNELS = 0x1042
SFC_CALC_NORM_MAX_ALL_CHANNELS = 0x1043
SFC_GET_SIGNAL_MAX = 0x1044
SFC_GET_MAX_ALL_CHANNELS = 0x1045
SFC_SET_ADD_PEAK_CHUNK = 0x1050
SFC_SET_ADD_HEADER_PAD_CHUNK = 0x1051
SFC_UPDATE_HEADER_NOW = 0x1060
SFC_SET_UPDATE_HEADER_AUTO = 0x1061
SFC_FILE_TRUNCATE = 0x1080
SFC_SET_RAW_START_OFFSET = 0x1090
SFC_SET_DITHER_ON_WRITE = 0x10A0
SFC_SET_DITHER_ON_READ = 0x10A1
SFC_GET_DITHER_INFO_COUNT = 0x10A2
SFC_GET_DITHER_INFO = 0x10A3
SFC_GET_EMBED_FILE_INFO = 0x10B0
SFC_SET_CLIPPING = 0x10C0
SFC_GET_CLIPPING = 0x10C1
SFC_GET_INSTRUMENT = 0x10D0
SFC_SET_INSTRUMENT = 0x10D1
SFC_GET_LOOP_INFO = 0x10E0
SFC_GET_BROADCAST_INFO = 0x10F0
SFC_SET_BROADCAST_INFO = 0x10F1
SFC_GET_CHANNEL_MAP_INFO = 0x1100
SFC_SET_CHANNEL_MAP_INFO = 0x1101
SFC_RAW_DATA_NEEDS_ENDSWAP = 0x1110
SFC_WAVEX_SET_AMBISONIC = 0x1200
SFC_WAVEX_GET_AMBISONIC = 0x1201
SFC_SET_VBR_ENCODING_QUALITY = 0x1300
SFC_TEST_IEEE_FLOAT_REPLACE = 0x6001
SFC_SET_ADD_DITHER_ON_WRITE = 0x1070
SFC_SET_ADD_DITHER_ON_READ = 0x1071
SF_STR_TITLE = 0x01
SF_STR_COPYRIGHT = 0x02
SF_STR_SOFTWARE = 0x03
SF_STR_ARTIST = 0x04
SF_STR_COMMENT = 0x05
SF_STR_DATE = 0x06
SF_STR_ALBUM = 0x07
SF_STR_LICENSE = 0x08
SF_STR_TRACKNUMBER = 0x09
SF_STR_GENRE = 0x10
SF_STR_FIRST = SF_STR_TITLE
SF_STR_LAST = SF_STR_GENRE
SF_FALSE = 0
SF_TRUE = 1
SFM_READ = 0x10
SFM_WRITE = 0x20
SFM_RDWR = 0x30
SF_AMBISONIC_NONE = 0x40
SF_AMBISONIC_B_FORMAT = 0x41
SF_ERR_NO_ERROR = 0
SF_ERR_UNRECOGNISED_FORMAT = 1
SF_ERR_SYSTEM = 2
SF_ERR_MALFORMED_FILE = 3
SF_ERR_UNSUPPORTED_ENCODING = 4
SF_CHANNEL_MAP_INVALID = 0
SF_CHANNEL_MAP_MONO = 1
SF_CHANNEL_MAP_LEFT = 2
SF_CHANNEL_MAP_RIGHT = 3
SF_CHANNEL_MAP_CENTER = 4
SF_CHANNEL_MAP_FRONT_LEFT = 5
SF_CHANNEL_MAP_FRONT_RIGHT = 6
SF_CHANNEL_MAP_FRONT_CENTER = 7
SF_CHANNEL_MAP_REAR_CENTER = 8
SF_CHANNEL_MAP_REAR_LEFT = 9
SF_CHANNEL_MAP_REAR_RIGHT = 10
SF_CHANNEL_MAP_LFE = 11
SF_CHANNEL_MAP_FRONT_LEFT_OF_CENTER = 12
SF_CHANNEL_MAP_FRONT_RIGHT_OF_CENTER = 13
SF_CHANNEL_MAP_SIDE_LEFT = 14
SF_CHANNEL_MAP_SIDE_RIGHT = 15
SF_CHANNEL_MAP_TOP_CENTER = 16
SF_CHANNEL_MAP_TOP_FRONT_LEFT = 17
SF_CHANNEL_MAP_TOP_FRONT_RIGHT = 18
SF_CHANNEL_MAP_TOP_FRONT_CENTER = 19
SF_CHANNEL_MAP_TOP_REAR_LEFT = 20
SF_CHANNEL_MAP_TOP_REAR_RIGHT = 21
SF_CHANNEL_MAP_TOP_REAR_CENTER = 22
SF_CHANNEL_MAP_AMBISONIC_B_W = 23
SF_CHANNEL_MAP_AMBISONIC_B_X = 24
SF_CHANNEL_MAP_AMBISONIC_B_Y = 25
SF_CHANNEL_MAP_AMBISONIC_B_Z = 26
SF_CHANNEL_MAP_MAX = 27
SFD_DEFAULT_LEVEL = 0
SFD_CUSTOM_LEVEL = 0x40000000
SFD_NO_DITHER = 500
SFD_WHITE = 501
SFD_TRIANGULAR_PDF = 502
SF_LOOP_NONE = 800
SF_LOOP_FORWARD = 801
SF_LOOP_BACKWARD = 802
SF_LOOP_ALTERNATING = 803


# typedefs
size_t = c_ulong
c_short_p = POINTER(c_short)
c_int_p = POINTER(c_int)
c_float_p = POINTER(c_float)
c_double_p = POINTER(c_double)
SNDFILE_p = c_void_p
sf_count_t = c_longlong
sf_vio_get_filelen = CFUNCTYPE(sf_count_t, c_void_p)
sf_vio_seek = CFUNCTYPE(sf_count_t, sf_count_t, c_int, c_void_p)
sf_vio_read = CFUNCTYPE(sf_count_t, c_void_p, sf_count_t, c_void_p)
sf_vio_write = CFUNCTYPE(sf_count_t, c_void_p, sf_count_t, c_void_p)
sf_vio_tell = CFUNCTYPE(sf_count_t, c_void_p)


# structs
class SF_INFO(Structure):
    _fields_ = [
        ('frames', sf_count_t),
        ('samplerate', c_int),
        ('channels', c_int),
        ('format', c_int),
        ('sections', c_int),
        ('seekable', c_int),
    ]
SF_INFO_p = POINTER(SF_INFO)

class SF_FORMAT_INFO(Structure):
    _fields_ = [
        ('format', c_int),
        ('name', c_char_p),
        ('extension', c_char_p),
    ]
SF_FORMAT_INFO_p = POINTER(SF_FORMAT_INFO)

class SF_DITHER_INFO(Structure):
    _fields_ = [
        ('type', c_int),
        ('level', c_double),
        ('name', c_char_p),
    ]
SF_DITHER_INFO_p = POINTER(SF_DITHER_INFO)

class SF_EMBED_FILE_INFO(Structure):
    _fields_ = [
        ('offset', sf_count_t),
        ('length', sf_count_t),
    ]
SF_EMBED_FILE_INFO_p = POINTER(SF_EMBED_FILE_INFO)

class _loop(Structure):
    _fields_ = [
        ('mode', c_int),
        ('start', c_uint),
        ('end', c_uint),
        ('count', c_uint),
    ]

class SF_INSTRUMENT(Structure):
    _fields_ = [
        ('gain', c_int),
        ('basenote', c_char),
        ('detune', c_char),
        ('velocity_lo', c_char),
        ('velocity_hi', c_char),
        ('key_lo', c_char),
        ('key_hi', c_char),
        ('loop_count', c_int),
        ('loops', _loop * 16),
    ]
SF_INSTRUMENT_p = POINTER(SF_INSTRUMENT)

class SF_LOOP_INFO(Structure):
    _fields_ = [
        ('time_sig_num', c_short),
        ('time_sig_den', c_short),
        ('loop_mode', c_int),
        ('num_beats', c_int),
        ('bpm', c_float),
        ('root_key', c_int),
        ('future', c_int * 6),
    ]
SF_LOOP_INFO_p = POINTER(SF_LOOP_INFO)

def SF_BROADCAST_INFO_VAR(coding_hist_size):
    class SF_BROADCAST_INFO_VAR(Structure):
        _fields_ = [
            ('description', c_char * 256),
            ('originator', c_char * 32),
            ('originator_reference', c_char * 32),
            ('originator_date', c_char * 10),
            ('originator_time', c_char * 8),
            ('time_reference_low', c_uint),
            ('time_reference_high', c_uint),
            ('version', c_short),
            ('umid', c_char * 64),
            ('reserved', c_char * 190),
            ('coding_history_size', c_uint),
            ('coding_history',  c_char * coding_hist_size),
        ]
    return SF_BROADCAST_INFO_VAR

class SF_VIRTUAL_IO(Structure):
    _fields_ = [
        ('get_filelen', sf_vio_get_filelen),
        ('seek', sf_vio_seek),
        ('read', sf_vio_read),
        ('write', sf_vio_write),
        ('tell', sf_vio_tell),
    ]
SF_VIRTUAL_IO_p = POINTER(SF_VIRTUAL_IO)


# functions
sf_open = libsndfile.sf_open
sf_open.argtypes = [c_char_p, c_int, SF_INFO_p]
sf_open.restype = SNDFILE_p

sf_open_fd = libsndfile.sf_open_fd
sf_open_fd.argtypes = [c_int, c_int, SF_INFO_p, c_int]
sf_open_fd.restype = SNDFILE_p

sf_open_virtual = libsndfile.sf_open_virtual
sf_open_virtual.argtypes = [SF_VIRTUAL_IO_p, c_int, SF_INFO_p, c_void_p]
sf_open_virtual.restype = SNDFILE_p

sf_error = libsndfile.sf_error
sf_error.argtypes = [SNDFILE_p]
sf_error.restype = c_int

sf_strerror = libsndfile.sf_strerror
sf_strerror.argtypes = [SNDFILE_p]
sf_strerror.restype = c_char_p

sf_error_number = libsndfile.sf_error_number
sf_error_number.argtypes = [c_int]
sf_error_number.restype = c_char_p

sf_perror = libsndfile.sf_perror
sf_perror.argtypes = [SNDFILE_p]
sf_perror.restype = c_int

sf_error_str = libsndfile.sf_error_str
sf_error_str.argtypes = [SNDFILE_p, c_char_p, size_t]
sf_error_str.restype = c_int

sf_command = libsndfile.sf_command
sf_command.argtypes = [SNDFILE_p, c_int, c_void_p, c_int]
sf_command.restype = c_int

sf_format_check = libsndfile.sf_format_check
sf_format_check.argtypes = [SF_INFO_p]
sf_format_check.restype = c_int

sf_seek = libsndfile.sf_seek
sf_seek.argtypes = [SNDFILE_p, sf_count_t, c_int]
sf_seek.restype = sf_count_t

sf_set_string = libsndfile.sf_set_string
sf_set_string.argtypes = [SNDFILE_p, c_int, c_char_p]
sf_set_string.restype = c_int

sf_get_string = libsndfile.sf_get_string
sf_get_string.argtypes = [SNDFILE_p, c_int]
sf_get_string.restype = c_char_p

sf_version_string = libsndfile.sf_version_string
sf_version_string.argtypes = []
sf_version_string.restype = c_char_p

sf_read_raw = libsndfile.sf_read_raw
sf_read_raw.argtypes = [SNDFILE_p, c_void_p, sf_count_t]
sf_read_raw.restype = sf_count_t

sf_write_raw = libsndfile.sf_write_raw
sf_write_raw.argtypes = [SNDFILE_p, c_void_p, sf_count_t]
sf_write_raw.restype = sf_count_t

sf_readf_short = libsndfile.sf_readf_short
sf_readf_short.argtypes = [SNDFILE_p, c_short_p, sf_count_t]
sf_readf_short.restype = sf_count_t

sf_writef_short = libsndfile.sf_writef_short
sf_writef_short.argtypes = [SNDFILE_p, c_short_p, sf_count_t]
sf_writef_short.restype = sf_count_t

sf_readf_int = libsndfile.sf_readf_int
sf_readf_int.argtypes = [SNDFILE_p, c_int_p, sf_count_t]
sf_readf_int.restype = sf_count_t

sf_writef_int = libsndfile.sf_writef_int
sf_writef_int.argtypes = [SNDFILE_p, c_int_p, sf_count_t]
sf_writef_int.restype = sf_count_t

sf_readf_float = libsndfile.sf_readf_float
sf_readf_float.argtypes = [SNDFILE_p, c_float_p, sf_count_t]
sf_readf_float.restype = sf_count_t

sf_writef_float = libsndfile.sf_writef_float
sf_writef_float.argtypes = [SNDFILE_p, c_float_p, sf_count_t]
sf_writef_float.restype = sf_count_t

sf_readf_double = libsndfile.sf_readf_double
sf_readf_double.argtypes = [SNDFILE_p, c_double_p, sf_count_t]
sf_readf_double.restype = sf_count_t

sf_writef_double = libsndfile.sf_writef_double
sf_writef_double.argtypes = [SNDFILE_p, c_double_p, sf_count_t]
sf_writef_double.restype = sf_count_t

sf_read_short = libsndfile.sf_read_short
sf_read_short.argtypes = [SNDFILE_p, c_short_p, sf_count_t]
sf_read_short.restype = sf_count_t

sf_write_short = libsndfile.sf_write_short
sf_write_short.argtypes = [SNDFILE_p, c_short_p, sf_count_t]
sf_write_short.restype = sf_count_t

sf_read_int = libsndfile.sf_read_int
sf_read_int.argtypes = [SNDFILE_p, c_int_p, sf_count_t]
sf_read_int.restype = sf_count_t

sf_write_int = libsndfile.sf_write_int
sf_write_int.argtypes = [SNDFILE_p, c_int_p, sf_count_t]
sf_write_int.restype = sf_count_t

sf_read_float = libsndfile.sf_read_float
sf_read_float.argtypes = [SNDFILE_p, c_float_p, sf_count_t]
sf_read_float.restype = sf_count_t

sf_write_float = libsndfile.sf_write_float
sf_write_float.argtypes = [SNDFILE_p, c_float_p, sf_count_t]
sf_write_float.restype = sf_count_t

sf_read_double = libsndfile.sf_read_double
sf_read_double.argtypes = [SNDFILE_p, c_double_p, sf_count_t]
sf_read_double.restype = sf_count_t

sf_write_double = libsndfile.sf_write_double
sf_write_double.argtypes = [SNDFILE_p, c_double_p, sf_count_t]
sf_write_double.restype = sf_count_t

sf_close = libsndfile.sf_close
sf_close.argtypes = [SNDFILE_p]
sf_close.restype = c_int

sf_write_sync = libsndfile.sf_write_sync
sf_write_sync.argtypes = [SNDFILE_p]
sf_write_sync.restype = None
