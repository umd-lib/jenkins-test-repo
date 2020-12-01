#!/bin/bash

# Sync the contents of the service account INBOX to local INBOX.mbox file
# pip install imapbackup3
imapbackup3 \
  --folders INBOX \
  --ssl \
  --server imap.gmail.com \
  --port 993 \
  --user 'lib-whpoolreports-service@umd.edu' \
  --password $IMAPBACKUP_PASSWORD \
  --mailbox mbox
