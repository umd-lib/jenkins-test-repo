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
    sanitizer = Sanitizer({
        "tags": {
            "a", "h1", "h2", "h3", "h4", "h5", "h6", "strong", "em", "p", "ul", "ol",
            "li", "br", "sub", "sup", "hr", "div", "pre",
        },
        "attributes": {"a": ("href", "name", "target", "title", "id", "rel")},
        "empty": {"hr", "a", "br"},
        "separate": {"a", "li"},
        "whitespace": {},
        "keep_typographic_whitespace": True,
        "add_nofollow": False,
        "autolink": False,
        "element_postprocessors": [],
        "is_mergeable": lambda e1, e2: False,
        })

    files = []
    files = base_path.glob('**/body-processed.html')

    for file in files:
        logger.debug(file.parent)
        clean_file = file.with_name('body-processed-clean.html')
        with file.open() as body_file:
            html = body_file.read()
            with clean_file.open(mode='w+'):
                clean_file.write_text(sanitizer.sanitize(html))
