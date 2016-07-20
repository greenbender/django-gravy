from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from Crypto.Cipher import DES
from Crypto.Hash import MD5
import struct


__all__ = ['EncryptedPKModel']


import logging
log = logging.getLogger('gravy.db.models.crypto')


def base36encode(number):
    number = int(number)
    alphabet, base36 = '0123456789abcdefghijklmnopqrstuvwxyz', []
    while number:
        number, i = divmod(number, 36)
        base36.insert(0, alphabet[i])
    return ''.join(base36) or alphabet[0]


def base36decode(numstr):
    return int(numstr, 36)


def encrypted_pk_to_pk(f):
    """Decorator for updating encrypted_pk kwarg to pk kwarg.
    
    Modified From: https://gist.github.com/treyhunner/735861
    License: MIT
    """
    def wrapper(self, *args, **kwargs):
        encrypted_pk = kwargs.pop('encrypted_pk', None)
        if encrypted_pk:
            kwargs['pk'] = struct.unpack('<Q', self.model.encryption_obj.decrypt(
                struct.pack('<Q', base36decode(encrypted_pk))
            ))[0]
        return f(self, *args, **kwargs)
    return wrapper
        
    
class EncryptedPKQuerySet(models.QuerySet):
    """Allows models to be identified based on their encrypted_pk value.
    
    Modified From: https://gist.github.com/treyhunner/735861
    License: MIT
    """

    @encrypted_pk_to_pk
    def filter(self, *args, **kwargs):
        return super(EncryptedPKQuerySet, self).filter(*args, **kwargs)

    @encrypted_pk_to_pk
    def exclude(self, *args, **kwargs):
        return super(EncryptedPKQuerySet, self).exclude(*args, **kwargs)


class EncryptedPKModel(models.Model):
    """Adds encrypted_pk property to children which returns the encrypted value
    of the primary key.

    Modified From: https://gist.github.com/treyhunner/735861
    License: MIT
    """
    objects = EncryptedPKQuerySet.as_manager()
    encryption_obj = DES.new(MD5.new(settings.SECRET_KEY).digest()[:8])

    def __init__(self, *args, **kwargs):
        super(EncryptedPKModel, self).__init__(*args, **kwargs)
        setattr(
            self.__class__,
            "encrypted_%s" % (self._meta.pk.name,),
            cached_property(self.__class__._encrypted_pk)
        )

    def _encrypted_pk(self):
        return base36encode(struct.unpack('<Q', self.encryption_obj.encrypt(
            str(struct.pack('<Q', self.pk))
        ))[0])

    encrypted_pk = cached_property(_encrypted_pk)

    class Meta:
        abstract = True
