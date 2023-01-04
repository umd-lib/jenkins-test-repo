# Capture

An automated process to capture email messages.

## sort.py

Automate the sorting process of messages to mailbox folders that does the following:

- Creates mailbox folders in yyyy-mm format if it does not exist
- Moves emails to the appropriate mailbox folder according to date
- Prints a log, that includes:
  - date/time of execution
  - name(s) of mailbox folder(s) that are created
- Runs once a day in order to keep imap credentials alive.

## mbox_download.py

Automate the fetching of messages from mailbox folders that does the following:

- Checks that there are no previous month’s messages in the inbox
- Check if mbox file already exists for one month prior. If it exists, then end.
- Fetches messages from the previous month’s mailbox folder
- Saves messages to an mbox file
- Compares the mbox file messages to the mailbox folder messages
- Prints a log, that includes:
  - date/time of execution
  - name of mailbox folder
  - total number of messages fetched
  - total number of messages in mailbox folder
- Runs at least once a month
