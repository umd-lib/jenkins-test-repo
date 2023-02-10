"""Download an mbox file for the previous month."""

import logging
import mailbox
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import click
from dotenv import load_dotenv  # pip install python-dotenv
from codetiming import Timer

from whpool import VERSION
from whpool.core.capture_imap import MailServerHandler

logger = logging.getLogger(__name__)

# get configs
load_dotenv()
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')

PREVIOUS_MONTH = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

path = None
output_dirname = None


def download_messages(mailserver, mbox_file_path):
    """Download messages for the previous month as an mbox file."""

    folder = PREVIOUS_MONTH
    filename = mbox_file_path

    mbox = mailbox.mbox(filename, factory=None, create=True)
    mbox.clear()
    mbox.lock()
    # Select a mailbox folder
    mailserver.select(f'"{folder}"', readonly=True)
    logger.info(f'Fetching mailbox folder: {PREVIOUS_MONTH}')
    # Search for emails in the selected mailbox
    search_criteria = 'ALL'
    charset = None  # All
    response_code, message_numbers_raw = mailserver.search(charset, search_criteria)
    logger.info(f'Search response: {response_code}')
    logger.debug(f'Message numbers: {message_numbers_raw}')
    message_numbers = message_numbers_raw[0].split()
    for n, message_number in enumerate(message_numbers):
        typ, data = mailserver.fetch(message_number, "RFC822")
        assert typ == "OK"
        for encoding in ["utf-8", "latin1"]:
            try:
                text = data[0][1].decode(encoding)
            except UnicodeDecodeError:
                text = None
        if text is None:
            text = data[0][1].decode("utf-8", "backslashreplace")
        text = text.strip().replace("\r", "")
        mbox.add(text.encode())
        logger.info(f'Downloading message {n} of {len(message_numbers)}')
    mbox.flush()
    mbox.unlock()
    mailserver.close()


def compare_message_counts(mailserver, mbox_file_path):
    """Compare message counts of mailbox folder and downloaded mbox file."""

    # Get message count for previous month
    directory_name = PREVIOUS_MONTH
    response_code, mail_count = mailserver.select(mailbox=directory_name, readonly=True)
    logger.info(f'Response Code For Select: {response_code}')
    directory_message_count = {directory_name: mail_count[0].decode()}
    logger.info(f'Message count for {directory_name}: {directory_message_count[directory_name]}')

    mbox = mailbox.mbox(mbox_file_path)
    mbox_message_count = {'messages': 0}
    for item in mbox.iteritems():
        mbox_message_count['messages'] += 1
        message = {'i': item}
        logger.debug(f'{message}')
    logger.info('Comparing message counts...')
    logger.info(f'mbox total message count  : {mbox_message_count["messages"]}')
    logger.info(f'Folder total message count: {directory_message_count[directory_name]}')
    mbox_messages = str(mbox_message_count['messages'])
    mailbox_messages = str(directory_message_count[directory_name])
    match = mbox_messages == mailbox_messages
    logger.info(f'Message count matches: {match}')


def set_path(output_dirname):
    """ Set path """

    if output_dirname is None:
        path = Path.cwd() / 'data_mbox'
    elif output_dirname is not None:
        path = Path(output_dirname)

    path.mkdir(parents=True, exist_ok=True)
    mbox_file_path = path / f'{PREVIOUS_MONTH}.mbox'
    return mbox_file_path


@click.command(help='Fetch messages in mbox format from mailbox folders.')
@click.version_option(VERSION, '--version', '-V', prog_name='whpool')
@click.option(
    '--output', '-o', 'output_dirname',
    type=click.Path(),
    default=output_dirname,
    help='''If the output_dirname is specified, the mbox file will be downloaded to that location.
            Otherwise, the file will be saved in ./data_mbox'''
)
@Timer(name="fetch", logger=logging.info)
def main(output_dirname) -> None:
    """Download an mbox file for the previous month."""

    logger.info(f'whpool version {VERSION}')
    logger.info(f'{__name__}')
    logger.info(f'Date: {datetime.now()}')

    # Set path
    mbox_file_path = set_path(output_dirname)

    start_time = time.time()

    mailserver_handler = MailServerHandler()
    mailserver_handler.connect(host=host, port=port)
    mailserver_handler.login(user=user, password=password)

    download_messages(mailserver_handler.mailserver, mbox_file_path)
    compare_message_counts(mailserver_handler.mailserver, mbox_file_path)

    mailserver_handler.logout()

    stop_time = time.time()
    logger.info(f'Process time (secs): {round(stop_time - start_time, 2)}')


if __name__ == '__main__':
    main()
