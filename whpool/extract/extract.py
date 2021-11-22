import logging
import mailbox
import os
import re
from csv import DictWriter

from email.header import make_header, decode_header
from pathlib import Path
from typing import Dict, Optional, Any
from whpool.core.external_images import ExternalFileError, ExternalImages
from whpool.core.message_file import MessageFile

logger = logging.getLogger(__name__)

HEADERS = ['id', 'Date', 'Reporter', 'Title', 'PoolReport', 'Publish', 'Comments']

OUTPUT_ATTACHMENTS_SUBDIR = "attachments/"

EXTERNAL_FILES_SUBDIR = "external_files/"

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


class Redact:
    REDACT_REPLACEMENT = '\u258A' * 10  # Replacement string: Left three quarters block

    REDACT_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    REDACT_PHONE = re.compile(r'''
        (\+\d{1,2}([ -]|%20)?)? # optional country code with separator
        \(?\d{3}\)?             # area code
        ([. -]|%20)             # separator
        \d{3}                   # exchange
        ([. -]|%20)             # separator
        \d{4}                   # local
    ''', re.VERBOSE)

    @staticmethod
    def redact(html: str) -> str:
        """ Redact content from the body. """

        # Remove email addresses
        html = Redact.REDACT_EMAIL.sub(Redact.REDACT_REPLACEMENT, html)

        # Remove US phone numbers
        html = Redact.REDACT_PHONE.sub(Redact.REDACT_REPLACEMENT, html)

        # Remove physical addresses
        html = Redact.physical_addresses(html)

        return html

    @staticmethod
    def physical_addresses(html: str) -> str:
        # Redact addresses from a hard-coded list
        for address in REDACT_ADDRESSES:
            if address in html:
                logger.debug(f"Redacting {address}")
                html = html.replace(address, Redact.REDACT_REPLACEMENT)

        return html


class PoolReport:
    # https://docs.python.org/3/library/re.html
    # r'\b...\b' is for matching "whole words"
    NONPOOL_REPORT_MARKERS = [
        re.compile('[Dd]ear [Cc]olleagues'),
        re.compile('[Hh]ello [Cc]olleagues'),
        re.compile('Colleagues'),
        re.compile('OFF RECORD', re.IGNORECASE),
        re.compile('off the record', re.IGNORECASE),
        re.compile(r'\bFPPO\b'),
        re.compile('non-reportable', re.IGNORECASE),
        re.compile(r'\breportable\b', re.IGNORECASE)
    ]

    @staticmethod
    def is_pool_report(html: str) -> bool:
        """
        Returns True if the given HTML appears to be pool report, False
        otherwise.
        """

        for marker in PoolReport.NONPOOL_REPORT_MARKERS:
            if marker.search(html):
                return False

        return True

    @staticmethod
    def process_pool_report(processed: Dict[str, Any]) -> None:
        """
        Sets the "PoolReport" entry in the given "processed" dictionary to
        "false" if the message is not a pool report.
        """
        title = processed['Title']
        body = processed['processed_body_html']

        if not (PoolReport.is_pool_report(title) and PoolReport.is_pool_report(body)):
            processed['PoolReport'] = 'false'

        logger.debug(f"PoolReport={processed['PoolReport']}")


def process_attachments(processed: Dict[str, Any]) -> None:
    """
    Updates processed['processed_body_html'], replacing
    links to attachments (assumed to have the form "cid:<content id>")
    with a link to the local copy of the file.
    """
    for file in processed['files']:
        if file.content_id:
            content_id = file.content_id
            filename = file.filename
            output_subdir = file.output_subdir

            str_to_replace = f"cid:{content_id}"

            path = Path(filename)
            if output_subdir:
                path = Path(output_subdir) / filename
            replacement_str = str(path)

            body = processed['processed_body_html']
            body = body.replace(str_to_replace, replacement_str)

            logger.debug(f"Replaced {str_to_replace} with {replacement_str}")
            processed['processed_body_html'] = body


def process_external_images(processed: Dict[str, Any], external_images: ExternalImages) -> None:
    """
    Updates processed['processed_body_html'], replacing
    links to external images with a link to a local copy of the file.
    """
    msg_id = processed['id']

    output_subdir = EXTERNAL_FILES_SUBDIR

    for src in external_images.srcs(msg_id):
        try:
            filename = external_images.get_file(src).filename
        except ExternalFileError:
            logger.warning(f"Unable to retrieve external image {src} for message {msg_id}")
            continue

        str_to_replace = src

        path = Path(filename)
        if output_subdir:
            path = Path(output_subdir) / filename
        replacement_str = str(path)

        body = processed['processed_body_html']

        if str_to_replace in body:
            body = body.replace(str_to_replace, replacement_str)

            logger.debug(f"Replaced '{str_to_replace}' with '{replacement_str}'")
            processed['processed_body_html'] = body
        else:
            logger.warning(f"Expected '{str_to_replace}' in message {msg_id}, but it was not found.")


