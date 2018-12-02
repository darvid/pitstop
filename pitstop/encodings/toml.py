"""Provides TOML encoding support."""
import dataclasses

import toml

import pitstop.encodings.base
import pitstop.types
import pitstop.utils


__all__ = ('TOMLEncoding', 'TOMLEncodingOptions')


@dataclasses.dataclass(frozen=True)
class TOMLEncodingOptions(pitstop.utils.OptionsBag):
    """TOML encoding options."""


@dataclasses.dataclass
class TOMLEncoding(
    pitstop.encodings.base.BaseEncoding,
    pitstop.utils.OptionsBagMixin[TOMLEncodingOptions],
):
    """TOML encoding."""

    def decode(self, s: str) -> pitstop.types.T_StrAnyMapping:
        """Decode the given TOML encoded string **s** to an object."""
        return toml.loads(s)

    def encode(self, o: pitstop.types.T_StrAnyMapping) -> str:
        """Encode the given object **o** to a TOML encoded string."""
        return toml.dumps(o)
