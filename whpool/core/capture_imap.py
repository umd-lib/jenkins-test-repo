"""IMAP connection handling."""

import imaplib
import time
import sys
import logging

logger = logging.getLogger(__name__)


class MailServerHandler:
    def __init__(self):
        self.mailserver = None

    def connect(self, host, port):
        """Connect to mail server."""

        start = time.time()
        try:
            self.mailserver = imaplib.IMAP4_SSL(host, port)
        except imaplib.IMAP4.error:
            logger.warning('Failed to connect')
            sys.exit(2)
        else:
            logger.info(f'Connection Object : {self.mailserver}')
            logger.info(f'Time to Connect : {time.time() - start:,.2f} Seconds')

    def login(self, user, password):
        """Log in to mail server."""

        logger.info('Logging into mailbox...')
        try:
            response_code, response = self.mailserver.login(user, password)
        except imaplib.IMAP4.error:
            logger.warning('Log in failed')
            sys.exit(2)
        else:
            logger.info(f'Response Code : {response_code}')
            logger.info(f'Response : {response[0].decode()}')

    def logout(self):
        """Log out of mail server."""

        logger.info('Logging Out...')
        try:
            response_code, response = self.mailserver.logout()
        except imaplib.IMAP4.error:
            logger.warning('Log out failed')
        else:
            logger.info(f'Response Code : {response_code}')
            logger.info(f'Response : {response[0].decode()}')
