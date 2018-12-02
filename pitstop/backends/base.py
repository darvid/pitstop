"""Abstract bases for configuration backends."""
import abc
import dataclasses
import typing

import structlog
import wrapt

import pitstop.encodings.base
import pitstop.errors
import pitstop.types


__all__ = (
    'BaseObjectBackend',
    'EncodingBackendMixin',
    'requires_decoded',
    'T_BackendOptions',
)

logger = structlog.get_logger()
T_BackendOptions = typing.TypeVar('T_BackendOptions')


@wrapt.decorator
def requires_decoded(wrapped, instance, args, kwargs):
    """Decorate a backend method, ensuring an `obj` property is not None."""
    if instance.obj is None:
        raise pitstop.errors.NotDecodedError('Configuration not decoded')
    return wrapped(*args, **kwargs)


# NOTE(darvid): python/mypy#5374
@dataclasses.dataclass  # type: ignore
class BaseObjectBackend(abc.ABC):
    """Abstract base class for a configuration backend."""

    priority: int
    name: str

    def cleanup(self) -> None:
        """Clean up backend connections or descriptors."""

    @abc.abstractmethod
    def connect(self) -> None:
        """Connect to a backend."""

    @abc.abstractmethod
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Get a configuration key.

        Args:
            key: The path or name of a configuration key.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The configuration value.

        """

    def __del__(self):
        """Clean up backend connections or descriptors."""
        self.cleanup()


# NOTE(darvid): python/mypy#5374
@dataclasses.dataclass  # type: ignore
class ReloadableObjectBackend(abc.ABC):
    """Abstract base class for a reloadable :class:`BaseObjectBackend`."""

    @abc.abstractmethod
    def reload(self):
        """Reload the backend."""


@dataclasses.dataclass
class EncodingBackendMixin:
    """Mixin for backends that require deserialization in-memory."""

    encoding: pitstop.encodings.base.BaseEncoding
    s: str = ''
    obj: typing.Optional[pitstop.types.T_StrAnyMapping] = dataclasses.field(
        init=False, default=None
    )

    def decode(self) -> None:
        """Decode configuration data to backend state."""
        logger.info(
            'backend.decoding', encoding=self.encoding.__class__.__name__
        )
        self.obj = self.encoding.decode(self.s)

    def __getattribute__(self, name):  # noqa: D105
        attr = super().__getattribute__(name)
        if name in ('get',):
            return requires_decoded(attr)
        return attr


@dataclasses.dataclass
class DictBackend(BaseObjectBackend):
    """A dictionary object backend."""

    obj: pitstop.types.T_StrAnyMapping

    def cleanup(self) -> None:
        """Noop."""

    def connect(self) -> None:
        """Noop."""

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Get a configuration key.

        Args:
            key: The path or name of a configuration key.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The configuration value.

        Raises:
            KeyError: If the key does not exist, and a default value is
                not provided.

        """
        return self.obj.get(key, default)
