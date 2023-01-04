import os
import time
from datetime import datetime
from dotenv import load_dotenv

from captureModule import Capture

def main():
    # store user and password in another file
    load_dotenv()
    user = os.environ.get("user", "default")
    password = os.environ.get("password", "default")

    current_date = datetime.now()

    start_time = time.time()
    print('Date              :', current_date)

    Capture.login(user, password)
    Capture.sort_messages()
    Capture.logout()

    stop_time = time.time()
    print('\nProcess time (secs):', round(stop_time - start_time, 2))


if __name__ == '__main__':
    main()
