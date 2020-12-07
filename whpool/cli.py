#!/usr/bin/env python3

import argparse
from collections import namedtuple
from pkgutil import iter_modules
import csv
from email.header import make_header, decode_header
import logging
import mailbox
import os
from pathlib import Path
import re
import sys
from importlib import import_module
from whpool import commands, VERSION

logger = logging.getLogger(__name__)


def main() -> None:
    """Parse args and handle options."""

    parser = argparse.ArgumentParser(
        prog='whpool',
        description='WHCA Utilities'
    )
    parser.set_defaults(cmd_name=None)

    parser.add_argument(
        '-V', '--version',
        help='Print version and exit.',
        action='version',
        version=VERSION
    )

    parser.add_argument(
        '-v', '--verbose',
        help='increase the verbosity of the status output',
        action='store_true'
    )

    parser.add_argument(
        '-q', '--quiet',
        help='decrease the verbosity of the status output',
        action='store_true'
    )

    subparsers = parser.add_subparsers(title='commands')

    # load all defined subcommands from the whpool.commands package
    command_modules = {}
    for _finder, name, _ispkg in iter_modules(commands.__path__):  # type: ignore[attr-defined]
        module = import_module(commands.__name__ + '.' + name)
        if hasattr(module, 'configure_cli'):
            module.configure_cli(subparsers)  # type: ignore[attr-defined]
            command_modules[name] = module

    # parse command line args
    args = parser.parse_args()

    # if no subcommand was selected, display the help
    if args.cmd_name is None:
        parser.print_help()
        sys.exit(0)

    # get the selected subcommand
    command = command_modules[args.cmd_name].Command()  # type: ignore[attr-defined]

    # logger.info(f"Starting {args.cmd_name} at {now} with args: {args}")

    try:
        # dispatch to the selected subcommand
        print_header(args)
        # logger.info(f'Loaded repo configuration from {args.repo}')
        # if args.delegated_user is not None:
        #     logger.info(f'Running repository operations on behalf of {args.delegated_user}')
        result = command(args)

        if result.was_successful() is False:
            errors = result.errors
            if len(errors) > 0:
                print("ERRORS OCCURRED")
                print("The following errors occurred:")
                for error in errors:
                    print(f"\t{error}")

            sys.exit(1)

        print_footer(args)
    except KeyboardInterrupt:
        # aborted due to Ctrl+C
        sys.exit(2)
    except Exception as ex:
        # something failed, exit with non-zero status
        logger.exception(ex)
        sys.exit(1)


def print_header(args: argparse.Namespace) -> None:
    """Common header formatting."""
    if not args.quiet:
        title = '|       whpool       |'
        bar = '+' + '=' * (len(title) - 2) + '+'
        spacer = '|' + ' ' * (len(title) - 2) + '|'
        print('\n'.join(['', bar, spacer, title, spacer, bar, '']), file=sys.stderr)


def print_footer(args: argparse.Namespace) -> None:
    """Report success or failure and resources created."""
    if not args.quiet:
        print('\nScript complete. Goodbye!\n', file=sys.stderr)


if __name__ == "__main__":
    main()
