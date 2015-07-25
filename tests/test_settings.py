import pytest
# we aim to test using only the public API
import reconf
from reconf.settings import NoOptionError


def test_python_dict():
    config = reconf.Config()
    config.add_resource(__name__, 'dict.conf')
    settings = config.settings(reconf.PythonDict('python-dict:valid'))
    assert settings.valid == {'key': 1}


def test_invalid_python_dict():
    config = reconf.Config()
    config.add_resource(__name__, 'dict.conf')
    settings = config.settings(reconf.PythonDict('python-dict:invalid'))
    with pytest.raises(ValueError):
        assert settings.invalid == {'key': 1}


def test_not_set():
    config = reconf.Config()
    config.add_resource(__name__, 'ex1.conf')
    settings = config.settings(reconf.Integer('mysection:not_set'))
    with pytest.raises(NoOptionError):
        settings.not_set


def test_func():
    config = reconf.Config()
    config.add_resource(__name__, 'ex1.conf')
    settings = config.settings(
        reconf.Integer('mysection:i'),
        reconf.Integer('mysection:func', func=lambda s: s.i + 1)
    )
    assert settings.func == 4
