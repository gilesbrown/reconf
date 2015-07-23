import os
import errno
from six import iteritems
from contextlib import contextmanager
from StringIO import StringIO
from pkg_resources import resource_stream


def enum(*names, **kw):
    typename = kw.pop('typename', 'Enum')
    values = [(name, i) for i, name in enumerate(names)]
    typedict = dict(values)
    typedict['FIRST'] = values[0][1]
    typedict['LAST'] = values[-1][1]
    return type(typename, (), typedict)


#
# This is the order in which configuration files are read.

LocationOrder = enum('RESOURCE', 'STANDARD', 'ENVIRON', 'ARGS', 'TEST')


class Location(object):
    """ A location from which we read configuration. """

    order = LocationOrder.STANDARD

    def __init__(self, name):
        self.name = name

    @contextmanager
    def context(self, config):
        """ Context manager for temporarily adding a config `Location`. """
        config.add_location(self)
        try:
            yield self
        finally:
            config.remove_location(self)

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name)

    def __eq__(self, other):
        return (getattr(other, '__class__') is self.__class__ and
                self.name == other.name)

    def files(self):
        for path in self.name.split(os.pathsep):
            try:
                with open(os.path.expanduser(path), 'rb') as fp:
                    yield fp, path
            except IOError as exc:
                if exc.errno != errno.ENOENT:
                    raise


class FileLocation(Location):
    """ An alias for `Location`. """


class ResourceLocation(Location):

    order = LocationOrder.RESOURCE

    def __init__(self, package, resource):
        super(ResourceLocation, self).__init__(os.pathsep.join([package,
                                                                resource]))

    def files(self):
        package, resource = self.name.split(os.pathsep, 1)
        fp = resource_stream(package, resource)
        return [(fp, self.name)]


class EnvironLocation(Location):

    order = LocationOrder.ENVIRON

    def files(self):
        value = os.environ.get(self.name, '')
        for path in value.split(os.pathsep):
            if path.strip() and os.path.exists(path.strip()):
                with open(path, 'rb') as fp:
                    yield fp, path


class ArgsLocation(Location):

    order = LocationOrder.ARGS

    def __init__(self):
        super(ArgsLocation, self).__init__('args')
        self.sections = {}

    def files(self):
        fp = StringIO()
        for section, values in iteritems(self.sections):
            fp.write('[{}]\n'.format(section))
            for item in iteritems(values):
                fp.write('{}={}\n'.format(*item))
        fp.seek(0)
        return [(fp, self.name)]


class TestResourceLocation(ResourceLocation):

    order = LocationOrder.TEST


class TestStringLocation(Location):

    order = LocationOrder.TEST

    def files(self):
        return [(StringIO(self.name), self.name)]


__all__ = [
    'FileLocation',
    'ResourceLocation',
    'EnvironLocation',
    'TestResourceLocation',
]
