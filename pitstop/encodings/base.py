"""Abstract bases for encoding providers."""
import abc
import dataclasses

import pitstop.types


__all__ = ('BaseEncoding',)


# NOTE(darvid): python/mypy#5374
@dataclasses.dataclass  # type: ignore
class BaseEncoding(abc.ABC):
    """Abstract base class for an encoding."""

    @abc.abstractmethod
    def decode(self, s: str) -> pitstop.types.T_StrAnyMapping:
        """Decode the given string **s** to an object."""

    @abc.abstractmethod
    def encode(self, o: pitstop.types.T_StrAnyMapping) -> str:
        """Encode the given object **o** to a string."""
