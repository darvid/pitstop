"""Provides a process environment backend."""
import dataclasses
import os
import typing

import structlog

import pitstop.backends.base
import pitstop.utils


__all__ = ('EnvironmentBackend', 'EnvironmentBackendOptions')

logger = structlog.get_logger()


@dataclasses.dataclass
class EnvironmentBackendOptions(pitstop.utils.OptionsBag):
    """Options for the environment backend.

    Args:
        prefix (str): If provided, all environment variables are
            prefixed with this value.

    """

    prefix: str = dataclasses.field(default='')


@dataclasses.dataclass
class EnvironmentBackend(
    pitstop.backends.base.BaseObjectBackend,
    pitstop.utils.OptionsBagMixin[EnvironmentBackendOptions],
):
    """Access configuration from environment variables."""

    def connect(self) -> None:
        """Noop."""
        logger.info('backend.connected', pid=os.getpid())

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Read a configuration key from the process environment.

        Periods (``.``) in the provided **key** are automatically
        converted to underscores (``_``), so accessing the environment
        variable ``FOO_BAR_BAZ`` will work with a key of
        ``foo.bar.baz``.

        Args:
            key (str): The key name.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The environment variable value, or **default** if none
            exists.

        Raises:
            KeyError: If the environment variable does not exist,
                and a default value is not provided.

        """
        log = logger.bind(path=key)
        value = os.getenv(self.options.prefix + key.replace('.', '_'))
        if value is None:
            if default is not None:
                return default
            log.warn('backend.get.failed')
            raise KeyError(key)
        log.info('backend.get.succeeded')
        return value
