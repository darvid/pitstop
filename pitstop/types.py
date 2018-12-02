"""Generics and convenient type annotation constants."""
import functools
import typing

import sortedcontainers


__all__ = ('PrioritizedBackendList', 'PriorityOverridesMap', 'T_StrAnyMapping')

PrioritizedBackendList = functools.partial(
    sortedcontainers.SortedList, key=lambda backend: backend.priority
)
PriorityOverridesMap = typing.Dict[str, typing.Iterable[str]]
T_StrAnyMapping = typing.Mapping[str, typing.Any]
