import tempfile
import logging.config
from logging import getLogger
from operator import attrgetter
from ConfigParser import SafeConfigParser
from reconf.settings import Settings
from reconf.loggingconfig import create_logging_config_dict
from reconf.location import (ResourceLocation,
                             FileLocation,
                             EnvironLocation,
                             TestResourceLocation,
                             TestStringLocation)


sort_key = attrgetter('order')


class Config(object):

    def __init__(self):
        self.locations = []
        self.settings_instances = []
        self.defaults = {'tempdir': tempfile.gettempdir()}
        self._config_parser = None

    def clear(self):
        self._config_parser = None
        for settings in self.settings_instances:
            settings.__dict__.clear()

    def add_location(self, location):
        try:
            pos = self.locations.index(location)
            return self.locations[pos]
        except ValueError:
            pass
        self.locations.append(location)
        self.locations.sort(key=sort_key)
        self.clear()
        return location

    def add_resource(self, package, resource):
        self.add_location(ResourceLocation(package, resource))

    def add_file(self, path):
        self.add_location(FileLocation(path))

    def add_environ(self, name):
        self.add_location(EnvironLocation(name))

    def add_test_resource(self, package, resource):
        return self.add_location(TestResourceLocation(package, resource))

    def add_test_string(self, string):
        self.add_location(TestStringLocation(string))

    def remove_location(self, location):
        self.locations.remove(location)
        self.clear()

    remove = remove_location

    def config_parser(self):

        if self._config_parser:
            return self._config_parser

        config_parser = SafeConfigParser(defaults=self.defaults)

        names = []
        logger = getLogger(__name__)
        for location in self.locations:
            for fp, name in location.files():
                logger.debug("reading %r (%s)", fp, name)
                config_parser.readfp(fp, name)
                names.append(name)

        self._config_parser = config_parser

        return config_parser

    def settings(self, *settings, **kwargs):
        settings = Settings.subclass(*settings, _config=self, **kwargs)()
        self.settings_instances.append(settings)
        return settings

    def logging_config_dict(self):
        return create_logging_config_dict(self.config_parser())

    def configure_logging(self):
        logging.config.dictConfig(self.logging_config_dict())
