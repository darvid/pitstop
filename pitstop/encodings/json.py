"""Provides JSON encoding support."""
import dataclasses
import json

import pitstop.encodings.base
import pitstop.types
import pitstop.utils


__all__ = ('JSONEncoding', 'JSONEncodingOptions')


@dataclasses.dataclass(frozen=True)
class JSONEncodingOptions(pitstop.utils.OptionsBag):
    """JSON encoding options.

    Args:
        encoding (str): The *character* encoding to use when encoding
            and decoding. Defaults to ``utf-8``.

    """

    encoding: str = 'utf-8'


@dataclasses.dataclass
class JSONEncoding(
    pitstop.encodings.base.BaseEncoding,
    pitstop.utils.OptionsBagMixin[JSONEncodingOptions],
):
    """JSON encoding utilizing :mod:`json` from the standard library."""

    def decode(self, s: str) -> pitstop.types.T_StrAnyMapping:
        """Decode the given JSON encoded string **s** to an object."""
        return json.loads(s, encoding=self.options.encoding)

    def encode(self, o: pitstop.types.T_StrAnyMapping) -> str:
        """Encode the given object **o** to a JSON encoded string."""
        return json.dumps(o)
