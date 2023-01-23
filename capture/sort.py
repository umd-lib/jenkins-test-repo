"""Sort messages from Inbox to yyyy-mm folders."""

import email
import logging
import os
import time
from datetime import datetime

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


def sort_with_uid(mailserver):
=======
user = os.environ.get("user", "default")
password = os.environ.get("password", "default")

host = "imap.gmail.com"
port = imaplib.IMAP4_SSL_PORT

# Create a folder list in order to remove Inbox flags
folder_list = []
#mailserver = None


def sort_with_uid(mailserver, folder_list):
>>>>>>> 0f94475 (Refactored mailserver)
    """Copy messages to their respective yyyy-mm folders."""

    # Track the folders where we need to remove Inbox flags
    folder_list = []

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

        # Add folder to list in order to remove Inbox flags
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


def remove_inbox_flag(mailserver, folder_list):
    """Remove Inbox label.
    Normally, using uid('STORE', uid, '+FLAGS', '\\Deleted')
    would remove messages in the Inbox, however this does not work
    with Gmail when using UIDs. Using Gmail imap extensions,
    '+X-GM-LABELS', '\\Trash', deletes messages from all folders
    because it uses labels and folders interchangeably.
    Thus, removing the inbox label in the yyyy-mm folder is the solution"""

    folder_list = list(set(folder_list))

    for folder in folder_list:
        mailserver.select(mailbox=('"' + folder + '"'), readonly=False)
        uids = mailserver.uid('SEARCH', 'ALL')
        logging.debug(uids)
        uid_list = uids[1][0].split()
        for uid in uid_list:
            mailserver.uid('FETCH', uid, '(RFC822)')
            logging.info(f'Removing Inbox label from {uid} in {folder} folder')
            response_code, response = mailserver.uid('STORE', uid, '-X-GM-LABELS', '\\Inbox')
            logging.debug(f'Response Code For Deleted Flag: {response_code}')
            logging.debug(f'Response For Deleted Flag     : {response[0].decode() if response[0] else None}')
        mailserver.close()


def main():
    """Sort messages from Inbox to yyyy-mm folders."""

    start_time = time.time()
    logging.info(f'Date: {datetime.now()}')

<<<<<<< HEAD
    mailserver_handler = MailServerHandler()
    mailserver_handler.connect(host=host, port=port)
    mailserver_handler.login(user=user, password=password)

    folder_list = sort_with_uid(mailserver_handler.mailserver)
    remove_inbox_flag(mailserver_handler.mailserver, folder_list)

    mailserver_handler.logout()
=======
    mailserver = MailServerHandler.connect(host=host, port=port)
    MailServerHandler.login(mailserver, user=user, password=password)

    sort_with_uid(mailserver, folder_list)
    remove_inbox_flag(mailserver, folder_list)

    MailServerHandler.logout(mailserver)
>>>>>>> 0f94475 (Refactored mailserver)

    stop_time = time.time()
    logging.info(f'Process time (secs): {round(stop_time - start_time, 2)}')


if __name__ == '__main__':
    main()
