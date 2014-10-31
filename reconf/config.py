import tempfile
from operator import attrgetter
from ConfigParser import SafeConfigParser
from reconf.settings import Settings
from reconf.location import (ResourceLocation,
                             FileLocation,
                             EnvironLocation,
                             TestResourceLocation,
                             TestStringLocation)


sort_key = attrgetter('order')


class Config(object):

    def __init__(self):
        self.locations = []
        self.cache = {}
        self.defaults = {'tempdir': tempfile.gettempdir()}

    def add_location(self, location):
        if location in self.locations:
            return
        self.locations.append(location)
        self.locations.sort(key=sort_key)

    def add_resource(self, package, resource):
        self.add_location(ResourceLocation(package, resource))

    def add_file(self, path):
        self.add_location(FileLocation(path))

    def add_environ(self, name):
        self.add_location(EnvironLocation(name))

    def add_test_resource(self, package, resource):
        self.add_location(TestResourceLocation(package, resource))

    def add_test_string(self, string):
        self.add_location(TestStringLocation(string))

    def remove_location(self, location):
        self.locations.remove(location)

    def load(self):
        cache = self.cache
        cache_key = tuple(self.locations)
        if cache_key in cache:
            return cache[cache_key]
        cache.clear()
        config = SafeConfigParser(defaults=self.defaults)

        names = []
        for location in self.locations:
            for fp, name in location.files():
                config.readfp(fp, name)
                names.append(name)

        cache[cache_key] = config
        return config

    def settings(self, *settings, **kwargs):
        return Settings.subclass(*settings, **kwargs)(self)
