"""Sort messages from Inbox to yyyy-mm folders."""

import os
import time
import imaplib
import email
from datetime import datetime
import logging

from dotenv import load_dotenv  # pip install python-dotenv

from capture_imap import login, logout

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# store user and password in another file
load_dotenv()
user = os.environ.get("user", "default")
password = os.environ.get("password", "default")

HOST = "imap.gmail.com"
PORT = imaplib.IMAP4_SSL_PORT
mailserver = imaplib.IMAP4_SSL(HOST, PORT)

# Create a folder list in order to remove Inbox flags
folder_list = []


def sort_with_uid(folder_list):
    """Copy messages to their respective yyyy-mm folders."""

    response_code = mailserver.select(mailbox='INBOX', readonly=False)
    logging.info(f'Select Inbox response Code: {response_code}')

    uids = mailserver.uid('SEARCH', 'ALL')
    logging.debug(f'{uids}')
    uid_list = uids[1][0].split()
    logging.debug(uid_list)
    for uid in uid_list:
        response, mail_data = mailserver.uid('FETCH', uid, '(RFC822)')
        logging.debug(f'Response For Fetch: {response}')
        message = email.message_from_bytes(mail_data[0][1])
        message_date = (message.get("Date"))[:-6]
        date_in_utc_iso = email.utils.parsedate_to_datetime(message_date)
        message_year_month = (str(date_in_utc_iso))[:7]
        logging.debug(f'{message_year_month}')

        folder_list.append(message_year_month)

        folder_exists = (mailserver.list('"' + message_year_month + '"'))
        logging.debug(f'{folder_exists}')
        # If there is no folder, then IMAP will return the response code OK and a None value.
        if folder_exists != ('OK', [None]):
            logging.debug(f'The folder {message_year_month} exists.')
        else:
            mailserver.create(mailbox=message_year_month)
            mailserver.subscribe(mailbox=message_year_month)
            logging.debug(f'The folder {message_year_month} does not exist. Creating folder.')
        logging.info(f'Copying {uid} to {message_year_month} folder')
        mailserver.uid('COPY', uid, message_year_month)
    mailserver.close()
    return folder_list


def remove_inbox_flag(folder_list):
    """Remove Inbox label.
    Normally, using uid('STORE', uid, '+FLAGS', '\\Deleted')
    would remove messages in the Inbox, however this does not work
    with Gmail when using UIDs. Using Gmail imap extensions,
    '+X-GM-LABELS', '\\Trash', deletes messages from all folders
    because it uses labels and folders interchangably.
    Thus, removing the inbox label in the yyyy-mm folder is the solution"""

    folder_list = list(set(folder_list))

    for folder in folder_list:
        response_code = mailserver.select(mailbox=('"' + folder + '"'), readonly=False)
        uids = mailserver.uid('SEARCH', 'ALL')
        logging.debug(uids)
        uid_list = uids[1][0].split()
        for uid in uid_list:
            response = mailserver.uid('FETCH', uid, '(RFC822)')
            logging.info(f'Removing Inbox label from {uid} in {folder} folder')
            response_code, response = mailserver.uid('STORE', uid, '-X-GM-LABELS', '\\Inbox')
            logging.debug(f'Response Code For Deleted Flag: {response_code}')
            logging.debug(f'Response For Deleted Flag     : {response[0].decode() if response[0] else None}')
        mailserver.close()


def main():
    """Sort messages from Inbox to yyyy-mm folders."""

    current_date = datetime.now()

    start_time = time.time()
    logging.info(f'Date: {current_date}')

    login(mailserver, user, password)

    sort_with_uid(folder_list)
    remove_inbox_flag(folder_list)

    logout(mailserver)

    stop_time = time.time()
    logging.info(f'Process time (secs): {round(stop_time - start_time, 2)}')


if __name__ == '__main__':
    main()
