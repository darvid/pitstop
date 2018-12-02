"""Provides generic utilities."""
import dataclasses
import functools
import typing

import glom
import typing_inspect

from pitstop.types import T_StrAnyMapping


__all__ = ('leaves', 'OptionsBag', 'OptionsBagMixin', 'T_OptionsBag', 'unglom')


T_OptionsBag = typing.TypeVar('T_OptionsBag')


def leaves(
    d: T_StrAnyMapping, parent: typing.Optional[str] = None
) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
    """Find the leaves of a given dictionary.

    Args:
        d (:obj:`dict`): A dictionary tree.

    Yields:
        :obj:`tuple`: Leaf key and value.

    """
    for key, value in d.items():
        if parent is not None:
            key = ".".join((parent, key))
        try:
            if value["type"] == "dict":
                yield from leaves(value["schema"], parent=key)
            else:
                yield (key, value)
        except (KeyError, TypeError):
            yield (key, value)


def unglom(
    d: T_StrAnyMapping, path: str, value: typing.Any
) -> T_StrAnyMapping:
    """Create nested dictionary structure given a glom compatible path.

    This is essentially just a wrapper around :func:`glom.assign`, but
    works with nested paths.

        >>> unglom({}, 'foo.bar.baz', 'spam')
        {'foo': {'bar': {'baz': 'spam'}}}

    Args:
        d (:obj:`dict`): The target dictionary.
        path (str): The key path.
        value: Any value.

    Returns:
        :obj:`dict`: The original, now mutated dictionary.

    """
    try:
        return glom.assign(d, path, value)
    except KeyError:
        parent, child = path.rsplit(".", 1)
        return unglom(d, parent, {child: value})


@dataclasses.dataclass(frozen=True)
class OptionsBag:
    """Provides a discrete dataclass-based container for API options.

    "Options bags," at least as implemented in this library, are
    designed to leverage :mod:`dataclasses` to provide type validation
    and coercion for sets of configuration parameters. Options bags also
    simplify instance constructor signatures, by separating arbitrarily
    complex, intrinsic settings from extrinsic or otherwise unrelated
    parameters.

    Base classes with a relatively high cardinality of subclasses, each
    requiring unique configuration parameters, should ideally be
    designed as flyweights and inherit :class:`OptionsBagMixin`.

    """


@dataclasses.dataclass
class OptionsBagMixin(typing.Generic[T_OptionsBag]):
    """A mixin for dataclasses that accept an :class:`OptionsBag`.

    Provides a classmethod, :meth:`with_options`, that returns a
    :func:`functools.partial` with **options** constructed from keyword
    arguments.

    """

    options: T_OptionsBag

    @classmethod
    def with_options(cls, **options) -> typing.Callable[[], "OptionsBagMixin"]:
        """Build an options bag and return an instance partial.

        Utilizes :mod:`typing_inspect` to determine the value of the
        :obj:`T_OptionsBag` generic, and instantialize it with the given
        keyword arguments.

        Returns:
            A :func:`functools.partial` object with **options** passed.

        """
        bases = typing_inspect.get_generic_bases(cls)
        for base in bases:
            if base.__class__.__name__ == "_GenericAlias":
                args = typing_inspect.get_args(base)
                if not args:
                    raise RuntimeError(
                        "Generic backend base not passed options bag"
                    )
                return functools.partial(cls, options=args[0](**options))
        raise RuntimeError("Invalid backend bases")
