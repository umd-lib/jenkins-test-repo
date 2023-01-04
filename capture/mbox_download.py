import os
import time
from datetime import datetime
from dotenv import load_dotenv

import logging
from captureModule import Capture

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    load_dotenv()
    user = os.environ.get("user", "default")
    password = os.environ.get("password", "default")

    current_date = datetime.now()
    month, year = (current_date.month-1, current_date.year) if current_date.month != 1 else (12, current_date.year-1)
    previous_month = str(current_date.replace(month=month, year=year))[0:7]
    mbox_file_path = os.path.join('./', previous_month+'.mbox')

    start_time = time.time()
    print('Date              :', current_date)
    Capture.login(user, password)
    Capture.check(previous_month)
    Capture.check_for_mbox_file(previous_month)

    if os.path.exists(mbox_file_path):
        os.remove(mbox_file_path)
    else:
        pass

    Capture.download_messages(previous_month)

    Capture.compare_message_counts()

    if not os.path.exists('data_mbox'):
        os.mkdir('data_mbox')
    else:
        pass

    if os.path.exists(mbox_file_path) and not os.path.exists('data_mbox/' + previous_month + '.mbox'):
        os.replace(mbox_file_path, 'data_mbox/' + previous_month + '.mbox')
    else:
        os.remove(mbox_file_path)


    Capture.logout()

    stop_time = time.time()
    print('\nProcess time (secs):', round(stop_time - start_time, 2))


if __name__ == '__main__':
    main()
