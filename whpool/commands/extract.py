import logging
import mailbox
from csv import DictWriter
from pathlib import Path

import click

from whpool.core.external_images import retrieve_external_images
from whpool.extract.extract import HEADERS, Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command(help='Extract pool report emails from mbox format file and create '
                    'an output format suitable for curatorial review.')
@click.option(
    '--input', '-i', 'input_filename',
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help='Input mbox format email file.'
)
@click.option(
    '--output', '-o', 'output_dirname',
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help='Output directory which must already exist; files and sub-directories '
         'will be created or overwritten as necessary.'
)
@click.option(
    '-v', '--verbose', 'verbosity',
    count=True,
    help='Produce verbose logging output.'
)
def extract(input_filename: str, output_dirname: str, verbosity: int) -> None:
    # Setup logging
    logging.basicConfig()

    if verbosity == 0:
        logging.getLogger("whpool").setLevel(logging.WARN)
    elif verbosity == 1:
        logging.getLogger("whpool").setLevel(logging.INFO)
    elif verbosity == 2:
        logging.getLogger("whpool").setLevel(logging.DEBUG)

    logger.debug(f'{input_filename=}')
    logger.debug(f'{output_dirname=}')
    logger.debug(f'{verbosity=}')

    # Read the mbox file (slurp all into memory)
    box = mailbox.mbox(input_filename)

    # Retrieve external images
    external_images = retrieve_external_images(box)

    output_path = Path(output_dirname)

    # Open the output CSV for writing
    with open(output_path/'whpool.csv', 'w') as csv_file:
        csv_writer = DictWriter(csv_file, fieldnames=HEADERS, extrasaction='ignore')

        # Add the headers
        csv_writer.writeheader()

        # Iterate over messages in the mbox file
        for msg_id, msg in box.iteritems():

            logger.debug(f'Processing message {msg_id}')

            # Process a single message
            message = Message(msg_id, msg, external_images)
            processed = message.process()

            if processed:
                logger.debug(f'Writing message {msg_id}')

                # Write out the message
                message.write(csv_writer, output_path)
