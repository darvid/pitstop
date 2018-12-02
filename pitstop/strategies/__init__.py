"""Provides configuration loading strategies.

Strategies are factories that manage the state and priority of one or
more configuration backends, and route configuration reads to the
appropriate backend(s).

"""
import typing

import glom
import stevedore

import pitstop.strategies.base
import pitstop.types


__all__ = ('strategy_factory',)


def strategy_factory(
    config: pitstop.types.T_StrAnyMapping,
    strategy_name: typing.Optional[str] = None,
) -> 'pitstop.strategies.base.BaseStrategy':
    """Initialize a strategy from a configuration object."""
    if strategy_name is None:
        strategy_name = f'v{glom.glom(config, "strategy.version", default=1)}'
    strategy_mgr = stevedore.driver.DriverManager(
        namespace='pitstop.strategies', name=strategy_name
    )
    strategy = strategy_mgr.driver.with_options(
        **glom.glom(config, 'strategy.options', default={})
    )(
        schema=config['schema'],
        bpo_map=glom.glom(
            config, 'strategy.backend_priority_overrides', default={}
        ),
    )
    for backend_cfg in config.get('backends', []):
        backend_mgr = stevedore.driver.DriverManager(
            namespace='pitstop.backends', name=backend_cfg['driver']
        )
        driver = backend_mgr.driver.with_options(**backend_cfg['options'])
        priority = backend_cfg.get('priority', -1)
        name = backend_cfg.get('name', backend_cfg['driver'])
        if issubclass(
            backend_mgr.driver, pitstop.backends.base.EncodingBackendMixin
        ):
            encoding = stevedore.driver.DriverManager(
                namespace='pitstop.encodings', name=backend_cfg["encoding"]
            ).driver.with_options()
            strategy.backends.add(
                driver(priority=priority, name=name, encoding=encoding())
            )
        else:
            strategy.backends.add(driver(priority=priority, name=name))
    strategy.connect_all()
    return strategy
