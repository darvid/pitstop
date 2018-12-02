"""Provides the version 1 configuration loading strategy."""
import dataclasses
import typing

import cerberus
import glom
import pkg_resources
import structlog

import pitstop.errors
import pitstop.strategies.base
import pitstop.types
import pitstop.utils


__all__ = ('Validator', 'VersionOneStrategy', 'VersionOneStrategyOptions')

logger = structlog.get_logger()


class Validator(cerberus.Validator):
    """A :mod:`cerberus` validator."""

    def _validate_isentrypoint(self, isentrypoint, field, value):
        """Validate an entrypoint with `pkg_resources`.

        The rule's arguments are validated against this schema:

        {'type': 'string'}
        """
        entrypoints = pkg_resources.iter_entry_points(isentrypoint)
        if value.lower() not in (e.name.lower() for e in entrypoints):
            self._error(field, f'Must be a valid entrypoint in {isentrypoint}')


@dataclasses.dataclass(frozen=True)
class VersionOneStrategyOptions(pitstop.utils.OptionsBag):
    """V1 strategy options."""


@dataclasses.dataclass
class VersionOneStrategy(
    pitstop.strategies.base.BaseStrategy,
    pitstop.utils.OptionsBagMixin[VersionOneStrategyOptions],
):
    """V1 configuration loading strategy.

    This is a naive strategy that simply maintains a sorted list of
    configuration backends by priority.

    """

    validator: cerberus.Validator = dataclasses.field(init=False)

    def __post_init__(
        self, validator: typing.Optional[cerberus.Validator] = None
    ) -> None:  # noqa: D105
        if self.options is None:
            self.options = VersionOneStrategyOptions()
        self.validator = Validator(self.schema)

    def get(self, path: str, default: typing.Any = None) -> typing.Any:
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
        log = logger.bind(path=path)
        try:
            bpo = glom.glom(self.bpo_map, path)
            backends = sorted(
                (b for b in self.backends if b.name in bpo),
                key=lambda b: bpo.index(b.name),
            )
        except glom.PathAccessError:
            backends = self.backends
        log = log.bind(bpo=[b.name for b in backends])
        log.debug('strategy.get')
        for backend in backends:
            try:
                return backend.get(path)
            except KeyError:
                continue
        if default is None:
            raise KeyError(path)
        return default

    def resolve(
        self, allow_missing: bool = True
    ) -> pitstop.types.T_StrAnyMapping:
        """Resolve a complete configuration object based on schema.

        Determines a set of configuration keys based on the current
        :attr:`schema`, and resolves each key against all backends,
        returning a nested mapping of current configuration.

        Args:
            allow_missing (:obj:`bool`, optional): If ``True``, any
                configuration keys that are present in the schema but
                missing from all backends will not raise a
                :class:`KeyError`. Defaults to ``True``.

        Returns:
            dict: Resolved and expanded configuration mapping.

        Raises:
            KeyError: If **allow_missing** is ``False``, a
                :class:`KeyError` is thrown if any configuration key
                from the :attr:`schema` could not be resolved.

        """
        document: pitstop.types.T_StrAnyMapping = {}
        for leaf, schema in pitstop.utils.leaves(self.schema):
            try:
                pitstop.utils.unglom(document, leaf, self.get(leaf))
            except KeyError:
                if not allow_missing:
                    raise
        valid = self.validator.validate(document)
        if not valid:
            raise pitstop.errors.ValidationError(self.validator.errors)
        return self.validator.document
