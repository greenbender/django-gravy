from django.utils import six
from PIL import Image
from PIL.ExifTags import TAGS
from pytesseract import image_to_string


__all__ = ['dump', 'load', 'ocr', 'exif', 'reorient', 'thumbnail']


import logging
log = logging.getLogger('gravy.images')


def dump(img, fd, **kwargs):
    img.save(fd, **kwargs)


def load(fd):
    return Image.open(fd)


def ocr(img):
    return image_to_string(
        img.resize(tuple(2*d for d in img.size), Image.NEAREST)
    )


def exif(img):
    data = {}
    info = img._getexif()
    if info is None:
        return data
    for tag, value in six.iteritems(info):
        name = TAGS.get(tag, tag)
        if name in ('UserComment',):
            encoding = value[:8]
            value = value[8:]
        data[name] = value
    return data


def reorient(img):
    rotate = exif(img).get('Orientation', 1)
    if rotate == 3:
        return img.rotate(-180)
    elif rotate == 6:
        return img.rotate(-90)
    elif rotate == 8:
        return img.rotate(-270)
    return img


def thumbnail(img, width=300, height=300):
    i = img.copy()
    i.thumbnail((width, height), Image.ANTIALIAS)
    return i
