from django.core.files.storage import FileSystemStorage
import hashlib
import base64


# XXX: should we be a proxy module for django.core.files.storage?
__all__ = ['HashedFileSystemStorage', 'B64HashedFileSystemStorage',]


class HashedFileSystemStorage(FileSystemStorage):
    algorithm = 'sha1'

    def __init__(self, *args, **kwargs):
        a = kwargs.pop('algorithm', None)
        if a is not None:
            self.algorithm = a
        super(HashedFileSystemStorage, self).__init__(*args, **kwargs)

    def get_available_name(self, name):
        return name

    def hash_to_name(self, hash):
        return hash.hexdigest()

    def _save(self, name, content):
        h = hashlib.new(self.algorithm)
        for chunk in content.chunks():
            h.update(chunk)
        name = self.hash_to_name(h)
        if self.exists(name):
            return name
        return super(HashedFileSystemStorage, self)._save(name, content)


class B64HashedFileSystemStorage(HashedFileSystemStorage):
    def hash_to_name(self, hash):
        return base64.b64encode(hash.digest()).rstrip('=')
