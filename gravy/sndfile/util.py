from _binding import *


def print_simple_formats():
    count = c_int()
    finfo = SF_FORMAT_INFO()
    sf_command(None, SFC_GET_SIMPLE_FORMAT_COUNT, byref(count), sizeof(count))
    for i in range(count.value):
        finfo.format = i
        sf_command(None, SFC_GET_SIMPLE_FORMAT, byref(finfo), sizeof(finfo))
        print "%08x  %s %s" % (finfo.format, finfo.name, finfo.extension)


def print_major_formats():
    count = c_int()
    finfo = SF_FORMAT_INFO()
    sf_command(None, SFC_GET_FORMAT_MAJOR_COUNT, byref(count), sizeof(count))
    for i in range(count.value):
        finfo.format = i
        sf_command(None, SFC_GET_FORMAT_MAJOR, byref(finfo), sizeof(finfo))
        print "%08x  %s %s" % (finfo.format, finfo.name, finfo.extension)


def print_subtype_formats():
    count = c_int()
    finfo = SF_FORMAT_INFO()
    sf_command(None, SFC_GET_FORMAT_SUBTYPE_COUNT, byref(count), sizeof(count))
    for i in range(count.value):
        finfo.format = i
        sf_command(None, SFC_GET_FORMAT_SUBTYPE, byref(finfo), sizeof(finfo))
        print "%08x  %s" % (finfo.format, finfo.name)
