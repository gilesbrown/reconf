import pytest
# we aim to test using only the public API
import reconf


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
