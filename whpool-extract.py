#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
import csv
from email.header import make_header, decode_header
import logging
import mailbox
import os
from pathlib import Path
import re
import sys

# Extract pool reports (email) from mbox format file and create an output
# format suitable for curatorial review.

logger = logging.getLogger('whpool-extract')


def get_args():
    """ Create parsers and return a namespace object. """
    parser = ArgumentParser()

    parser.add_argument(
        '-i', '--input',
        required=True,
        help="Input mbox format email file",
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help="Output directory which must already exist; files and" +
        "sub-directories will be created or overwritten as necessary.",
    )

    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        default=1,
        choices=[0, 1, 2],
        help="verbosity of logging output; default is 1")

    return parser.parse_args()


def process_message(id, message):
    """ Process a single message and return as a dict. """

    processed = {'id': id}

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
            processed['Title'] = process_title(value)

    processed['files'] = []

    # Iterate over each part of the message
    for part in message.walk():
        content_type = part.get_content_type()
        filename = part.get_filename()

        logger.debug(f'attachment: {content_type=}')
        logger.debug(f'attachment: {filename=}')

        # Assert that this won't happen
        if filename in ('body.html', 'body.txt', 'body-redacted.html'):
            logger.error(f'filename conflict: {filename}')
            return None

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
                else:
                    filename = 'body.html'

        elif filename:
            bytes = part.get_payload(decode=True)

        # Anything we want to save now has a filename and bytes to store
        if filename:
            processed['files'].append((filename, bytes))

    return processed


title_scrub = [
    '[WH Pool] ',
]


def process_title(value):
    """ Build the Title field from the message Subject header. """

    logger.debug(f'title: Subject={value}')

    for scrub in title_scrub:
        if scrub in value:
            value = value.replace(scrub, '')
            logger.debug(f'title: scrubbed "{scrub}": {value}')

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


def process_reporter(value):
    """ Build the Reporter field from the message From header. """

    logger.debug(f'reporter: From={value}')

    for scrub in reporter_scrub:
        if scrub in value:
            value = value.replace(scrub, '')
            logger.debug(f'reporter: scrubbed "{scrub}": {value}')

    if m := reporter_extract.match(value):
        value = m.group(1)
        logger.debug(f'reporter: extracted: {value}')

    return value


def write_message(id, processed, csvwriter, outdir):
    """ Write out a single processed message. """

    # Write metadata to the CSV file
    csvwriter.writerow(
        [processed['id'],
         processed['Date'],
         processed['Reporter'],
         processed['Title'],
         ]
    )

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
    for filename, bytes in processed['files']:
        logger.debug(f'Creating {filename=}, size={len(bytes)}')
        with open(mdir / filename, 'wb') as outfile:
            outfile.write(bytes)


def main():
    """ Main processing loop. """

    args = get_args()

    # Setup logging
    logging.basicConfig()

    if args.verbosity == 0:
        logger.setLevel(logging.WARN)
    elif args.verbosity == 2:
        logger.setLevel(logging.DEBUG)

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

    # Open the output CSV for writing
    with open(outdir/'whpool.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Add the headers
        csvwriter.writerow(['id', 'Date', 'Reporter', 'Title'])

        # Iterate over messages in the mbox file
        for id, message in box.iteritems():

            # Process a single message
            processed = process_message(id, message)

            if processed:
                # Write out the message
                write_message(id, processed, csvwriter, outdir)


if __name__ == "__main__":
    main()
