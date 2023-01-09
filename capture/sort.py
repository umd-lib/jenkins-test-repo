import os
import time
import imaplib
import email
from datetime import datetime
from dotenv import load_dotenv

from captureModule import login, logout

mailserver = imaplib.IMAP4_SSL(host="imap.gmail.com", port=imaplib.IMAP4_SSL_PORT)

def sort_with_uid(mailserver):

    resp_code, messages = mailserver.select(mailbox='INBOX', readonly=False)
    uids = mailserver.uid('SEARCH', 'ALL')
    print(uids)
    uid_list = uids[1][0].split()
    # print(uid_list)
    for uid in uid_list:
        resp, mail_data = mailserver.uid('FETCH', uid, '(RFC822)')
        message = email.message_from_bytes(mail_data[0][1])
        # print(uid, message['date'])
        message_date = (message.get("Date"))[:-6]
        date_in_utc_iso = datetime.strptime(message_date, '%a, %d %b %Y %H:%M:%S').isoformat() + 'Z'
        message_year_month = str(date_in_utc_iso[:7])
        # print(message_year_month)
        folder_exists = (mailserver.list('"' + message_year_month + '"'))
        # print(folder_exists)
        # print(folder_exists == ('OK', [None]))
        if folder_exists != ('OK', [None]):
            print('The folder', message_year_month, 'exists.')
        else:
            mailserver.create(mailbox=message_year_month)
            mailserver.subscribe(mailbox=message_year_month)
            print('The folder', message_year_month, 'does not exist. Creating folder.')
        print('Copying', uid, 'to', message_year_month, 'folder')
        mailserver.uid('COPY', uid, message_year_month)
    mailserver.close()

def remove_inbox_label(mailserver):
    # mailserver.uid('STORE', uid, '+FLAGS', '\\Deleted'))
    # does not work with gmail
    # mailserver.uid('STORE', uid, '+X-GM-LABELS', '\\Trash')
    # deletes messages from all folders
    # because gmail uses labels and folders interchangably
    # removing the inbox label with a select, fetch, store in the yyyy-mm folder is the solution
    # Hard Coded Value. Change after function refactoring.
    mailbox_month = ('"2023-01"')
    resp_code, messages = mailserver.select(mailbox=mailbox_month, readonly=False)
    uids = mailserver.uid('SEARCH', 'ALL')
    print(uids)
    uid_list = uids[1][0].split()
    # print(uid_list)
    for uid in uid_list:
        resp, mail_data = mailserver.uid('FETCH', uid, '(RFC822)')
        print('Removing Inbox label from', uid, 'in', mailbox_month, 'folder')
        resp_code, response = mailserver.uid('STORE', uid, '-X-GM-LABELS', '\\Inbox')  # Setting Remove Label Flag
        print(f'Response Code For Deleted Flag: {resp_code}')
        print(f'Response For Deleted Flag     : {response[0].decode() if response[0] else None}\n')
    mailserver.close()

def main():
    # store user and password in another file
    load_dotenv()
    user = os.environ.get("user", "default")
    password = os.environ.get("password", "default")

    current_date = datetime.now()

    start_time = time.time()
    print('Date              :', current_date)

    login(mailserver, user, password)

    sort_with_uid(mailserver)
    remove_inbox_label(mailserver)

    logout(mailserver)

    stop_time = time.time()
    print('\nProcess time (secs):', round(stop_time - start_time, 2))


if __name__ == '__main__':
    main()
