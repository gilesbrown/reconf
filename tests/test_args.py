from six import text_type
# we aim to test using only the public API
import reconf


def test_python_dict():
    config = reconf.Config()
    settings = config.settings(reconf.Integer('args:i'))
    parser = settings.argument_parser()
    value = 9
    parser.parse_args(['--args:i', text_type(value)])
    assert settings.i == value
