"""Download an mbox file for the previous month."""

import logging
import mailbox
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv  # pip install python-dotenv

from capture_imap import MailServerHandler

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# get configs
load_dotenv()
<<<<<<< HEAD
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
=======
user = os.environ.get("user", "default")
password = os.environ.get("password", "default")

host = "imap.gmail.com"
port = imaplib.IMAP4_SSL_PORT
>>>>>>> 0f94475 (Refactored mailserver)

PREVIOUS_MONTH = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

path = Path.cwd() / 'data_mbox'
path.mkdir(parents=True, exist_ok=True)
mbox_file_path = path.joinpath(PREVIOUS_MONTH + '.mbox')


def download_messages(mailserver):
    """Download messages for the previous month as an mbox file."""

    folder = PREVIOUS_MONTH
    filename = mbox_file_path

    mbox = mailbox.mbox(filename, factory=None, create=True)
    mbox.clear()
    mbox.lock()
    # Select a mailbox folder
    mailserver.select(f'"{folder}"', readonly=True)
    logging.info(f'Fetching mailbox folder: {PREVIOUS_MONTH}')
    # Search for emails in the selected mailbox
    search_criteria = 'ALL'
    charset = None  # All
    response_code, message_numbers_raw = mailserver.search(charset, search_criteria)
    logging.info(f'Search response: {response_code}')
    logging.debug(f'Message numbers: {message_numbers_raw}')
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
        logging.info(f'Downloading message {n} of {len(message_numbers)}')
    mbox.flush()
    mbox.unlock()
    mailserver.close()


def compare_message_counts(mailserver):
    """Compare message counts of mailbox folder and downloaded mbox file."""

    # Get message count for previous month
    directory_name = PREVIOUS_MONTH
    response_code, mail_count = mailserver.select(mailbox=directory_name, readonly=True)
    logging.info(f'Response Code For Select: {response_code}')
    directory_message_count = {directory_name: mail_count[0].decode()}
    logging.info(f'Message count for {directory_name}: {directory_message_count[directory_name]}')

    mbox = mailbox.mbox(mbox_file_path)
    mbox_message_count = {'messages': 0}
    for item in mbox.iteritems():
        mbox_message_count['messages'] += 1
        message = {'i': item}
        logging.debug(f'{message}')
    logging.info('Comparing message counts...')
    logging.info(f'mbox total message count  : {mbox_message_count["messages"]}')
    logging.info(f'Folder total message count: {directory_message_count[directory_name]}')
    mbox_messages = str(mbox_message_count['messages'])
    mailbox_messages = str(directory_message_count[directory_name])
    match = mbox_messages == mailbox_messages
    logging.info(f'Message count matches: {match}')


def main():
    """Download an mbox file for the previous month."""

    start_time = time.time()
    logging.info(f'Date: {datetime.now()}')

<<<<<<< HEAD
    mailserver_handler = MailServerHandler()
    mailserver_handler.connect(host=host, port=port)
    mailserver_handler.login(user=user, password=password)

    download_messages(mailserver_handler.mailserver)
    compare_message_counts(mailserver_handler.mailserver)

    mailserver_handler.logout()
=======
    mailserver = MailServerHandler.connect(host=host, port=port)
    MailServerHandler.login(mailserver, user=user, password=password)

    download_messages(mailserver)
    compare_message_counts(mailserver)

    MailServerHandler.logout(mailserver)
>>>>>>> 0f94475 (Refactored mailserver)

    stop_time = time.time()
    logging.info(f'Process time (secs): {round(stop_time - start_time, 2)}')


if __name__ == '__main__':
    main()
