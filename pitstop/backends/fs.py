"""Provides a local filesystem backend."""
import dataclasses
import typing

import glom
import structlog

import pitstop.backends.base
import pitstop.utils


__all__ = ('FilesystemBackend', 'FilesystemBackendOptions')

logger = structlog.get_logger()


@dataclasses.dataclass(frozen=True)  # type: ignore
class FilesystemBackendOptions(pitstop.utils.OptionsBag):
    """Options for the filesystem backend.

    Args:
        path (str): The path to a configuration file.
        file_encoding (str, optional): The file encoding. Defaults to
            ``utf-8``.
        enable_checksums (bool, optional): If ``True``, the checksum of
            the file will be recorded on read, and compared against the
            previous checksum on reloading, returning a :obj:`bool`
            indicating whether or not the file was modified since last
            read.

    """

    path: str
    file_encoding: str = dataclasses.field(default='utf-8')
    enable_checksums: bool = dataclasses.field(default=True)


# See python/mypy#5681
@dataclasses.dataclass
class FilesystemBackend(
    pitstop.backends.base.ReloadableObjectBackend,
    pitstop.backends.base.EncodingBackendMixin,
    pitstop.backends.base.BaseObjectBackend,
    pitstop.utils.OptionsBagMixin[FilesystemBackendOptions],
):
    """Access configuration from a local file."""

    fp: typing.Optional[typing.TextIO] = dataclasses.field(
        init=False, default=None
    )
    checksum: int = dataclasses.field(init=False, default=0)

    def cleanup(self) -> None:
        """Close the file descriptor."""
        logger.debug('backend.cleanup')
        if self.fp is not None:
            self.fp.close()
            self.fp = None
            self.checksum = 0

    def connect(self) -> None:
        """Open a file descriptor and read into memory."""
        self.fp = open(
            self.options.path, mode='r', encoding=self.options.file_encoding
        )
        self.s = self.fp.read()
        log = logger.bind(
            path=self.options.path, length=f'{len(self.s)/1000:.1f}K'
        )
        if self.options.enable_checksums:
            self.checksum = hash(self.s)
            log = log.bind(checksum=self.checksum)
        log.info('backend.connected')

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Read a configuration key from the decoded configuration file.

        Args:
            key (str): The key name.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The configuration value, or **default** if key not present.

        """
        log = logger.bind(path=key)
        try:
            value = glom.glom(self.obj, key)
            log.info('backend.get.succeeded')
            return value
        except glom.PathAccessError:
            if default is not None:
                return default
            log.warn('backend.get.failed')
            raise KeyError(key)

    def reload(self) -> bool:
        """Reload the configuration file.

        Returns:
            bool: ``True`` if the file was changed since last read,
                otherwise ``False``.

        """
        checksum = self.checksum
        self.cleanup()
        self.connect()
        logger.info(
            'reloaded',
            path=self.options.path,
            changed=self.checksum != checksum,
        )
        return self.checksum != checksum
