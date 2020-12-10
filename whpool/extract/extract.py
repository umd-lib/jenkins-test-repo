import argparse
from collections import namedtuple
import csv
import _csv  # For mypy typing
from email.header import make_header, decode_header
import logging
import mailbox
import os
from pathlib import Path
import re
import sys
from whpool.core.external_images import ExternalImages
from whpool.core.external_images import retrieve_external_images
from whpool.core.message_file import MessageFile
from whpool.core.command import CommandResult
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

HEADERS = ['id', 'Date', 'Reporter', 'Title', 'PoolReport', 'Publish',
           'Comments']

OUTPUT_ATTACHMENTS_SUBDIR = "attachments/"

EXTERNAL_FILES_SUBDIR = "external_files/"


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
        '''
        Returns True if the given HTML appears to be pool report, False
        otherwise.
        '''

        for marker in PoolReport.NONPOOL_REPORT_MARKERS:
            if marker.search(html):
                return False

        return True

    @staticmethod
    def process_pool_report(processed: Dict[str, Any]) -> None:
        '''
        Sets the "PoolReport" entry in the given "processed" dictionary to
        "false" if the message is not a pool report.
        '''
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
        filename = external_images.get_file(src).filename

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
            logger.warn(f"Expected '{str_to_replace}' in message {msg_id}, but it was not found.")


def process_message(id: str, message: mailbox.Message, external_images: ExternalImages) -> Optional[Dict[str, Any]]:
    """ Process a single message and return as a dict. """

    processed = {
        'id': id,
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

        bytes = None
        content_id = ''

        if content_type in ('text/plain', 'text/html'):
            # Decode and convert back to UTF-8 bytes
            bytes = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if charset is None:
                charset = 'UTF-8'
            string = bytes.decode(charset)
            bytes = string.encode('UTF-8')

            if not filename:
                # Likely a body part
                if content_type == 'text/plain':
                    filename = 'body.txt'
                    output_subdir = ''
                else:
                    filename = 'body.html'
                    output_subdir = ''

        elif filename:
            bytes = part.get_payload(decode=True)
            content_id = part['Content-ID']
            if content_id:
                # Strip off starting "<" and ending ">"
                content_id = content_id.replace("<", "").replace(">", "")

        # Anything we want to save now has a filename and bytes to store
        if filename:
            processed['files'].append(MessageFile(filename, bytes, output_subdir, content_id))


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
    id: str, processed: Dict[str, Any], csvwriter: '_csv._writer',
        outdir: Path, external_images: ExternalImages) -> None:
    """ Write out a single processed message. """

    # Write metadata to the CSV file
    csvwriter.writerow(
        [processed['id'],
         processed['Date'],
         processed['Reporter'],
         processed['Title'],
         processed['PoolReport'],
         processed['Publish'],
         processed['Comments'],
         ]
    )

    # Add the "processed" HTML to the "processed" files list for output
    processed['files'].append(MessageFile('body-processed.html', processed['processed_body_html'].encode('UTF-8')))

    # Redact and add the "body-redacted.html" to the "processed" files list
    # for output
    processed['processed_body_redacted_html'] = Redact.redact(processed['processed_body_html'])
    processed['files'].append(MessageFile('body-processed-redacted.html',
                                          processed['processed_body_redacted_html'].encode('UTF-8')))

    # Create the directory for storing per message files
    mdir = outdir / f'{processed["id"]:03d}'

    logger.debug(f'message directory: {mdir}')

    if not mdir.is_dir():
        try:
            os.mkdir(mdir)
        except OSError as e:
            logger.error(f'Error creating {mdir}: {e}')
            return
        else:
            logger.debug(f'created {mdir}')

    # Create the files

    for extract_file in processed['files']:
        filename = extract_file.filename
        bytes = extract_file.bytes
        output_subdir = extract_file.output_subdir

        logger.debug(f'Creating filename={filename}, size={len(bytes)}, output_subdir={output_subdir}')
        out_dir = mdir / output_subdir
        if not out_dir.is_dir():
            # Make sure subdirectory exists
            os.mkdir(out_dir)

        with open(out_dir / filename, 'wb') as outfile:
            outfile.write(bytes)

    # Write the external files
    for src in external_images.srcs(id):
        external_image_file = external_images.get_file(src)
        filename = external_image_file.filename
        bytes = external_image_file.bytes
        output_subdir = EXTERNAL_FILES_SUBDIR

        logger.debug(f'Creating external file: filename={filename}, size={len(bytes)}, output_subdir={output_subdir}')

        out_dir = mdir / output_subdir
        if not out_dir.is_dir():
            # Make sure subdirectory exists
            os.mkdir(out_dir)

        with open(out_dir / filename, 'wb') as outfile:
            outfile.write(bytes)


def run_command(args: argparse.Namespace) -> CommandResult:
    """ Main processing loop. """

    # Setup logging
    logging.basicConfig()

    if args.verbosity == 0:
        logging.getLogger("whpool").setLevel(logging.WARN)
    elif args.verbosity == 1:
        logging.getLogger("whpool").setLevel(logging.INFO)
    elif args.verbosity == 2:
        logging.getLogger("whpool").setLevel(logging.DEBUG)

    logger.debug(f'{args.input=}')
    logger.debug(f'{args.output=}')
    logger.debug(f'{args.verbosity=}')

    # Ensure the output directory exists and is writable
    outdir = Path(args.output)

    if not outdir.exists():
        logger.error(f'Output "{outdir}" does not exist')
        sys.exit(1)

    if not outdir.is_dir():
        logger.error(f'Output "{outdir}" is not a directory')
        sys.exit(1)

    if not os.access(outdir, os.W_OK):
        logger.error(f'Output directory {outdir} is not writable')
        sys.exit(1)

    # Read the mbox file (slurp all into memory)
    box = mailbox.mbox(args.input)

    # Retrieve external images
    external_images = retrieve_external_images(box)

    # Open the output CSV for writing
    with open(outdir/'whpool.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Add the headers
        csvwriter.writerow(HEADERS)

        # Iterate over messages in the mbox file
        for id, message in box.iteritems():

            logger.debug(f'Processing message {id}')

            # Process a single message
            processed = process_message(id, message, external_images)

            if processed:
                logger.debug(f'Writing message {id}')

                # Write out the message
                write_message(id, processed, csvwriter, outdir, external_images)

    return CommandResult(True, [])
