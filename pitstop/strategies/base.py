"""Abstract bases for configuration strategies."""
import abc
import dataclasses
import typing

import sortedcontainers
import structlog

import pitstop.backends.base
import pitstop.types
import pitstop.utils


__all__ = ('BaseStrategy',)

logger = structlog.get_logger()


# NOTE(darvid): python/mypy#5374
@dataclasses.dataclass  # type: ignore
class BaseStrategy(abc.ABC):
    """Abstract base class for a configuration loading strategy.

    Args:
        schema (:obj:`dict`): A :mod:`cerberus` schema.
        backends (:class:`sortedcontainers.SortedList`): A list of
            :class:`~.backends.base.BaseObjectBackend` instances,
            ordered by priority.
        bpo_map (:obj:`dict`): A mapping of :mod:`glob` compatible key
            paths to lists of backend names, facilitating certain
            configuration keys to override backend priority when being
            read from the strategy.

    """

    schema: pitstop.types.T_StrAnyMapping
    backends: sortedcontainers.SortedList = dataclasses.field(
        default_factory=pitstop.types.PrioritizedBackendList
    )
    bpo_map: pitstop.types.PriorityOverridesMap = dataclasses.field(
        default_factory=dict
    )

    _defaults_cache: pitstop.types.T_StrAnyDict = dataclasses.field(
        default_factory=dict, init=False, repr=False
    )

    def connect_all(self, decode: bool = True) -> None:
        """Initialize all backends.

        Args:
            decode (:obj:`bool`, optional): If ``True``, decodes
                configuration payloads from any backends that require
                decoding. Defaults to ``True``.

        """
        logger.debug('connect.all')
        for backend in self.backends:
            backend.connect()
            if decode and isinstance(
                backend, pitstop.backends.base.EncodingBackendMixin
            ):
                backend.decode()

    @abc.abstractmethod
    def get(self, path: str, default: typing.Any) -> typing.Any:
        """Read a configuration key **path**.

        Args:
            path (str): The key path.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The configuration value, or **default** if none exists in
            any backend.

        Raises:
            KeyError: If the configuration path does not exist in any
                backend, and a default value is not provided.

        """

    @abc.abstractmethod
    def resolve(self) -> pitstop.types.T_StrAnyMapping:
        """Resolve a complete configuration object based on schema."""

    def _get_schema_default(
        self, path: str, use_cache: bool = True
    ) -> typing.Any:
        """Get the default value for a key from current :attr:`schema`.

        Args:
            path (str): The key path.
            use_cache (bool, optional): If ``True``, default values from
                the schema are memoized to instance state. Defaults to
                ``True``.

        Returns:
            The default value or ``None`` is not set in the schema.

        Raises:
            KeyError: If the key does not exist in the schema.

        """
        if path in self._defaults_cache:
            return self._defaults_cache[path]
        for leaf, schema in pitstop.utils.schema_leaves(self.schema):
            if leaf != path:
                continue
            default = schema.get('default')
            if default is not None:
                self._defaults_cache[path] = default
            return default
        raise KeyError(path)
