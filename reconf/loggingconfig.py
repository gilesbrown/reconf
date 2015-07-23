from ast import literal_eval
from ConfigParser import NoSectionError

logging_section = 'logging'
root_section = 'logging.root'


def create_logging_config_dict(cp):

    config_dict = {
        'formatters': create_formatters(cp),
        'filters': create_filters(cp),
        'handlers': create_handlers(cp),
        'loggers': create_loggers(cp),
    }

    for option in options(cp, logging_section):
        if option == 'version':
            config_dict[option] = cp.getint(logging_section, option)
        elif option in ('incremental', 'disable_existing_loggers'):
            config_dict[option] = cp.getboolean(logging_section, option)
        else:
            config_dict[option] = cp.get(logging_section, option)

    if cp.has_section(root_section):
        config_dict['root'] = logger_dict_from_section(cp, root_section)

    if 'version' not in config_dict:
        config_dict['version'] = 1

    return config_dict


def sections_with_prefix(prefix, cp):
    for section in cp.sections():
        if section.startswith(prefix):
            yield section, section[len(prefix):]


def create_formatters(cp):
    formatters = {}
    defaults = {'datefmt': None}
    prefix = 'logging.formatter:'
    for section, formatter_id in sections_with_prefix(prefix, cp):
        formatters[formatter_id] = {
            'format': cp.get(section, 'format', 1, defaults),
            'datefmt': cp.get(section, 'datefmt', 1, defaults),
        }
    return formatters


def create_filters(cp):
    return {}


def create_handlers(cp):
    handlers = {}
    prefix = 'logging.handler:'
    for section, handler_id in sections_with_prefix(prefix, cp):
        handler = handlers[handler_id] = {}
        for option in options(cp, section):
            value = cp.get(section, option)
            if option == 'filters':
                handler[option] = id_list(value)
            elif option in ('class', 'level', 'formatter'):
                handler[option] = value
            else:
                try:
                    handler[option] = literal_eval(value)
                except (SyntaxError, ValueError):
                    handler[option] = value

    return handlers


def create_loggers(cp):
    loggers = {}
    prefix = 'logging.logger:'
    for section, logger_id in sections_with_prefix(prefix, cp):
        loggers[logger_id] = logger_dict_from_section(cp, section)
    return loggers


def logger_dict_from_section(cp, section):
    logger_dict = {}
    for option in options(cp, section):
        if option in ('filters', 'handlers'):
            logger_dict[option] = id_list(cp.get(section, option))
        elif option == 'propagate':
            logger_dict[option] = cp.getboolean(section, option)
        else:
            logger_dict[option] = cp.get(section, option)
    return logger_dict


def options(cp, section):
    """ Get options from section without including defaults. """
    try:
        return [k for k in cp._sections[section].keys() if k != '__name__']
    except KeyError:
        raise NoSectionError(section)


def id_list(value):
    return [s.strip() for s in value.split(',')]
