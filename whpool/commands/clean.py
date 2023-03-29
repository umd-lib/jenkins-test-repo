import logging
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

import click
import emoji
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


def remove_ufeff(html):
    """Remove invisible characters U+FEFF"""
    html.replace(u'\ufeff', '')

    return html


def cleaner(html):
    """Sanitizes the HTML"""

    sanitizer = Sanitizer({
        "tags": {
            # Text Tags
            'p', 'br', 'hr', 'div',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'em', 'sub', 'sup', 'u', 'i', 'b',
            'blockquote', 'cite', 'q',

            # Link and Image Tags
            'a', 'img',

            # List Tags
            'ul', 'ol', 'li', 'dl', 'dt', 'dd',

            # Table Tags
            'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'col', 'colgroup', 'caption'
        },

        "attributes": {"a": ("href", "name", "target", "title", "id", "rel"),
                       "img": ("src", "name", "alt", "height"),
                       },
        "empty": {"hr", "a", "br", "img"},
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


def ms_messages(html):
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['head', 'style', 'meta']):
        tag.extract()

    empty_whitelist = ['a', 'img']
    while True:
        tag = soup.find('div', class_="WordSection1")
        if not tag:
            break
        tag.name = 'p'
        for x in soup.find_all():
            if len(x.get_text(strip=False)) == 0 and (x.name not in empty_whitelist):
                x.extract()

        for tag in soup(['p']):
            tag.append(soup.new_tag('br'))
        for tag in soup(['p', 'html', 'div']):
            tag.unwrap()
        tag_body = soup.body
        tag_body.name = 'p'

    return str(soup)


def remove_p_br_p(html):
    soup = BeautifulSoup(html, 'lxml')
    matches = soup.find_all('p')

    for match in matches:
        just_br = match.find_all('br')
        for x in just_br:
            x.extract()

    return str(soup)


def xml_escape(chars, data_dict):
    """Emoji encoding helps ensure successful html-sanitizer processing"""
    return chars.encode('ascii', 'xmlcharrefreplace').decode()


def ltr_messages(html):
    soup = BeautifulSoup(html, 'lxml')

    for tag in soup('p', class_='p1'):
        tag.append(soup.new_tag('br'))
    for tag in soup('span', class_='s1'):
        tag.wrap(soup.new_tag('b'))
    for tag in soup('p', class_='p1'):
        tag.unwrap()

    return str(soup)


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

        html_remove_odd_spaces = remove_p_br_p(html)
        html_no_pre = replace_pre_with_p(html_remove_odd_spaces)
        html_no_ufeff = remove_ufeff(html_no_pre)
        cleaned_ms_messages = ms_messages(html_no_ufeff)
        cleaned_ltr_messages = ltr_messages(cleaned_ms_messages)
        html_emoji_replaced = emoji.replace_emoji(cleaned_ltr_messages, replace=xml_escape)
        html_cleaned = cleaner(html_emoji_replaced)

        clean_file = file.with_name('body-processed-clean.html')
        with clean_file.open(mode='w+'):
            clean_file.write_text(html_cleaned)
