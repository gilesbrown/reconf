import os
import re
import errno
from operator import methodcaller
from six import PY2
from six.moves import filter

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO


class Settings(object):


    def __init__(self, config):
        self.__config__ = config

    @classmethod
    def subclass(cls, *settings, **kw):
        subclass_dict = {setting.name: setting for setting in settings}
        subclass_dict.update(kw)
        subclass = type(cls.__name__, (cls,), subclass_dict)
        return subclass


class Setting(object):

    def __init__(self, option, **kw):
        self.section = kw.pop('section', None)
        if self.section is None:
            self.section, _, self.option = option.partition(':')
        else:
            self.option = option
        self.name = kw.pop('name', self.option)
        if kw:
            raise ValueError("unexpected keyword args '%s'" % kw.keys())

    def __get__(self, obj, objtype):

        if objtype is None:
            return obj

        config = obj.__config__.load()
        cache = config.__dict__.setdefault('__settings_cache__', {})
        if self in cache:
            return cache[self]

        value = self.get(obj, config)
        cache[self] = value
        return value

    def get(self, settings, config):
        return config.get(self.section, self.option)


class Text(Setting):
    """ A setting that is text. """


class DelimitedList(Setting):
    """ A list of items from a single option. """

    def __init__(self, name, **kwargs):
        super(DelimitedList, self).__init__(name)
        self.delimiter = kwargs.pop('delimiter', '\n')
        self.value_type = kwargs.pop('value_type', None)

    def get(self, settings, config):
        text = config.get(self.section, self.option)
        return list(map(self.value_type, text.split(self.delimiter)))


class Directory(Setting):
    """ A setting that is a directory. """

    def __init__(self, name, **kwargs):
        self.makedirs = kwargs.pop('makedirs', False)
        self.expanduser = kwargs.pop('expanduser', True)
        super(Directory, self).__init__(name, **kwargs)

    def get(self, settings, config):
        dirpath = config.get(self.section, self.option)
        if self.expanduser:
            dirpath = os.path.expanduser(dirpath)
        try:
            if self.makedirs:
                os.makedirs(dirpath)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
        return dirpath


class Float(Setting):
    """ A setting that is a floating point number. """

    def get(self, settings, config):
        return config.getfloat(self.section, self.option)


class Integer(Setting):
    """ A setting that is an integer. """

    def get(self, settings, config):
        return config.getint(self.section, self.option)


class Collection(Setting):
    """ Multiple configuration lines combined into one setting. """

    def __init__(self, *settings, **kwargs):
        self.separator = kwargs.pop('separator', '-_')
        self.value_type = kwargs.pop('value_type', None)
        super(Collection, self).__init__(*settings, **kwargs)

    def iteritems(self, config):
        for option, value in config.items(self.section):
            pat = '{0}[{1}](.*)$'.format(self.option, self.separator)
            match = re.match(pat, option)
            if not match:
                continue
            if self.value_type is not None:
                value = self.value_type(value)
            yield match.group(1), value


class List(Collection):
    """ A `Collection` setting that is an list of values.  """

    def get(self, settings, config):
        digit_items = (item for item in self.iteritems(config) if item[0].isdigit())
        sorted_items = sorted(digit_items, key=lambda item: int(item[0]))
        return list(item[1] for item in sorted_items)


class Dict(Collection):
    """ A `Collection` setting that is an dictionary of values.  """

    def get(self, settings, config):
        return dict(self.iteritems(config))


__all__ = [
    "Text",
    "DelimitedList",
    "Directory",
    "Float",
    "Integer",
    "List",
    "Dict",
]
