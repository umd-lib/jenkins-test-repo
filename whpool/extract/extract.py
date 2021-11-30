import logging
import mailbox
import os
import re
from csv import DictWriter
from email.header import decode_header, make_header
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence

from whpool.core.external_image_file import ExternalImageFile
from whpool.core.external_images import ExternalImages
from whpool.core.message_file import MessageFile

logger = logging.getLogger(__name__)

HEADERS = ['id', 'Date', 'Reporter', 'Title', 'PoolReport', 'Publish', 'Comments']

OUTPUT_ATTACHMENTS_SUBDIR = "attachments/"

EXTERNAL_FILES_SUBDIR = "external_files/"


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


class Message:
    def __init__(self, msg_id: str, message: mailbox.Message, external_images: ExternalImages) -> None:
        self.msg_id = msg_id
        self.message = message
        self.external_images = set(external_images[src] for src in external_images(msg_id))
        self.processed: Dict[str, Any] = {
            'id': self.msg_id,
            'Publish': 'false',
            'Comments': '',
        }

    def process(self) -> Optional[Dict[str, Any]]:
        """
        Process a single message and return as a dict.
        """
        # Extract the headers
        for header, value in self.message.items():
            # Decode and convert to str
            value = str(make_header(decode_header(value)))

            if header == 'Date':
                self.processed['Date'] = value
                logger.debug(f'date: {value}')

            elif header == 'From':
                # For now, ignore the messages which were forwarded manually from
                # lib-whpoolreports to lib-whpoolreports-service
                if 'lib-whpoolreports' in value:
                    return None

                self.processed['Reporter'] = process_reporter(value)

            elif header == 'Subject':
                self.processed['Title'] = scrub_title(value)

        # Process all parts and attachments
        self.processed['files'] = list(get_files(self.message))

        # Process the body content
        html = create_canonical_body_html(self.msg_id, self.processed['files'])
        self.processed['canonical_body_html'] = html
        self.processed['processed_body_html'] = scrub_body(html)

        # Replace <img> content ids with links to attachments
        # Updates processed['processed_body_html'], replacing
        # links to attachments (assumed to have the form "cid:<content id>")
        # with a link to the local copy of the file.
        for file in filter(lambda f: f.content_id, self.processed['files']):
            self.processed['processed_body_html'] = rewrite_attachment_path(file, self.processed['processed_body_html'])

        # Replace external image links with links to local copies
        # Updates processed['processed_body_html'], replacing
        # links to external images with a link to a local copy of the file.
        output_subdir = EXTERNAL_FILES_SUBDIR

        for file in self.external_images:
            self.processed['processed_body_html'] = rewrite_external_file_location(
                file,
                self.processed['processed_body_html'],
                output_subdir
            )

        # Determine whether message is a pool report
        # Sets the "PoolReport" entry in the given "processed" dictionary to
        # false" if the message is not a pool report.
        title = self.processed['Title']
        body = self.processed['processed_body_html']

        if is_pool_report(title) and is_pool_report(body):
            self.processed['PoolReport'] = 'true'
        else:
            self.processed['PoolReport'] = 'false'

        logger.debug(f"PoolReport={self.processed['PoolReport']}")

        return self.processed

    def write(self, writer: 'DictWriter[str]', output_dir: Path) -> None:
        """ Write out a single processed message. """

        # Write metadata to the CSV file
        writer.writerow(self.processed)

        # Add the "processed" HTML to the "processed" files list for output
        self.processed['files'].append(
            MessageFile('body-processed.html', self.processed['processed_body_html'].encode('UTF-8'))
        )

        # Create the directory for storing per message files
        message_dir = output_dir / f'{self.processed["id"]:03d}'

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

        for extract_file in self.processed['files']:
            filename = extract_file.filename
            extracted_bytes = extract_file.content
            output_subdir = extract_file.output_subdir

            logger.debug(f'Creating filename={filename}, size={len(extracted_bytes)}, output_subdir={output_subdir}')
            out_dir = message_dir / output_subdir
            if not out_dir.is_dir():
                # Make sure subdirectory exists
                os.mkdir(out_dir)

            with open(out_dir / filename, 'wb') as outfile:
                outfile.write(extracted_bytes)

        # Write the external files
        for external_image_file in self.external_images:
            filename = external_image_file.filename
            extracted_bytes = external_image_file.content
            output_subdir = EXTERNAL_FILES_SUBDIR

            logger.debug(
                f'Creating external file: filename={filename}, '
                f'size={len(extracted_bytes)}, output_subdir={output_subdir}'
            )

            out_dir = message_dir / output_subdir
            if not out_dir.is_dir():
                # Make sure subdirectory exists
                os.mkdir(out_dir)

            with open(out_dir / filename, 'wb') as outfile:
                outfile.write(extracted_bytes)


