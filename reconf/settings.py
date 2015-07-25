import os
import argparse
import errno
import json
from ast import literal_eval
from six import PY2
from .location import ArgsLocation
from six.moves.configparser import NoOptionError, NoSectionError

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO  # flake8: noqa


class Settings(object):

    @classmethod
    def subclass(cls, *settings, **kw):
        subclass_dict = {setting.name: setting for setting in settings}
        subclass_dict.update(kw)
        subclass = type(cls.__name__, (cls,), subclass_dict)
        return subclass

    def argument_parser(self):
        parser = argparse.ArgumentParser()
        args = ArgsLocation()
        self._config.add_location(args)
        for value in self.__class__.__dict__.values():
            if isinstance(value, Setting):
                value.add_argument(parser, args)
        return parser


class Setting(object):

    def __init__(self, option, **kw):
        self.func = kw.pop('func', None)
        self.section = kw.pop('section', None)
        if self.section is None:
            self.section, _, self.option = option.partition(':')
        else:
            self.option = option
        self.name = kw.pop('name', self.option)
        if kw:
            raise ValueError("unexpected keyword args '%s'" % kw.keys())

    def __get__(self, settings, objtype):

        if settings is None:
            return self

        cache = settings.__dict__

        try:
            return cache[self]
        except KeyError:
            pass

        config_parser = settings._config.config_parser()
        try:
            value = self.get(settings, config_parser)
        except (NoOptionError, NoSectionError):
            if self.func is None:
                raise
            value = self.func(settings)
        cache[self] = value

        return value

    def get(self, settings, config):
        return config.get(self.section, self.option)

    def add_argument(self, parser, args):

        class Action(argparse.Action):
            # note: have used `action` instead of `self` here to avoid shadowing
            def __call__(action, parser, namespace, values, option_string=None):
                section = args.sections.setdefault(self.section, {})
                section[self.option] = values
                setattr(namespace, action.dest, values)

        parser.add_argument('--{0.section}:{0.option}'.format(self), action=Action)


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


class File(Setting):
    """ A setting that is a file. """

    def __init__(self, name, **kwargs):
        self.required = kwargs.pop('required', False)
        self.mode = kwargs.pop('mode', 'r')
        self.expanduser = kwargs.pop('expanduser', True)
        super(File, self).__init__(name, **kwargs)

    def get(self, settings, config):
        filespec = config.get(self.section, self.option)
        if self.expanduser:
            filespec = os.path.expanduser(filespec)
        return filespec


class Boolean(Setting):
    """ A setting that is a boolean value. """

    def get(self, settings, config):
        return config.getboolean(self.section, self.option)


class Float(Setting):
    """ A setting that is a floating point number. """

    def get(self, settings, config):
        return config.getfloat(self.section, self.option)


class Integer(Setting):
    """ A setting that is an integer. """

    def get(self, settings, config):
        return config.getint(self.section, self.option)


class Literal(Setting):

    type_check = lambda i: i
    evaluate = staticmethod(literal_eval)

    def __init__(self, name, **kwargs):
        self.type_check = kwargs.pop('type_check', self.type_check)
        super(Literal, self).__init__(name, **kwargs)

    def get(self, settings, config):
        text = config.get(self.section, self.option)
        try:
            value = self.evaluate(text)
        except ValueError:
            raise ValueError("'%s' is not a valid %s literal" % 
                             (text, self.__class__.__name__))
        return self.type_check(value)


class JSON(Literal):

    evaluate = staticmethod(json.loads)


class JSONArray(JSON):

    type_check = list


class JSONDict(JSON):

    type_check = dict


class Python(Literal):
    """ Alias. """

class PythonDict(Python):
    type_check = dict


class PythonList(Python):
    type_check = list


class PythonTuple(Python):
    type_check = tuple


__all__ = [
    "Boolean",
    "DelimitedList",
    "Directory",
    "File",
    "Float",
    "Integer",
    "JSON",
    "JSONArray",
    "JSONDict",
    "Python",
    "PythonDict",
    "PythonList",
    "PythonTuple",
    "Text",
]
