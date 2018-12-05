"""A CLI utility that aggregates configuration sources into a JSON object."""
import json
import logging
import os
import typing

import cleo
import structlog
import toml

import pitstop
import pitstop.backends.base
import pitstop.strategies
import pitstop.strategies.base
import pitstop.types


__all__ = ('app', 'main')

app = cleo.Application("pitstop", pitstop.__version__, complete=True)


def load_strategy(
    path: str, strategy_name: typing.Optional[str] = None
) -> pitstop.strategies.base.BaseStrategy:
    """Load a configuration strategy from a pitstop configuration file."""
    filename = os.path.basename(path)
    with open(path, 'r') as f:
        config = toml.loads(f.read())
    if filename == 'pyproject.toml':
        config = config['tool']['pitstop']
    return pitstop.strategies.strategy_factory(config, strategy_name)


def main() -> None:
    """``pitstop`` entrypoint."""
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(),
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    app.add(ResolveCommand())
    app.run()


class BaseCommand(cleo.Command):
    """Base :class:`cleo.Command`."""

    def handle(self) -> None:
        """Perform shared CLI application setup.

        All CLI commands should subclass :class:`BaseCommand` and call
        :func:`super` when overriding this method.

        """
        verbosity = self.output.get_verbosity()
        if verbosity == cleo.Output.VERBOSITY_QUIET:
            level = logging.FATAL
        elif verbosity == cleo.Output.VERBOSITY_NORMAL:
            level = logging.WARN
        elif verbosity <= cleo.Output.VERBOSITY_VERBOSE:
            level = logging.INFO
        elif verbosity <= cleo.Output.VERBOSITY_DEBUG:
            level = logging.DEBUG
        root_logger = logging.getLogger()
        root_logger.setLevel(level)


class ResolveCommand(BaseCommand):
    """
    Resolve all backend sources and output resolved configuration.

    resolve
        {config? : pitstop configuration file}
        {--s|strategy=v1 : pitstop strategy version}
        {--c|compact : enable compact output}

    """

    def handle(self) -> None:  # noqa: D102
        super().handle()
        config = self.argument('config')
        strategy = self.option('strategy')
        if config is None:
            config = 'pyproject.toml'
        strategy = load_strategy(config, strategy_name=strategy)
        config = strategy.resolve()
        self.line(
            json.dumps(config, indent=None if self.option('compact') else 4)
        )


if __name__ == '__main__':
    main()
