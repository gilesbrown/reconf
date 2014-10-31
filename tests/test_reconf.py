import os
from uuid import uuid4
from pkg_resources import resource_filename
import pytest
import reconf

ex1 = resource_filename(__name__, 'ex1.conf')

def build(add_ex1=True):
    config = reconf.Config()
    settings = config.settings(reconf.Integer('i'))
    return config, settings


def test_config():
    c, s = build()
    c.add_resource(__name__, 'ex1.conf')
    assert s.i == 3
    # And this one should come from the cache
    assert s.i == 3


def test_config_add_file():
    c, s = build()
    c.add_file(ex1)
    assert s.i == 3


def test_config_add_file_is_idempotent():
    c, s = build()
    c.add_file(ex1)
    c.add_file(ex1)
    assert len(c.locations) == 1


def test_config_add_environ():
    c, s = build()
    var_name = str(uuid4())
    os.environ[var_name] = ex1
    c.add_environ(var_name)
    assert s.i == 3

def test_config_add_test_resource():
    c, s = build()
    c.add_test_resource(__name__, 'ex1.conf')
    assert s.i == 3


def test_config_add_test_resource_overrides():
    c, s = build()
    c.add_resource(__name__, 'ex2.conf')
    c.add_test_resource(__name__, 'ex1.conf')
    assert s.i == 3


def test_config_add_test_string():
    c, s = build()
    c.add_test_string("[py.test]\ni=5")
    assert s.i == 5


def test_context():
    c, s = build()
    with reconf.ResourceLocation(__name__, 'ex2.conf').context(c):
        assert s.i == 4


def test_config_location_enoent():
    c, s = build()
    c.add_resource(__name__, 'ex1.conf')
    c.add_file('/no/such/file')
    assert s.i == 3


def test_config_location_other_ioerror():
    c, s = build()
    c.add_resource(__name__, 'ex1.conf')
    c.add_file('/')
    with pytest.raises(IOError):
        s.i
