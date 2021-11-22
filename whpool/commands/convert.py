import logging
import re
from csv import DictReader, DictWriter
from distutils.util import strtobool
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, TextIO

import click
from html_sanitizer import Sanitizer  # type: ignore

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def is_pool_report(row: Dict[str, str]) -> bool:
    return bool(strtobool(row['PoolReport']))


def is_publishable(row: Dict[str, str]) -> bool:
    return bool(strtobool(row['Publish']))


@click.command(help='Convert extracted pool reports metadata and files into an import package.')
@click.option(
    '--input-dir', '-I', 'base_dirname',
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
@click.option(
    '--base-id', '-b', 'base_identifier',
    required=True,
    help='String to prepend to the item id; it will be followed by a "_".'
)
def convert(output_file: TextIO, base_identifier: str, base_dirname: str) -> None:
    columns = ['Identifier', 'Title', 'Date', 'Creator', 'Object Type', 'Rights Statement', 'FILES']
    base_path = Path(base_dirname)
    sanitizer = Sanitizer()
    with open(base_path/'whpool.csv', mode='r') as input_file:
        csv_input = DictReader(input_file)
        csv_output = DictWriter(output_file, columns)
        csv_output.writeheader()
        for row in filter(is_publishable, csv_input):
            dir_name = format(int(row['id']), '03d')
            logger.info(f'Processing {dir_name}')
            files = []
            item_path = base_path/dir_name
            body_path = item_path/'body-processed-redacted.html'
            if body_path.is_file():
                # create a sanitized version of the HTML
                sanitized_path = item_path/f'body-{dir_name}.html'
                with body_path.open() as body_file:
                    html = body_file.read()
                with sanitized_path.open(mode='w') as sanitized_file:
                    sanitized_file.write(sanitizer.sanitize(html))
                files.append(sanitized_path)
            attachments_dir = item_path/'attachments'
            if attachments_dir.is_dir():
                files.extend(attachments_dir.iterdir())

            identifier = base_identifier + '_' + dir_name
            timestamp = parsedate_to_datetime(row['Date']).isoformat()
            # work around a parse_edtf bug where it does not accept "+00:00" or "-00:00"
            # as a valid timezone offset, by changing those to "Z"
            timestamp = re.sub('[+-]00:00$', 'Z', timestamp)
            item_row = {
                'Date': timestamp,
                'Title': row['Title'],
                'Creator': row['Reporter'],
                'Object Type': 'http://vocab.lib.umd.edu/form#pool_reports',
                'Rights Statement': 'http://vocab.lib.umd.edu/rightsStatement#InC-NC',
                'Identifier': identifier,
                'FILES': ';'.join(str(f.relative_to(base_path)) for f in files)
            }
            csv_output.writerow(item_row)