def process_message(msg_id: str, message: mailbox.Message, external_images: ExternalImages) -> Optional[Dict[str, Any]]:
    """ Process a single message and return as a dict. """

    processed = {
        'id': msg_id,
        'PoolReport': 'true',
        'Publish': 'false',
        'Comments': '',
    }

    # Extract the headers
    for header, value in message.items():

        # Decode and convert to str
        value = str(make_header(decode_header(value)))

        if header == 'Date':
            processed['Date'] = value
            logger.debug(f'date: {value}')

        elif header == 'From':
            # For now, ignore the messages which were forwarded manually from
            # lib-whpoolreports to lib-whpoolreports-service
            if 'lib-whpoolreports' in value:
                return None

            processed['Reporter'] = process_reporter(value)

        elif header == 'Subject':
            process_title(processed, value)

    # Process all parts and attachments
    process_files(processed, message)

    # Process the body content
    process_body(processed)

    # Replace <img> content ids with links to attachments
    process_attachments(processed)

    # Replace external image links with links to local copies
    process_external_images(processed, external_images)

    # Determine whether message is a pool report
    PoolReport.process_pool_report(processed)

    return processed


def process_files(processed: Dict[str, Any], message: mailbox.Message) -> None:
    """ Process all parts and attachments. """

    processed['files'] = []

    # Iterate over each part of the message
    for part in message.walk():
        content_type = part.get_content_type()
        filename = part.get_filename()

        logger.debug(f'attachment: {content_type=}')
        logger.debug(f'attachment: {filename=}')

        output_subdir = OUTPUT_ATTACHMENTS_SUBDIR

        # Assert that this won't happen
        if filename in ('body.html', 'body.txt', 'body-redacted.html'):
            m = f'filename conflict: {filename}'
            logger.error(m)
            raise Exception(m)

        content = None
        content_id = ''

        if content_type in ('text/plain', 'text/html'):
            # Decode and convert back to UTF-8 bytes
            content = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if charset is None:
                charset = 'UTF-8'
            string = content.decode(charset)
            content = string.encode('UTF-8')

            if not filename:
                # Likely a body part
                if content_type == 'text/plain':
                    filename = 'body.txt'
                    output_subdir = ''
                else:
                    filename = 'body.html'
                    output_subdir = ''

        elif filename:
            content = part.get_payload(decode=True)
            content_id = part['Content-ID']
            if content_id:
                # Strip off starting "<" and ending ">"
                content_id = content_id.replace("<", "").replace(">", "")

        # Anything we want to save now has a filename and bytes to store
        if filename:
            processed['files'].append(MessageFile(filename, content, output_subdir, content_id))


body_scrub = [
    '''-- \nTo unsubscribe from this group and stop receiving emails from it, send an email to all+unsubscribe@whpoolreports.com.''',  # noqa
    '''-- <br />\nTo unsubscribe from this group and stop receiving emails from it, send an email to <a href="mailto:all+unsubscribe@whpoolreports.com">all+unsubscribe@whpoolreports.com</a>.<br />''',  # noqa
]


p_charset = re.compile(r'charset=[a-zA-Z0-9-]+')


def create_canonical_body_html(processed: Dict[str, Any]) -> None:
    # Populates the given "processed" object with two additional fields:
    #   * canonical_body_html - representing with original HTML the body,
    #                           or the HTML-ized version of the text.
    #   * processed_body_html - Initially the same as "canonical_body_html"
    #                           but changed into the final HTML by the
    #                           various filters

    # Extract the body
    html, text = None, None
    for file in processed['files']:
        if file.filename == 'body.html':
            html = file.bytes.decode('UTF-8')
        elif file.filename == 'body.txt':
            text = file.bytes.decode('UTF-8')

    # Use the text version if HTML is not available
    if not html:
        if not text:
            m = f'Unable to find message body: {processed["id"]}'
            logger.error(m)
            raise Exception(m)

        html = f"<html><body><pre>{text}</pre></body></html>"

    processed['canonical_body_html'] = html
    processed['processed_body_html'] = html


