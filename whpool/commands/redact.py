import logging
import re
from pathlib import Path
from typing import Dict, List, Pattern, TextIO
from datetime import datetime

import click
import yaml
from codetiming import Timer

from whpool.core.redaction import REDACT_PATTERNS, RedactedText

logger = logging.getLogger(__name__)


def load_redact_strings(strings_file: TextIO) -> List[str]:
    if strings_file is None:
        return []

    redact_strings = []
    for line in strings_file:
        line = line.strip()
        if line == '' or line.startswith('#'):
            # skip empty lines and comment lines
            continue
        redact_strings.append(line)
    return redact_strings


def load_redact_patterns(patterns_file: TextIO) -> Dict[str, Pattern[str]]:
    if patterns_file is None:
        return {}

    return {k: re.compile(v, re.VERBOSE) for k, v in yaml.safe_load(patterns_file).items()}


@click.command(help='Redact strings or patterns in extracted message bodies in the given directories.')
@click.option(
    '--strings-from-file', 'strings_file',
    type=click.File(),
    help='File containing exact strings to redact, one per line.'
)
@click.option(
    '--patterns-from-file', 'patterns_file',
    type=click.File(),
    help='YAML file containing a map of labels to regular expressions to redact.'
)
@click.option(
    '--dry-run', '-n',
    is_flag=True,
    help='Display the redacted text, but do not write the output file.'
)
@click.argument(
    'directories',
    nargs=-1,
    type=click.Path(exists=True, file_okay=False),
)
@Timer(name="redact", logger=logging.info)
def redact(strings_file: TextIO, patterns_file: TextIO, dry_run: bool, directories: List[str]) -> None:
    logger.info(f'{__name__}')
    logger.info(f'Date: {datetime.now()}')

    redact_strings = load_redact_strings(strings_file)
    redact_patterns = {**REDACT_PATTERNS, **load_redact_patterns(patterns_file)}

    for directory in map(Path, directories):
        processed_body_file = directory / 'body-processed.html'
        if not processed_body_file.exists():
            logger.warning(f'Directory {directory} does not contain a "body-processed.html"; skipping')
            continue

        with processed_body_file.open(mode='r') as fh:
            html = fh.read()

        redacted_html = RedactedText(html)

        # Remove by patterns (e.g., email, phone numbers)
        for label, pattern in redact_patterns.items():
            redacted_html.redact(pattern, f"{label} pattern")

        # Remove exact strings (e.g., physical addresses)
        for string in redact_strings:
            redacted_html.redact(string, f'"{string}"')

        print(directory)

        if dry_run:
            print('=' * 80)
            print(redacted_html)
            print('=' * 80)
        else:
            redacted_body_file = directory / 'body-processed-redacted.html'
            with redacted_body_file.open(mode='w') as fh:
                fh.write(str(redacted_html))

            print(f'Wrote redacted version to {redacted_body_file}')

        print('Total redactions:', sum(redacted_html.matches.values()))
        for label, count in redacted_html.matches.items():
            print('  Redacted', count, 'occurrence(s) of', label)
