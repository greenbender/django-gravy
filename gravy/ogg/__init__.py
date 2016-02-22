from _binding import *


__all__ = ['OggError', 'OggPacket', 'OggPage', 'OggStream']


class OggError(Exception):
    pass


class OggPacket(object):

    def __init__(self, packet=None, *args, **kwargs):
        self.c_type = ogg_packet(*args, **kwargs)
        if packet is not None:
            self.packet = packet

    @property
    def packet(self):
        return string_at(self.c_type.packet, self.c_type.bytes)

    @packet.setter
    def packet(self, value):
        self.c_type.packet = cast(c_char_p(value), c_uchar_p)
        self.c_type.bytes = len(value)


class OggPage(object):

    def __init__(self, *args, **kwargs):
        self.c_type = ogg_page(*args, **kwargs)

    def __str__(self):
        return ''.join([
            string_at(self.c_type.header, self.c_type.header_len),
            string_at(self.c_type.body, self.c_type.body_len)
        ])


class OggStream(object):

    def __init__(self, serialno, *args, **kwargs):
        self.c_type = ogg_stream_state(*args, **kwargs)
        result = ogg_stream_init(byref(self.c_type), serialno)
        if result:
            raise OggError('ogg_stream_init')

    def __del__(self):
        result = ogg_stream_destroy(byref(self.c_type))
        if result:
            raise OggError('ogg_stream_destroy')

    def clear(self):
        result = ogg_stream_clear(byref(self.c_type))
        if result:
            raise OggError('ogg_stream_clear')

    def reset(self):
        result = ogg_stream_reset(byref(self.c_type))
        if result:
            raise OggError('ogg_stream_reset')

    def packetin(self, packet):
        result = ogg_stream_packetin(byref(self.c_type), byref(packet.c_type))
        if result:
            raise OggError('ogg_stream_packetin')

    def pageout(self):
        page = OggPage()
        result = ogg_stream_pageout(byref(self.c_type), byref(page.c_type))
        if result == 1:
            return page
        return None

    def flush(self):
        page = OggPage()
        result = ogg_stream_flush(byref(self.c_type), byref(page.c_type))
        if result == 1:
            return page
        return None
