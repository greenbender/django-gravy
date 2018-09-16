from django.core.files.storage import FileSystemStorage
import hashlib
import base64


__all__ = ['HashedFileSystemStorage', 'B64HashedFileSystemStorage',]


class HashedFileSystemStorage(FileSystemStorage):
    """
    Use the hexdigest of the hashed file content as the filename. If the
    filename already exists assume it has the same content and don't bother
    writing it to disk.
    """
    algorithm = 'sha1'

    def __init__(self, algorithm=None, *args, **kwargs):
        if algorithm is not None:
            self.algorithm = algorithm
        super(HashedFileSystemStorage, self).__init__(*args, **kwargs)

    def get_available_name(self, name, max_length=None):
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
    """
    Use the base64 encoded digest of the hashed file content as the filename.
    The base64 padding characters are removed from the filename.
    """

    def hash_to_name(self, hash):
        return base64.b64encode(hash.digest()).rstrip('=')
