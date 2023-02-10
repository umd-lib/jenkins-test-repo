import logging
import pkgutil

from importlib import import_module
from typing import List

import click

from whpool import VERSION, commands

logger = logging.getLogger(__name__)


class DynamicCLI(click.MultiCommand):
    def list_commands(self, ctx: click.Context) -> List[str]:
        return [m.name for m in pkgutil.iter_modules(commands.__path__)]  # type: ignore

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command:
        try:
            module = import_module(f'whpool.commands.{cmd_name}')
        except ModuleNotFoundError as e:
            raise click.UsageError(f'Unrecognized command: {cmd_name}') from e
        for name in dir(module):
            attr = getattr(module, name)
            if isinstance(attr, click.Command):
                return attr

        # raise a usage error if no matching command can be found
        raise click.UsageError(f'Unrecognized command: {cmd_name}')


def logging_verbosity(verbosity):
    """Set logger verbosity level."""
    if verbosity == 0:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
    elif verbosity == 1:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    elif verbosity == 2:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


@click.command(
    name='whpool',
    help='WHCA Utilities',
    cls=DynamicCLI
)
@click.version_option(VERSION, '--version', '-V', prog_name='whpool')
@click.option(
    '-v', '--verbose', 'verbosity',
    default=1,
    help='''\b
            Set verbosity logging output level.
            0 = Warning
            1 = Info (default)
            2 = Debug'''
)
def main(verbosity: int) -> None:
    logging_verbosity(verbosity)


if __name__ == "__main__":
    main()