def process_body(processed: Dict[str, Any]) -> None:
    """ Generate body-redacted.html. """
    create_canonical_body_html(processed)

    html = processed['processed_body_html']

    # Scrub specific string values
    for scrub in body_scrub:
        if scrub in html:
            html = html.replace(scrub, '')
            logger.debug(f'body: scrubbed "{scrub}"')

    # Update the charset since we have convert to utf-8
    html = p_charset.sub("charset=utf-8", html)

    processed['processed_body_html'] = html


title_scrub = [
    '[WH Pool] ',
    '\n',
]


def process_title(processed: Dict[str, Any], value: str) -> None:
    """ Build the Title field from the message Subject header. """

    logger.debug(f'title: Subject={value}')

    for scrub in title_scrub:
        if scrub in value:
            value = value.replace(scrub, '')
            logger.debug(f'title: scrubbed "{scrub}": {value}')

    processed['Title'] = value


reporter_scrub = [
    ', Senior White House Correspondent',
    'via All',
    'EOP/WHO',
]


reporter_extract = re.compile(r'''
    ^
    ["\' ]*     # ignore punctuation and whitespace
    (.*?)       # reporter name (minimal match)
    ["\' ]*     # ignore punctuation and whitespace
    (?:\(.+\))? # ignore a title or organization in parentheses
    ["\' ]*     # ignore punctuation and whitespace
    <.*>        # ignore the email address
    $
''', re.VERBOSE)


def process_reporter(value: str) -> str:
    """ Build the Reporter field from the message From header. """

    logger.debug(f'reporter: From={value}')

    for scrub in reporter_scrub:
        if scrub in value:
            value = value.replace(scrub, '')
            logger.debug(f'reporter: scrubbed "{scrub}": {value}')

    if m := reporter_extract.match(value):
        s = re.split(r' *, *', m[1])
        if len(s) == 1:
            value = s[0]
        else:
            # Change "LastName, FirstName" to "FirstName LastName"
            # Ignore anything after a second comma
            value = s[1] + " " + s[0]

        logger.debug(f'reporter: extracted: {value}')

    return value


def write_message(
    msg_id: str, processed: Dict[str, Any], writer: DictWriter,
        output_dir: Path, external_images: ExternalImages) -> None:
    """ Write out a single processed message. """

    # Write metadata to the CSV file
    writer.writerow(processed)

    # Add the "processed" HTML to the "processed" files list for output
    processed['files'].append(MessageFile('body-processed.html', processed['processed_body_html'].encode('UTF-8')))

    # Redact and add the "body-redacted.html" to the "processed" files list
    # for output
    processed['processed_body_redacted_html'] = Redact.redact(processed['processed_body_html'])
    processed['files'].append(MessageFile('body-processed-redacted.html',
                                          processed['processed_body_redacted_html'].encode('UTF-8')))

    # Create the directory for storing per message files
    message_dir = output_dir / f'{processed["id"]:03d}'

    logger.debug(f'message directory: {message_dir}')

    if not message_dir.is_dir():
        try:
            os.mkdir(message_dir)
        except OSError as e:
            logger.error(f'Error creating {message_dir}: {e}')
            return
        else:
            logger.debug(f'created {message_dir}')

    # Create the files

    for extract_file in processed['files']:
        filename = extract_file.filename
        extracted_bytes = extract_file.bytes
        output_subdir = extract_file.output_subdir

        logger.debug(f'Creating filename={filename}, size={len(extracted_bytes)}, output_subdir={output_subdir}')
        out_dir = message_dir / output_subdir
        if not out_dir.is_dir():
            # Make sure subdirectory exists
            os.mkdir(out_dir)

        with open(out_dir / filename, 'wb') as outfile:
            outfile.write(extracted_bytes)

    # Write the external files
    for src in external_images.srcs(msg_id):
        try:
            external_image_file = external_images.get_file(src)
        except ExternalFileError:
            logger.warning(f'Skipping {src}, external file is not retrievable')
            continue

        filename = external_image_file.filename
        extracted_bytes = external_image_file.bytes
        output_subdir = EXTERNAL_FILES_SUBDIR

        logger.debug(
            f'Creating external file: filename={filename}, size={len(extracted_bytes)}, output_subdir={output_subdir}'
        )

        out_dir = message_dir / output_subdir
        if not out_dir.is_dir():
            # Make sure subdirectory exists
            os.mkdir(out_dir)

        with open(out_dir / filename, 'wb') as outfile:
            outfile.write(extracted_bytes)
