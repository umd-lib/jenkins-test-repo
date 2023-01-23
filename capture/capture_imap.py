"""IMAP connection handling."""

import imaplib
import time
import sys
import logging


class MailServerHandler:

    def connect(host, port):
        """Connect to mail server."""

        start = time.time()
        try:
            mailserver = imaplib.IMAP4_SSL(host, port)
            return mailserver
        except imaplib.IMAP4.error:
            logging.warn('Failed to connect')
            mailserver = None
            sys.exit(2)
        finally:
            logging.info(f'Connection Object : {mailserver}')
            logging.info(f'Time to Connect : {time.time() - start:,.2f} Seconds')

    def login(mailserver, user, password):
        """Log in to mail server."""

        logging.info('Logging into mailbox...')
        try:
            response_code, response = mailserver.login(user, password)
        except imaplib.IMAP4.error:
            logging.warn('Log in failed')
            response_code, response = None, None
            sys.exit(2)
        finally:
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
        finally:
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')
