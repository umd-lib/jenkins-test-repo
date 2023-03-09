"""Download an mbox file for the previous month."""

import logging
import mailbox
import os
from datetime import datetime, timedelta
from pathlib import Path

import click
from codetiming import Timer
from dotenv import load_dotenv

from whpool.core.capture_imap import MailServerHandler

logger = logging.getLogger(__name__)

# get configs
load_dotenv()
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')


class Folder:
    def __init__(self, mailserver, folder_name, output_dirname=None):
        self.mailserver = mailserver
        self.folder_name = folder_name
        if output_dirname is None:
            path = Path.cwd() / 'data_mbox'
        else:
            path = Path(output_dirname)

        self.mbox_path = path / f'{folder_name}.mbox'

    def download_messages(self):
        self.mbox_path.parent.mkdir(parents=True, exist_ok=True)
        mbox = mailbox.mbox(self.mbox_path, factory=None, create=True)
        mbox.clear()
        mbox.lock()
        # Select a mailbox folder
        self.mailserver.select(f'"{self.folder_name}"', readonly=True)
        logger.info(f'Fetching mailbox folder {self.folder_name} to {self.mbox_path}')
        # Search for emails in the selected mailbox
        search_criteria = 'ALL'
        charset = None  # All
        response_code, message_numbers_raw = self.mailserver.search(charset, search_criteria)
        logger.info(f'Search response: {response_code}')
        logger.debug(f'Message numbers: {message_numbers_raw}')
        message_numbers = message_numbers_raw[0].split()
        for n, message_number in enumerate(message_numbers, 1):
            typ, data = self.mailserver.fetch(message_number, "RFC822")
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
        self.mailserver.close()

    def compare_message_counts(self):
        """Compare message counts of mailbox folder and downloaded mbox file."""

        # Get message count for this folder
        response_code, mail_count = self.mailserver.select(mailbox=self.folder_name, readonly=True)
        logger.info(f'Response Code For Select: {response_code}')
        directory_message_count = {self.folder_name: mail_count[0].decode()}
        logger.info(f'Message count for {self.folder_name}: {directory_message_count[self.folder_name]}')

        mbox = mailbox.mbox(self.mbox_path)
        mbox_message_count = {'messages': 0}
        for item in mbox.iteritems():
            mbox_message_count['messages'] += 1
            message = {'i': item}
            logger.debug(f'{message}')
        logger.info('Comparing message counts...')
        logger.info(f'mbox total message count  : {mbox_message_count["messages"]}')
        logger.info(f'Folder total message count: {directory_message_count[self.folder_name]}')
        mbox_messages = str(mbox_message_count['messages'])
        mailbox_messages = str(directory_message_count[self.folder_name])
        match = mbox_messages == mailbox_messages
        logger.info(f'Message count matches: {match}')


@click.command(help='Fetch messages in mbox format from mailbox folders.')
@click.option(
    '--output', '-o', 'output_dirname',
    type=click.Path(),
    help='''If the output_dirname is specified, the mbox file will be downloaded to that location.
            Otherwise, the file will be saved in ./data_mbox'''
)
@click.argument(
    'folder_names',
    nargs=-1,
)
@Timer(name="fetch", logger=logger.info)
def fetch(output_dirname, folder_names) -> None:
    """Download an mbox file for each of the given folders."""
    logger.info(f'{__name__}')
    logger.info(f'Date: {datetime.now()}')

    if len(folder_names) == 0:
        previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        logger.debug(f'No folders given, defaulting to "{previous_month}"')
        folder_names = (previous_month,)

    mailserver_handler = MailServerHandler()
    mailserver_handler.connect(host=host, port=port)
    mailserver_handler.login(user=user, password=password)

    for folder_name in folder_names:
        folder = Folder(mailserver_handler.mailserver, folder_name, output_dirname)
        folder.download_messages()
        folder.compare_message_counts()

    mailserver_handler.logout()
