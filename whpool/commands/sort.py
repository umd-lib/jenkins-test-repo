"""Sort messages from Inbox to yyyy-mm folders."""

import email
import logging
import os
import time
from datetime import datetime

import click
from dotenv import load_dotenv  # pip install python-dotenv

from whpool.core.capture_imap import MailServerHandler


logger = logging.getLogger(__name__)

# get configs
load_dotenv()
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')


def sort_with_uid(mailserver):
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


@click.command(help='Sorts messages by yyyy-mm to mailbox folders, '
                    'creating mailbox folders in yyyy-mm format if it does not exist.')
@click.option(
    '-v', '--verbose', 'verbosity',
    default=1,
    help='''\b
            Set verbosity logging output level.
            0 = Warning
            1 = Info (default)
            2 = Debug'''
)
def main(verbosity: int) -> None:
    """Sort messages from Inbox to yyyy-mm folders."""

    # Setup logging
    if verbosity == 0:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
    elif verbosity == 1:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    elif verbosity == 2:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    logger.debug(f'{verbosity=}')

    start_time = time.time()
    logging.info(f'Date: {datetime.now()}')

    mailserver_handler = MailServerHandler()
    mailserver_handler.connect(host=host, port=port)
    mailserver_handler.login(user=user, password=password)

    folder_list = sort_with_uid(mailserver_handler.mailserver)
    remove_inbox_flag(mailserver_handler.mailserver, folder_list)

    mailserver_handler.logout()

    stop_time = time.time()
    logging.info(f'Process time (secs): {round(stop_time - start_time, 2)}')


if __name__ == '__main__':
    main()
