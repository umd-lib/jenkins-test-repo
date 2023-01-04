import os
import imaplib
import mailbox
import email
from email.header import decode_header
from email.message import EmailMessage
import time
from datetime import datetime
import sys
from termcolor import cprint
import logging


class Capture():

    def login(user, password):
        start = time.time()
        global mailserver

        try:
            mailserver = imaplib.IMAP4_SSL(host="imap.gmail.com", port=imaplib.IMAP4_SSL_PORT)
        except Exception as e:
            cprint('ErrorType : {}, Error : {}'.format(type(e).__name__, e), 'red')
            mailserver = None
            sys.exit()

        print('Connection Object : {}'.format(mailserver))
        print('Time to Connect   : {:,.2f} Seconds'.format(time.time() - start))
        print('\nLogging into mailbox...')

        try:
            response_code, response = mailserver.login(user, password)
        except Exception as e:
            cprint('ErrorType : {}, Error : {}'.format(type(e).__name__, e), 'red')
            response_code, response = None, None
            sys.exit()

        print(f'Response Code : {response_code}')
        print(f'Response      : {response[0].decode()}')

    def check(previous_month):
        global directory_name
        global directory_message_count

        directory_name = previous_month

        response_code, mail_count = mailserver.select(mailbox=directory_name, readonly=True)
        directory_message_count = {directory_name: mail_count[0].decode()}
        print('Message count for', directory_name, ':', directory_message_count[directory_name])

    def logout():
        print('\nLogging Out....')

        try:
            response_code, response = mailserver.logout()
        except Exception as e:
            cprint(f'ErrorType : {type(e).__name__}, Error : {e}', 'red')
            response_code, response = None, None

        print(f'Response Code : {response_code}')
        print(f'Response      : {response[0].decode()}')

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
        mailserver.select('"{}"'.format(folder), readonly=True)
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

    def sort_messages():

        resp_code, messages = mailserver.select(mailbox='INBOX', readonly=False)

        # Retrieve Mail IDs for given Directory  
        resp_code, messages = mailserver.search(None, "ALL")

        # print("Mail IDs : {}\n".format(messages[0].decode().split()))

        mail_ids = messages[0].decode().split()

        for mail_id in mail_ids:
            resp_code, mail_data = mailserver.fetch(mail_id, '(RFC822)')

            message = email.message_from_bytes(mail_data[0][1])
            message_date = (message.get("Date"))[:-6]
            date_in_utc_iso = datetime.strptime(message_date, '%a, %d %b %Y %H:%M:%S').isoformat() + 'Z'
            message_year_month = str(date_in_utc_iso[:7])

            print(mail_id, message_year_month)
            folder_exists = (mailserver.list('"' + message_year_month + '"'))
            print(folder_exists)
            # print(folder_exists != ('OK', [None]))

            if folder_exists != ('OK', [None]):
                print('Copy', mail_id, 'to', message_year_month, 'folder')
                mailserver.copy(mail_id, message_year_month)  # To move: copy, delete, expunge
                resp_code, response = mailserver.store(mail_id, '+FLAGS', '\\Deleted')  # Setting Delete Flag
                print(f'Response Code : {resp_code}')
                print(f'Response      : {response[0].decode()}\n')
            else:
                mailserver.create(mailbox=message_year_month)
                print('The folder', message_year_month, 'does not exist. Creating folder.')
                print('Copy', mail_id, 'to', message_year_month, 'folder')
                mailserver.copy(mail_id, message_year_month)  # To move: copy, delete, expunge
                resp_code, response = mailserver.store(mail_id, '+FLAGS', '\\Deleted')  # Setting Delete Flag
                print(f'Response Code : {resp_code}')
                print(f'Response      : {response[0].decode()}\n')

        resp_code, response = mailserver.expunge()
        print(f'Response Code : {resp_code}')
        print(f'Response      : {response[0].decode() if response[0] else None}\n')

        mailserver.close()

    def sort_with_uid():
        # WIP change to uid
        # resp_code, mail_data = mailserver.uid('fetch', mail_id, '(RFC822)')
        pass
