import logging
import re

logger = logging.getLogger(__name__)

# Redaction replacement string: Left three-quarters block (U+258A)
REDACT_REPLACEMENT = '\u258A' * 10

REDACT_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

REDACT_PHONE = re.compile(r'''
    (\+\d{1,2}([ -]|%20)?)? # optional country code with separator
    \(?\d{3}\)?             # area code
    ([. -]|%20)             # separator
    \d{3}                   # exchange
    ([. -]|%20)             # separator
    \d{4}                   # local
''', re.VERBOSE)

REDACT_ADDRESSES = [
    "1025 Connecticut Ave. NW, Suite 800 | Washington, D.C. 20036",

    "1630 Connecticut Avenue NW, 7th Floor, Washington, DC 20009",

    "1627 I Street NW",
    "Washington, DC 20006",

    "1920 L Street NW, Suite 200",
    "Washington DC 20036",


    "2020 Technology Parkway, Suite 300, Mechanicsburg, PA 17050",

    r"214&nbsp;Massachusetts&nbsp;Avenue,&nbsp;NE",
    r"Washington,&nbsp;DC&nbsp;20002",

    "319 Main Street",
    "Hyannis, MA 02601",

    "3600 New York Ave NE | Washington DC, 20002",

    "424 W. 1st St. Duluth, MN 55802",

    "51 Astor Place, 9th Floor, New York, NY 10003",

    "529 14th Street NW, Suite 960-A",
    "Washington, D.C. 20045",

    "529 14th Street NW Suite 994",
    "Washington, DC 20045",

    "600 New Hampshire Ave. NW",
    "8th Floor",
    "Washington DC 20037-2403",

    "6752 Cincinnati-Dayton Rd. Suite 205, Liberty Twp., OH 45044",

    "75 N. Washington St.",
    "Wilkes-Barre, PA 18711",

    "900 17th St NW, Suite 250",
    "Washington, DC 20006",

]


def redact(html: str) -> str:
    """ Redact content from the body. """

    # Remove email addresses
    html = REDACT_EMAIL.sub(REDACT_REPLACEMENT, html)

    # Remove US phone numbers
    html = REDACT_PHONE.sub(REDACT_REPLACEMENT, html)

    # Remove physical addresses
    html = physical_addresses(html)

    return html


def physical_addresses(html: str) -> str:
    # Redact addresses from a hard-coded list
    for address in REDACT_ADDRESSES:
        if address in html:
            logger.debug(f"Redacting {address}")
            html = html.replace(address, REDACT_REPLACEMENT)

    return html
