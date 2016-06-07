from _binding import *


class SndFileError(Exception):
    pass


class VirtualIO(SF_VIRTUAL_IO):
    def __init__(self, fd):

        # references
        self._fd = fd
        self._c_char = c_char
        self._string_at = string_at

        def get_filelen(userdata):
            where = self._fd.tell()
            self._fd.seek(0, SEEK_END)
            length = self._fd.tell()
            self._fd.seek(where, SEEK_SET)
            return length

        def seek(count, whence, userdata):
            self._fd.seek(count, whence)
            return self._fd.tell()

        def read(data, count, userdata):
            dst = (self._c_char * count).from_address(data)
            buf = self._fd.read(count)
            length = len(buf)
            dst[:length] = buf
            return length

        def write(data, count, userdata):
            self._fd.write(self._string_at(data, count))
            return count

        def tell(userdata):
            return self._fd.tell()

        return super(VirtualIO, self).__init__(
            get_filelen=sf_vio_get_filelen(get_filelen),
            seek=sf_vio_seek(seek),
            read=sf_vio_read(read),
            write=sf_vio_write(write),
            tell=sf_vio_tell(tell)
        )
    

class SndFile(object):
    default_frames = 1024

    def __init__(self, obj, mode='r', major=None, subtype=None, samplerate=None, channels=None):
        self._sndfile = None

        # references
        self._obj = obj
        self._sf_close = sf_close

        # create sfinfo
        self._sfinfo = SF_INFO()
        if samplerate:
            self._sfinfo.samplerate = samplerate
        if channels:
            self._sfinfo.channels = channels
        if major:
            self._sfinfo.format = self._parse_format(major, subtype)

        # open sndfile
        mode = self._parse_mode(mode)
        if isinstance(self._obj, basestring):
            self._sndfile = sf_open(self._obj, mode, byref(self._sfinfo))
        elif hasattr(self._obj, 'fileno'):
            self._sndfile = sf_open_fd(self._obj.fileno(), mode, byref(self._sfinfo), 0)
        else:
            self._vio = VirtualIO(self._obj)
            self._sndfile = sf_open_virtual(byref(self._vio), mode, byref(self._sfinfo), None)
        if self._sndfile is None:
            raise SndFileError(sf_strerror(self._sndfile))

    def __getattr__(self, name):
        return getattr(self._sfinfo, name)

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    @staticmethod
    def _parse_format(major, subtype=None):
        fmt = 0
        if major == 'WAV':
            fmt |= SF_FORMAT_WAV
            subtype = subtype or 'PCM_32'
        elif major == 'OGG':
            fmt |= SF_FORMAT_OGG
            subtype = subtype or 'VORBIS'
        if subtype == 'PCM_32':
            fmt |= SF_FORMAT_PCM_32
        elif subtype == 'GSM610':
            fmt |= SF_FORMAT_GSM610
        elif subtype == 'VORBIS':
            fmt |= SF_FORMAT_VORBIS
        return fmt

    @staticmethod
    def _parse_mode(mode):
        if mode == 'r':
            return SFM_READ
        if mode == 'r+':
            return SFM_RDWR
        if mode == 'w':
            return SFM_WRITE
        if mode == 'w+':
            return SFM_WRITE
        raise ValueError('Bad mode %s' % mode)

    def _get_remaining_frames(self):
        return self._sfinfo.frames - sf_seek(self._sndfile, 0, SEEK_CUR)

    def _get_frame_buffer(self, frames=None):
        frames = frames or self.default_frames
        count = self._sfinfo.channels * frames
        if not hasattr(self, '_buf') or len(self._buf) < count:
            self._buf = (c_int * count)()
        return self._buf

    def _get_item_buffer(self, count):
        if not hasattr(self, '_buf') or len(self._buf) < count:
            self._buf = (c_int * count)()
        return self._buf

    def read(self, frames=None):
        frames = frames or self._get_remaining_frames()
        buf = self._get_frame_buffer(frames)
        count = sf_read_int(self._sndfile, buf, len(buf))
        return buf[:count]

    def write(self, items):
        count = len(items)
        buf = self._get_item_buffer(count)
        buf[:count] = items
        count = sf_write_int(self._sndfile, buf, count)
        return count

    def next(self):
        items = self.read(self.default_frames)
        if not items:
            raise StopIteration
        return items

    def close(self):
        if self._sndfile:
            self._sf_close(self._sndfile)
            self._sndfile = None
