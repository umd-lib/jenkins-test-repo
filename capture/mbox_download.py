"""Download an mbox file for the previous month."""

import os
import time
from datetime import datetime
import imaplib
import mailbox
import logging

from dotenv import load_dotenv
from capture_imap import login, logout

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

load_dotenv()
user = os.environ.get("user", "default")
password = os.environ.get("password", "default")

HOST = "imap.gmail.com"
PORT = imaplib.IMAP4_SSL_PORT
mailserver = imaplib.IMAP4_SSL(HOST, PORT)

current_date = datetime.now()
month, year = (current_date.month-1, current_date.year) if current_date.month != 1 else (12, current_date.year-1)
PREVIOUS_MONTH = str(current_date.replace(month=month, year=year))[0:7]

mbox_file_path = os.path.join('./', PREVIOUS_MONTH + '.mbox')


def check_for_mbox_file():
    """Check if mbox file exists for prior month."""

    print('Checking for mbox file:', mbox_file_path)
    is_file = os.path.isfile(mbox_file_path)
    print('mbox file exists:', is_file)


def download_messages():
    """Download messages for the previous month as an mbox file."""

    folder = PREVIOUS_MONTH
    filename = mbox_file_path
    # factory = email.message_from_binary_file(folder, policy=email.policy.default)
    mbox = mailbox.mbox(filename, factory=None)
    mbox.lock()
    # Select a mailbox folder
    mailserver.select(f'"{folder}"', readonly=True)
    print('\nFetching mailbox folder:', PREVIOUS_MONTH)
    # Search for emails in the selected mailbox
    search_criteria = 'ALL'
    charset = None  # All
    respose_code, message_numbers_raw = mailserver.search(charset, search_criteria)
    print(f'Search response: {respose_code}')
    # print(f'Message numbers: {message_numbers_raw}')
    message_numbers = message_numbers_raw[0].split()
    for message_number in message_numbers:
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
    mbox.flush()
    mbox.unlock()
    mailserver.close()


def compare_message_counts():
    """Compare message counts of mailbox folder and downloaded mbox file."""

    # Get message count for previous month
    directory_name = PREVIOUS_MONTH
    response_code, mail_count = mailserver.select(mailbox=directory_name, readonly=True)
    print(f'Response Code For Select: {response_code}')
    directory_message_count = {directory_name: mail_count[0].decode()}
    print('Message count for', directory_name, ':', directory_message_count[directory_name])

    mbox = mailbox.mbox(mbox_file_path)
    mbox_message_count = {'messages': 0}
    for item in mbox.iteritems():
        mbox_message_count['messages'] += 1
        message = {'i': item}
        print(message)
    print('\nComparing message counts...')
    print('mbox total message count  :', mbox_message_count['messages'])
    print('Folder total message count:', directory_message_count[directory_name])
    mbox_messages = str(mbox_message_count['messages'])
    mailbox_messages = str(directory_message_count[directory_name])
    match = mbox_messages == mailbox_messages
    print('Message count matches     :', match)


def main():
    """Download an mbox file for the previous month."""

    start_time = time.time()
    print('Date              :', current_date)
    login(mailserver, user, password)

    check_for_mbox_file()

    if os.path.exists(mbox_file_path):
        os.remove(mbox_file_path)
    else:
        pass

    download_messages()

    compare_message_counts()

    if not os.path.exists('data_mbox'):
        os.mkdir('data_mbox')
    else:
        pass

    if os.path.exists(mbox_file_path) and not os.path.exists('data_mbox/' + PREVIOUS_MONTH + '.mbox'):
        os.replace(mbox_file_path, 'data_mbox/' + PREVIOUS_MONTH + '.mbox')
    else:
        os.remove(mbox_file_path)

    logout(mailserver)

    stop_time = time.time()
    print('\nProcess time (secs):', round(stop_time - start_time, 2))


if __name__ == '__main__':
    main()
