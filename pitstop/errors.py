"""Provides error types used across the library."""


class PitstopError(Exception):
    """Generic base for all API specific errors."""


class NotConnectedError(PitstopError):
    """Indicates a backend connection failure."""


class NotDecodedError(PitstopError):
    """Indicates a decoding error."""


class ValidationError(PitstopError):
    """Indicates a schema validation error."""
