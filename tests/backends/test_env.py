"""Environment configuration backend unit tests."""
import os

import pytest

import pitstop.backends.env


@pytest.fixture
def backend() -> pitstop.backends.env.EnvironmentBackend:
    """Provide an environment variable backend fixture."""
    options = pitstop.backends.env.EnvironmentBackendOptions()
    return pitstop.backends.env.EnvironmentBackend(  # type: ignore
        priority=1, name='env', options=options
    )


def test_connect(backend: pitstop.backends.env.EnvironmentBackend) -> None:
    """Noop for the environment backend."""
    backend.connect()


def test_get(backend: pitstop.backends.env.EnvironmentBackend) -> None:
    """Test retrieval of environment variables."""
    for var in os.environ:
        assert os.getenv(var) == backend.get(var)


def test_get_default(backend: pitstop.backends.env.EnvironmentBackend) -> None:
    """Ensure reading nonexistent keys return a default value."""
    if 'NONEXISTENT' in os.environ:
        del os.environ['NONEXISTENT']
    assert backend.get('NONEXISTENT', default='foo') == 'foo'


def test_get_nonexistent(
    backend: pitstop.backends.env.EnvironmentBackend
) -> None:
    """Ensure reading nonexistent keys throws a :class:`KeyError`."""
    if 'NONEXISTENT' in os.environ:
        del os.environ['NONEXISTENT']
    with pytest.raises(KeyError):
        backend.get('NONEXISTENT')
