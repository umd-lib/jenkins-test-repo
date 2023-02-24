import logging
import re
from csv import DictReader, DictWriter
from datetime import datetime
from distutils.util import strtobool
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, TextIO

import click
from codetiming import Timer
from html_sanitizer import Sanitizer  # type: ignore

logger = logging.getLogger(__name__)


def get_files(base_path: Path, dir_name: str, sanitizer: Sanitizer) -> List[Path]:
    files = []
    item_path = base_path / dir_name
    body_path = item_path / 'body-processed-redacted.html'
    if body_path.is_file():
        # create a sanitized version of the HTML
        sanitized_path = item_path / f'body-{dir_name}.html'
        with body_path.open() as body_file:
            html = body_file.read()
        with sanitized_path.open(mode='w') as sanitized_file:
            sanitized_file.write(sanitizer.sanitize(html))
        files.append(sanitized_path)
    attachments_dir = item_path / 'attachments'
    if attachments_dir.is_dir():
        files.extend(attachments_dir.iterdir())
    return files


@click.command(help='Clean extracted pool reports HTML files.')
@click.option(
    '--input', '-i', 'base_dirname',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True,
    help='Location of metadata and binaries to convert to an import package.'
)
@click.option(
    '--output', '-o', 'output_file',
    type=click.File(mode='w'),
    required=True,
    help='Output CSV file; use "-" for STDOUT.'
)
@Timer(name="clean", logger=logger.info)
def clean(output_file: TextIO, base_dirname: str) -> None:
    logger.info(f'{__name__}')
    logger.info(f'Date: {datetime.now()}')

    base_path = Path(base_dirname)
    sanitizer = Sanitizer()
    with open(base_path/'whpool.csv', mode='r') as input_file:
        csv_input = DictReader(input_file)
        csv_output = DictWriter(output_file, OUTPUT_COLUMNS)
        csv_output.writeheader()
        for row in filter(is_publishable, csv_input):
            dir_name = format(int(row['id']), '03d')
            logger.info(f'Processing {dir_name}')
            files = [str(f.relative_to(base_path)) for f in get_files(base_path, dir_name, sanitizer)]
            identifier = base_identifier + '_' + dir_name
            csv_output.writerow(get_item_row(identifier, row, files))

# need to remove csv formatting
