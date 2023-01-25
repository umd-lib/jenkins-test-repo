"""IMAP connection handling."""

import imaplib
import time
import sys
import logging


class MailServerHandler:
    def __init__(self):
        self.mailserver = None

    def connect(self, host, port):
        """Connect to mail server."""

        start = time.time()
        try:
            self.mailserver = imaplib.IMAP4_SSL(host, port)
        except imaplib.IMAP4.error:
            logging.warning('Failed to connect')
            sys.exit(2)
        else:
            logging.info(f'Connection Object : {self.mailserver}')
            logging.info(f'Time to Connect : {time.time() - start:,.2f} Seconds')

    def login(self, user, password):
        """Log in to mail server."""

        logging.info('Logging into mailbox...')
        try:
            response_code, response = self.mailserver.login(user, password)
        except imaplib.IMAP4.error:
            logging.warning('Log in failed')
            sys.exit(2)
        else:
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')

    def logout(self):
        """Log out of mail server."""

        logging.info('Logging Out...')
        try:
            response_code, response = self.mailserver.logout()
        except imaplib.IMAP4.error:
            logging.warning('Log out failed')
        else:
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')
