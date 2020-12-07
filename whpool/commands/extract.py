#!/usr/bin/env python3

import argparse
from collections import namedtuple
# import csv
# from email.header import make_header, decode_header
import logging
# import mailbox
# import os
# from pathlib import Path
# import re
# import sys
import whpool.core.command
from whpool.extract.extract import run_command

# # Extract pool reports (email) from mbox format file and create an output
# # format suitable for curatorial review.

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# HEADERS = ['id', 'Date', 'Reporter', 'Title', 'PoolReport', 'Publish',
#            'Comments']

# File = namedtuple('File', 'name, bytes')


def configure_cli(subparsers) -> None:  # type: ignore
    """
    Configures the CLI arguments for this command
    """
    parser = subparsers.add_parser(
        name='extract',
        description='Extracts files from mbox'
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Input mbox format email file",
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help="Output directory which must already exist; files and" +
        "sub-directories will be created or overwritten as necessary.",
    )

    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="verbosity of logging output; default is 1")

    parser.set_defaults(cmd_name='extract')


class Command(whpool.core.command.Command):
    def __call__(self, args: argparse.Namespace) -> whpool.core.command.CommandResult:
        return run_command(args)
