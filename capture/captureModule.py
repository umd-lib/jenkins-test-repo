import os
import imaplib
import mailbox
import email
# from email.header import decode_header
# from email.message import EmailMessage
import time
from datetime import datetime
import sys
import logging



def login(mailserver, user, password):
    start = time.time()

    try:
        mailserver
    except imaplib.IMAP4.error:
        print('Failed to connect')
        mailserver = None
        sys.exit()
    print(f'Connection Object : {mailserver}')
    print(f'Time to Connect   : {time.time() - start:,.2f} Seconds')
    print('\nLogging into mailbox...')
    try:
        response_code, response = mailserver.login(user, password)
    except imaplib.IMAP4.error:
        print('Log in failed')
        response_code, response = None, None
        sys.exit()
    print(f'Response Code : {response_code}')
    print(f'Response      : {response[0].decode()}')

def logout(mailserver):
    print('\nLogging Out....')
    try:
        response_code, response = mailserver.logout()
    except imaplib.IMAP4.error:
        print('Log out failed')
        response_code, response = None, None
    print(f'Response Code : {response_code}')
    print(f'Response      : {response[0].decode()}')