def is_pool_report(html: str) -> bool:
    """
    Returns True if the given HTML appears to be pool report, False
    otherwise.
    """
    for marker in NONPOOL_REPORT_MARKERS:
        if marker.search(html):
            return False

    return True


def get_files(message: mailbox.Message) -> Iterable[MessageFile]:
    """
    Iterate over each part of the message, and yield a MessageFile for each part.
    """
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
        if filename and content:
            yield MessageFile(filename, content, output_subdir, content_id)


def rewrite_attachment_path(file: MessageFile, body: str) -> str:
    content_id = file.content_id
    filename = file.filename
    output_subdir = file.output_subdir

    str_to_replace = f"cid:{content_id}"

    path = Path(filename)
    if output_subdir:
        path = Path(output_subdir) / filename
    replacement_str = str(path)

    body = body.replace(str_to_replace, replacement_str)

    logger.debug(f"Replaced {str_to_replace} with {replacement_str}")

    return body


def rewrite_external_file_location(file: ExternalImageFile, body: str, output_subdir: Optional[str] = None) -> str:
    path = Path(file.filename)
    if output_subdir:
        path = Path(output_subdir) / file.filename

    if file.src in body:
        logger.debug(f"Replacing '{file.src}' with '{path}'")
        return body.replace(file.src, str(path))
    else:
        logger.warning(f"Expected to find '{file.src}' but it was not found.")
        # return the body as-is
        return body


body_scrub = [
    '''-- \nTo unsubscribe from this group and stop receiving emails from it, send an email to all+unsubscribe@whpoolreports.com.''',  # noqa
    '''-- <br />\nTo unsubscribe from this group and stop receiving emails from it, send an email to <a href="mailto:all+unsubscribe@whpoolreports.com">all+unsubscribe@whpoolreports.com</a>.<br />''',  # noqa
]

p_charset = re.compile(r'charset=[a-zA-Z0-9-]+')


def create_canonical_body_html(msg_id: str, files: Sequence[MessageFile]) -> str:
    # Populates the given "processed" object with two additional fields:
    #   * canonical_body_html - representing with original HTML the body,
    #                           or the HTML-ized version of the text.
    #   * processed_body_html - Initially the same as "canonical_body_html"
    #                           but changed into the final HTML by the
    #                           various filters

    # Extract the body
    html, text = None, None
    for file in files:
        if file.filename == 'body.html':
            html = file.content.decode('UTF-8')
        elif file.filename == 'body.txt':
            text = file.content.decode('UTF-8')

    # Use the text version if HTML is not available
    if not html:
        if not text:
            m = f'Unable to find message body for message {msg_id}'
            logger.warning(m)
            text = ""

        html = f"<html><body><pre>{text}</pre></body></html>"

    return html


def scrub_body(html: str) -> str:
    # Scrub specific string values
    for scrub in body_scrub:
        if scrub in html:
            html = html.replace(scrub, '')
            logger.debug(f'body: scrubbed "{scrub}"')

    # Update the charset since we have convert to utf-8
    html = p_charset.sub("charset=utf-8", html)

    return html


title_scrub = [
    '[WH Pool] ',
    '\n',
]


def scrub_title(value: str) -> str:
    """
    Build the Title field from the message Subject header.
    """
    logger.debug(f'title: Subject={value}')

    for scrub in title_scrub:
        if scrub in value:
            value = value.replace(scrub, '')
            logger.debug(f'title: scrubbed "{scrub}": {value}')

    # escape any backslashes and pipe characters
    value = re.sub(r'([\\|])', r'\\\1', value)

    return value


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
