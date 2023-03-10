import logging
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

import click
from codetiming import Timer
from html_sanitizer import Sanitizer  # type: ignore

logger = logging.getLogger(__name__)


def replace_pre_with_p(html):
    """Replaces pre tag with p tag and line breaks with br"""

    if '<pre>' in html:
        html = html.replace("\n", "<br>")
        soup = BeautifulSoup(html, 'lxml')
        while True:
            tag = soup.find('pre')
            if not tag:
                break
            tag.name = 'p'
        html = str(soup)
        return html
    else:
        return html


def replace_div_with_p(html):
    """Replaces div tag with p tag and removes empty div tags"""

    empty_whitelist = ['a', 'img', 'br']

    soup = BeautifulSoup(html, 'lxml')
    while True:
        tag = soup.find('div')
        if not tag:
            break
        tag.name = 'p'
        for x in soup.find_all():
            if len(x.get_text(strip=True)) == 0 and (x.name not in empty_whitelist):
                x.extract()
    return str(soup)


def cleaner(html):
    """Sanitizes the HTML"""

    sanitizer = Sanitizer({
        "tags": {
            "p", "a", "br", "hr",
            "h1", "h2", "h3", "h4", "h5", "h6",
            "strong", "em", "sub", "sup",
            "ul", "ol", "li",
            "table", "tbody", "thead", "tr", "td",
            "blockquote", "img",
        },

        "attributes": {"a": ("href", "name", "target", "title", "id", "rel"),
                       "img": ("src", "name", "alt", "height"),
                       },
        "empty": {"hr", "a", "br"},
        "separate": {"a", "li"},
        "whitespace": {},
        "keep_typographic_whitespace": False,
        "add_nofollow": False,
        "autolink": False,
        "element_preprocessors": [],
        "element_postprocessors": [],
        "is_mergeable": lambda e1, e2: False,
        })

    html = sanitizer.sanitize(html)
    return html


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

    for file in base_path.glob('**/body-processed.html'):
        logger.debug(file.parent)
        with file.open() as body_file:
            html = body_file.read()

        html_no_pre = replace_pre_with_p(html)
        html_no_div = replace_div_with_p(html_no_pre)
        html_cleaned = cleaner(html_no_div)

        soup = BeautifulSoup(html_cleaned, 'lxml')
        clean_file = file.with_name('body-processed-clean.html')
        with clean_file.open(mode='w+'):
            clean_file.write_text(soup.prettify())
