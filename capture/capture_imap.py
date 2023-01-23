"""IMAP connection handling."""

import imaplib
import time
import sys
import logging


class MailServerHandler:
<<<<<<< HEAD
    def __init__(self):
        self.mailserver = None

    def connect(self, host, port):
=======

    def connect(host, port):
>>>>>>> 0f94475 (Refactored mailserver)
        """Connect to mail server."""

        start = time.time()
        try:
<<<<<<< HEAD
            self.mailserver = imaplib.IMAP4_SSL(host, port)
        except imaplib.IMAP4.error:
            logging.warning('Failed to connect')
            sys.exit(2)
        else:
            logging.info(f'Connection Object : {self.mailserver}')
            logging.info(f'Time to Connect : {time.time() - start:,.2f} Seconds')

    def login(self, user, password):
=======
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
>>>>>>> 0f94475 (Refactored mailserver)
        """Log in to mail server."""

        logging.info('Logging into mailbox...')
        try:
<<<<<<< HEAD
            response_code, response = self.mailserver.login(user, password)
        except imaplib.IMAP4.error:
            logging.warning('Log in failed')
            sys.exit(2)
        else:
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')

    def logout(self):
=======
            response_code, response = mailserver.login(user, password)
        except imaplib.IMAP4.error:
            logging.warn('Log in failed')
            response_code, response = None, None
            sys.exit(2)
        finally:
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')

    def logout(mailserver):
>>>>>>> 0f94475 (Refactored mailserver)
        """Log out of mail server."""

        logging.info('Logging Out...')
        try:
<<<<<<< HEAD
            response_code, response = self.mailserver.logout()
        except imaplib.IMAP4.error:
            logging.warning('Log out failed')
        else:
=======
            response_code, response = mailserver.logout()
        except imaplib.IMAP4.error:
            logging.warn('Log out failed')
            response_code, response = None, None
        finally:
>>>>>>> 0f94475 (Refactored mailserver)
            logging.info(f'Response Code : {response_code}')
            logging.info(f'Response : {response[0].decode()}')
