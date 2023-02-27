import logging
from datetime import datetime
from pathlib import Path

import click
from codetiming import Timer
from html_sanitizer import Sanitizer  # type: ignore

logger = logging.getLogger(__name__)


@click.command(help='Clean extracted pool reports HTML files.')
@click.option(
    '--input', '-i', 'base_dirname',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    required=True,
    help='Location of metadata and binaries to convert to an import package.'
)
@Timer(name="clean", logger=logger.info)
def clean(base_dirname: str) -> None:
    logger.info(f'{__name__}')
    logger.info(f'Date: {datetime.now()}')

    base_path = Path(base_dirname)
    sanitizer = Sanitizer()

    files = []
    files = base_path.glob('**/body-processed.html')

    for file in files:
        logger.debug(file.parent)
        clean_file = file.with_name('body-processed-clean.html')
        with file.open() as body_file:
            html = body_file.read()
            with clean_file.open(mode='w+'):
                clean_file.write_text(sanitizer.sanitize(html))
