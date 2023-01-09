import os
import time
from datetime import datetime
import imaplib
import mailbox
import email
from dotenv import load_dotenv
import logging

from captureModule import login, logout

mailserver = imaplib.IMAP4_SSL(host="imap.gmail.com", port=imaplib.IMAP4_SSL_PORT)

def check(previous_month, mailserver):
    global directory_name
    global directory_message_count
    directory_name = previous_month
    response_code, mail_count = mailserver.select(mailbox=directory_name, readonly=True)
    directory_message_count = {directory_name: mail_count[0].decode()}
    print('Message count for', directory_name, ':', directory_message_count[directory_name])

def check_for_mbox_file(previous_month):
    global mbox_file_path
    # Check if mbox file already exists for prior month
    mbox_file_path = os.path.join('./', previous_month+'.mbox')
    print('Checking for mbox file:', mbox_file_path)
    isFile = os.path.isfile(mbox_file_path)
    print('mbox file exists:', isFile)

def download_messages(previous_month):
    folder = previous_month
    filename = mbox_file_path
    # factory = email.message_from_binary_file(folder, policy=email.policy.default)
    mbox = mailbox.mbox(filename, factory=None)
    mbox.lock()
    # Select a mailbox folder
    mailserver.select(f'"{folder}"', readonly=True)
    print('\nFetching mailbox folder:', previous_month)
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
    # Compare the mbox file messages to the mailbox folder messages
    mbox = mailbox.mbox(mbox_file_path)
    mbox_message_count = {'messages': 0}
    for n in mbox.iteritems():
        mbox_message_count['messages'] += 1
        message = {'n': n}
    print('\nComparing message counts...')
    print('mbox total message count  :', mbox_message_count['messages'])
    print('Folder total message count:', directory_message_count[directory_name])
    a = str(mbox_message_count['messages'])
    b = str(directory_message_count[directory_name])
    match = a == b
    print('Message count matches     :', match)

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    load_dotenv()
    user = os.environ.get("user", "default")
    password = os.environ.get("password", "default")

    current_date = datetime.now()
    month, year = (current_date.month-1, current_date.year) if current_date.month != 1 else (12, current_date.year-1)
    previous_month = str(current_date.replace(month=month, year=year))[0:7]
    mbox_file_path = os.path.join('./', previous_month+'.mbox')

    start_time = time.time()
    print('Date              :', current_date)
    login(mailserver, user, password)
    check(previous_month, mailserver)
    check_for_mbox_file(previous_month)

    if os.path.exists(mbox_file_path):
        os.remove(mbox_file_path)
    else:
        pass

    download_messages(previous_month)

    compare_message_counts()

    if not os.path.exists('data_mbox'):
        os.mkdir('data_mbox')
    else:
        pass

    if os.path.exists(mbox_file_path) and not os.path.exists('data_mbox/' + previous_month + '.mbox'):
        os.replace(mbox_file_path, 'data_mbox/' + previous_month + '.mbox')
    else:
        os.remove(mbox_file_path)


    logout(mailserver)

    stop_time = time.time()
    print('\nProcess time (secs):', round(stop_time - start_time, 2))


if __name__ == '__main__':
    main()
