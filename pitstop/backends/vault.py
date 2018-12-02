"""Provides a HashiCorp Vault secrets key-value backend."""
import dataclasses
import typing

import hvac
import structlog
import wrapt

import pitstop.backends.base
import pitstop.errors
import pitstop.utils


__all__ = ('requires_client', 'VaultBackend', 'VaultBackendOptions')

logger = structlog.get_logger()


@wrapt.decorator
def requires_client(wrapped, instance, args, kwargs):
    """Decorate a Vault backend method, ensuring an open connection."""
    if instance.client is None:
        raise pitstop.errors.NotConnectedError(
            'Backend not connected to Vault'
        )
    return wrapped(*args, **kwargs)


@dataclasses.dataclass
class VaultBackendOptions(pitstop.utils.OptionsBag):
    """Options for the Vault backend.

    Accepts the same keyword arguments as :class:`hvac.Client`, in
    addition to the following parameters.

    Args:
        kv_version (int, optional): Vault secrets KV version. Defaults
            to ``2``.
        mount_point (str, optional): Mount point used by all Vault KV
            reads. Defaults to ``secret/``.

    """

    addr: str = dataclasses.field(default='http://localhost:8200')
    token: typing.Optional[str] = dataclasses.field(default=None)
    cert: typing.Optional[typing.Tuple[str, str]] = dataclasses.field(
        default=None
    )
    verify: bool = dataclasses.field(default=True)
    timeout: int = dataclasses.field(default=30)
    proxies: typing.Mapping[str, str] = dataclasses.field(default_factory=dict)
    allow_redirects: bool = dataclasses.field(default=True)
    namespace: typing.Optional[str] = dataclasses.field(default=None)
    kv_version: int = dataclasses.field(default=2)
    mount_point: str = dataclasses.field(default='secret/')


@dataclasses.dataclass
class VaultBackend(
    pitstop.backends.base.BaseObjectBackend,
    pitstop.utils.OptionsBagMixin[VaultBackendOptions],
):
    """Access secrets from a Vault KV store."""

    client: typing.Optional[hvac.Client] = dataclasses.field(
        init=False, default=None
    )

    def connect(self) -> None:
        """Connect to Vault."""
        self.client = hvac.Client(
            url=self.options.addr,
            token=self.options.token,
            verify=self.options.verify,
            timeout=self.options.timeout,
            proxies=self.options.proxies,
            allow_redirects=self.options.allow_redirects,
            namespace=self.options.namespace,
        )
        logger.info('backend.connected')

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Read a secret from Vault secrets KV store.

        Periods (``.``) in the provided **key** are automatically
        converted to forward slashes (``/``), so accessing the Vault
        secret at path ``/secrets/foo/bar`` will work with a key of
        ``foo.bar``, assuming :attr:`mount_point` is set to the default
        of ``secret/``.

        Args:
            key (str): The key name.
            default (:obj:`typing.Any`, optional): A default value.

        Returns:
            The secret value, or **default** if none exists.

        Raises:
            KeyError: If the environment variable does not exist,
                and a default value is not provided.

        """
        log = logger.bind(path=key)
        key = key.replace('.', '/')
        if self.options.kv_version == 1:
            value = self.get_v1(key)
        else:
            value = self.get_v2(key)
        if value is None:
            return default
        log.info('backend.get.succeeded')
        return value

    @requires_client
    def get_v1(self, path: str) -> typing.Any:
        """Read a secret from the KV v1 engine."""
        log = logger.bind(path=path)
        parent, key = path.rsplit('/', 1)
        result = self.client.secrets.kv.v1.read_secret(  # type: ignore
            path=parent, mount_point=self.options.mount_point
        )
        try:
            return result['data'][key]
        except KeyError:
            log.warn('backend.get.failed')
            raise KeyError(path)

    @requires_client
    def get_v2(self, path: str) -> typing.Any:
        """Read a secret from the KV v2 engine."""
        log = logger.bind(path=path)
        parent, key = path.rsplit('/', 1)
        result = self.client.secrets.kv.v2.read_secret_version(  # type: ignore
            parent, mount_point=self.options.mount_point
        )
        try:
            return result['data']['data'][key]
        except KeyError:
            log.warn('backend.get.failed')
            raise KeyError(path)
