from django.core.cache import cache as _cache


class CachedProperty(property):
    """
    Decorator much like django cached_property however it also caches to a
    'real' cache and exposes some additional functionality for setting/deleting
    the cache value along with the ability to perform additional actions when
    the cache value is set or deleted
    """
    # use the default django cache
    cache = _cache

    # use str on the object (this should be overridden)
    key_fmt = '{object}'

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        key = self.key_fmt.format(object=obj)
        value = self.cache.get(key)
        if value is not None:
            return value
        value = super(CachedProperty, self).__get__(obj, objtype)
        self.cache.set(key, value)
        return value

    def __set__(self, obj, value):
        key = self.key_fmt.format(object=obj)
        self.cache.set(key, value)
        if self.fset is not None:
            super(CachedProperty, self).__set__(obj, value)

    def __delete__(self, obj):
        key = self.key_fmt.format(object=obj)
        self.cache.delete(key)
        if self.fdel is not None:
            super(CachedProperty, self).__delete__(obj)

    on_set = property.setter

    on_del = property.deleter


class CachedClassProperty(CachedProperty):
    """
    Same as CachedProperty decorator but acts as a class proprty rather than an
    instance property. 
    """
    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        return super(CachedClassProperty, self).__get__(objtype)

    def __set__(self, obj):
        super(CachedClassProperty, self).__set__(type(obj))

    def __delete__(self, obj):
        super(CachedClassProperty, self).__delete__(type(obj))


def real_cached_property(key_fmt, cache=None):
    """
    Return a CachedProperty decorator that utilises the suppiled key_fmt and
    cache.
    """
    class RealCachedProperty(CachedProperty):
        def __init__(self, *args, **kwargs):
            super(RealCachedProperty, self).__init__(*args, **kwargs)
            self.key_fmt = key_fmt
            if cache is not None:
                self.cache = cache

    return RealCachedProperty


def real_cached_classproperty(key_fmt, cache=None):
    """
    Return a CachedClassProperty decorator that utilises the suppiled key_fmt
    and cache.
    """
    class RealCachedClassProperty(CachedClassProperty):
        def __init__(self, *args, **kwargs):
            super(RealCachedClassProperty, self).__init__(*args, **kwargs)
            self.key_fmt = key_fmt
            if cache is not None:
                self.cache = cache

    return RealCachedClassProperty

