"""Package-level unit tests."""
from pitstop import __version__


def test_version():
    """Version test."""
    assert __version__ == '0.1a1'
