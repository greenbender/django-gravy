import logging

log = logging.getLogger('gravy.db.models')

class CurrentUserFieldRegistry(object):
    _registry = {}

    def add_field(self, model, field):
        reg = self.__class__._registry.setdefault(model, [])
        reg.append(field)

    def get_fields(self, model):
        fields = []
        for m, f in self.__class__._registry.items():
            if issubclass(model, m):
                fields.extend(f)
        return fields

    def __contains__(self, model):
        return issubclass(model, tuple(self.__class__._registry.keys()))
