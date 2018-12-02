"""Filesystem backend unit tests."""
import pytest

import pitstop.backends.fs
import pitstop.encodings.json


@pytest.fixture
def backend(tmpdir):
    """Provide a filesystem backend fixture."""
    p = tmpdir.join('config.json')
    p.write('{"foo": "bar"}')
    encoding = pitstop.encodings.json.JSONEncoding.with_options()
    options = pitstop.backends.fs.FilesystemBackendOptions(path=str(p))
    return pitstop.backends.fs.FilesystemBackend(
        options, priority=1, name='fs', encoding=encoding
    )


def test_connect(backend):
    """Connect the filesystem backend (read a file)."""
    backend.connect()
    assert backend.fp is not None
