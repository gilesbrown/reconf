import os
import logging
from uuid import uuid4
from pkg_resources import resource_filename, resource_string
import pytest
import reconf

ex1 = resource_filename(__name__, 'ex1.conf')

def build(*settings):
    config = reconf.Config()
    settings = config.settings(*settings)
    return config, settings


def test_config():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_resource(__name__, 'ex1.conf')
    assert s.i == 3
    # And this one should come from the cache
    assert s.i == 3


def test_config_add_file():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_file(ex1)
    assert s.i == 3


def test_config_add_file_is_idempotent():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_file(ex1)
    c.add_file(ex1)
    assert len(c.locations) == 1


def test_config_add_environ():
    c, s = build(reconf.Integer('mysection:i'))
    var_name = str(uuid4())
    os.environ[var_name] = ex1
    c.add_environ(var_name)
    assert s.i == 3

def test_config_add_test_resource():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_test_resource(__name__, 'ex1.conf')
    assert s.i == 3


def test_config_add_test_resource_overrides():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_resource(__name__, 'ex2.conf')
    c.add_test_resource(__name__, 'ex1.conf')
    assert s.i == 3


def test_config_add_test_string():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_test_string(resource_string(__name__, 'ex1.conf'))
    assert s.i == 3


def test_context():
    c, s = build(reconf.Integer('mysection:i'))
    with reconf.ResourceLocation(__name__, 'ex2.conf').context(c):
        assert s.i == 4


def test_config_location_enoent():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_resource(__name__, 'ex1.conf')
    c.add_file('/no/such/file')
    assert s.i == 3


def test_config_location_other_ioerror():
    c, s = build(reconf.Integer('mysection:i'))
    c.add_resource(__name__, 'ex1.conf')
    c.add_file('/')
    with pytest.raises(IOError):
        s.i

def test_config_configure_logging(tmpdir):
    c, s = build()
    c.defaults['tempdir'] = tmpdir.strpath
    c.add_resource(__name__, 'exlogging.conf')
    c.configure_logging()
    logger = logging.getLogger('my.Logger')
    logger.info('HELLO')
    with tmpdir.join('hand01.log').open() as log:
        assert log.read() == 'INFO HELLO\n'

