#!/bin/bash

# Sync the contents of the service account folder(s) as provided in a comma
# separated list
# pip install imapbackup3
imapbackup3 \
  --folders "$1" \
  --ssl \
  --server imap.gmail.com \
  --port 993 \
  --user 'lib-whpoolreports-service@umd.edu' \
  --password $IMAPBACKUP_PASSWORD \
  --mailbox mbox
