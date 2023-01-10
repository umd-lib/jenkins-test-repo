"""IMAP connection handling."""

import imaplib
import time
import sys
import logging


def login(mailserver, user, password):
    """Connect and log in to mail server."""

    start = time.time()

    try:
        mailserver
    except imaplib.IMAP4.error:
        logging.warn('Failed to connect')
        mailserver = None
        sys.exit()
    logging.info(f'Connection Object : {mailserver}')
    logging.info(f'Time to Connect : {time.time() - start:,.2f} Seconds')
    logging.info('Logging into mailbox...')
    try:
        response_code, response = mailserver.login(user, password)
    except imaplib.IMAP4.error:
        logging.warn('Log in failed')
        response_code, response = None, None
        sys.exit()
    logging.info(f'Response Code : {response_code}')
    logging.info(f'Response : {response[0].decode()}')


def logout(mailserver):
    """Log out of mail server."""

    logging.info('Logging Out...')
    try:
        response_code, response = mailserver.logout()
    except imaplib.IMAP4.error:
        logging.warn('Log out failed')
        response_code, response = None, None
    logging.info(f'Response Code : {response_code}')
    logging.info(f'Response : {response[0].decode()}')
